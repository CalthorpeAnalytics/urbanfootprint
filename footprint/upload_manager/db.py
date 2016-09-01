
# UrbanFootprint v1.5
# Copyright (C) 2016 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

import os
import re
import copy
import logging
import tempfile
import subprocess
from zipfile import ZipFile

from inflection import titleize

from django.db import connection
from django.conf import settings
from django.utils import timezone
from django.template.defaultfilters import slugify

from footprint.main.models import DbEntity
from footprint.main.models.category import Category
from footprint.main.models.keys.db_entity_category_key import DbEntityCategoryKey
from footprint.upload_manager.models import UploadTask, UploadDatasetTask

from footprint.main.utils.utils import increment_key
from footprint.utils.websockets import send_message_to_client
from footprint.upload_manager.utils import create_task as create_upload_task


logger = logging.getLogger(__name__)


def get_db_entity_params(layer_name):
    """
    For DbEntity creation we need a key and name. The key is a 'slugified'
    version of the name, and name is extracted from the layer.
    """

    db_entity_name = titleize(layer_name)

    # ensure we have unique names if the layer has been uploaded before
    while DbEntity.objects.filter(name=db_entity_name).count() > 0:
        db_entity_name = increment_key(db_entity_name)

    db_entity_key = slugify(db_entity_name).replace('-', '_')

    return db_entity_key, db_entity_name


def create_db_entity(pg_dump_fpath, db_entity_key, db_entity_name, table_name, layer_count, user, config_entity, **kwargs):
    """
    Create a DbEntity and all associated layers, etc. The majority of the
    processing occurs in the post-save methods on DbEntity objects, this method
    simply gets objects in the necessary state to trigger it.
    """

    logger.debug("Creating DbEntity %s with pg_dump file %s", db_entity_key, pg_dump_fpath)

    if 'upload_task' in kwargs:
        upload_task = kwargs['upload_task']
    else:
        # we're calling this from the command line
        # for testing purposes
        upload_task = create_upload_task(
            user,
            pg_dump_fpath,
            config_entity,
            extra_data_dict={'X-Progress-ID': 'unused'}
        )

    # later post-save processes expect a zipped sql file
    zipped_sql_fpath = "{}.zip".format(pg_dump_fpath)
    with ZipFile(zipped_sql_fpath, 'w') as zipped_sql:
        zipped_sql.write(pg_dump_fpath)

    # the UploadDataset represents the processing of a single file
    upload_dataset_task = UploadDatasetTask.objects.create(
        upload_task=upload_task,
        dataset_id=-1,
        file_path=zipped_sql_fpath,
        filename=db_entity_key,
        progress=upload_task.progress,
        status=upload_task.status,
        extra=upload_task.extra
    )

    # the schema metadata, has information necessary for Django to create
    # new data models based on the upload. The DbEntity post-save
    # logic uses this.
    schema_metadata = get_schema_metadata(pg_dump_fpath, table_name)
    upload_dataset_task.metadata = schema_metadata
    logger.debug("Saving DbEntity %s and inititialzing post-save processing.", db_entity_key)
    upload_dataset_task.save()

    db_entity = DbEntity(
        creator=user,
        updater=user,
        name=db_entity_name,
        key=db_entity_key,
        url='file://{}'.format(zipped_sql_fpath),
        setup_percent_complete=0,
        schema=config_entity.schema()
    )

    # setting `_config_entity` and then calling `save()` triggers
    # the post-save processing flow, which, among other things,
    # loads the data into the database, creates layers and runs
    # required updates to other model objects to be aware of this
    # layer.
    db_entity._config_entity = config_entity
    db_entity.save()

    db_entity.categories.add(
        Category.objects.get(
            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
            value=DbEntityCategoryKey.REFERENCE
        )
    )

    upload_dataset_task.progress = 100
    upload_dataset_task.status = UploadDatasetTask.SUCCESS
    upload_dataset_task.ended_on = timezone.now()
    upload_dataset_task.save()
    upload_dataset_task.send_progress()

    finished_dataset_count = UploadDatasetTask.objects.filter(upload_task=upload_task, status=UploadDatasetTask.SUCCESS).count()
    if finished_dataset_count == layer_count:
        upload_task.progress = 100
        upload_task.status = UploadTask.SUCCESS
        upload_task.ended_on = timezone.now()
        upload_task.save()
        upload_task.send_progress()

    message_kwargs = dict(
        event="doCreateDbEntity",
        id=db_entity.id,
        name=db_entity_name,
        key=db_entity_key,
        config_entity=config_entity.id,
        file_dataset=upload_dataset_task.id
    )

    # send websockets `doCreateDbEntity` signal to the browser
    send_message_to_client(
        user.id,
        message_kwargs
    )


def load_to_database(pg_dump_fpath, table_name, schema_only=False):
    """
    Run the sql script to load the transformed data into Postgres.
    Optionally, only create the table and load no data (used by
    the process handling DbEntity creation can inspect the table
    schema, information needed to create a data model for Django
    to represent the table).
    """

    # the line in the sql file to delete geometry columns doesn't
    # work with our established materialized views, so remove it
    # TODO: probably better to do this in chunks for large files
    with open(pg_dump_fpath, 'r') as f:
        contents = f.read()
        contents = re.sub(
            r'DELETE FROM geometry_columns WHERE f_table_name = (.*) AND f_table_schema = (.*);',
            '',
            contents
        )

        if schema_only:
            """
            If schema_only, then we don't need to load the data from the sql script
            The pg_dump format looks like, e.g.:

            ...
            CREATE TABLE "myschema"."mytable" ( MY_PK, CONSTRAINT "my_table_pk" PRIMARY KEY (MY_PK) );
            ALTER TABLE "myschema"."mytable" ADD COLUMN "my_column" VARCHAR;
            COPY "myschema"."mytable" ("my_column") FROM STDIN;
            row_1
            ...
            row_n
            \.
            COMMIT;

            where '\.' signals the end of STDIN, so all data loading content to be removed
            is bounded by 'COPY' and '\.'
            """
            contents = re.sub(
                r'COPY(?!\\\.).*\\\.',
                '',
                contents,
                flags=re.DOTALL  # DOTALL so that .* includes newlines
            )

    # write the script contents back to disk with the substitution
    with open(pg_dump_fpath, 'w') as f:
        f.write(contents)

    with tempfile.NamedTemporaryFile(delete=False) as pgpass:
        pgpass.write(
            "{}:{}:{}:{}:{}\n".format(
                settings.DATABASE_HOST,
                settings.DATABASE_PORT,
                settings.DATABASE_NAME,
                settings.DATABASE_USERNAME,
                settings.DATABASE_PASSWORD
            )
        )

    env = dict(copy.deepcopy(os.environ))
    env['PGPASSFILE'] = pgpass.name

    # create the import schema if needed
    create_schema_cmd = [
        "psql",
        "-d", settings.DATABASE_NAME,
        "-U", settings.DATABASE_USERNAME,
        "-h", settings.DATABASE_HOST,
        "-p", settings.DATABASE_PORT,
        "-c", "CREATE SCHEMA IF NOT EXISTS {schema}; GRANT ALL ON SCHEMA {schema} TO public;".format(schema=settings.IMPORT_SCHEMA)
    ]

    subprocess.check_call(create_schema_cmd, env=env)

    # load the data into postgres
    load_data_cmd = [
        "psql",
        "-d", settings.DATABASE_NAME,
        "-U", settings.DATABASE_USERNAME,
        "-h", settings.DATABASE_HOST,
        "-p", settings.DATABASE_PORT,
        "-f", pg_dump_fpath
    ]

    subprocess.check_call(load_data_cmd, env=env)

    # clean up and remove temp pgpass file
    os.remove(pgpass.name)

    # coerce the geometry columns into 2 dimensions and 4326 projection
    cursor = connection.cursor()
    try:
        cursor.execute('ALTER TABLE import.{} ALTER COLUMN wkb_geometry '
                       'TYPE Geometry(geometry, 4326) '
                       'USING ST_Transform(ST_Force_2d(wkb_geometry), 4326);'.format(table_name))
    finally:
        cursor.close()


def get_schema_metadata(pg_dump_fpath, table_name):
    """
    Schema metadata is needed in order to create a Django data model
    to represent the eventual table. The methods `feature_class_configuration_from_metadata`
    and `resolve_field` in feature_class_creator.py are the consumers of
    this data and expect a list of dictionaries, where each dictionary
    represents key-value pairs for the name, type and default value of
    table column, e.g.:

    [
        {
            'name': 'field_1',
            'type': 'integer',
            'default': None
        },
        {
            ...
        }
    ]

    Additionally, for dynamic models based on uploaded datasets, the primary key
    assigned during conversion in ogr2ogr is removed by
    `feature_class_configuration_from_metadata`, so we simply filter
    it out now during a query on the `information_schema.columns` table.

    """

    load_to_database(pg_dump_fpath, table_name, schema_only=True)

    query = """
        SELECT
            column_name,
            CASE
                WHEN data_type = 'USER-DEFINED'
                    THEN udt_name
                ELSE data_type
            END,
            column_default
        FROM
            information_schema.columns
        WHERE
            table_name = %(table_name)s
            AND table_schema = %(schema)s
        AND column_name not in (
            SELECT
                a.attname
            FROM
                pg_index i
            JOIN
                pg_attribute a
            ON
                a.attrelid = i.indrelid
                AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = (%(schema)s || '.' || %(table_name)s)::regclass
            AND i.indisprimary
        )
    """

    cursor = connection.cursor()
    try:
        cursor.execute(query, {"schema": settings.IMPORT_SCHEMA, "table_name": table_name})
        rows = cursor.fetchall()
    finally:
        cursor.close()

    schema = []

    for row in rows:
        schema.append({
            "name": row[0],
            "type": row[1],
            "default": row[2]
        })

    return schema


if __name__ == "__main__":
    """
    A simple CLI interaction for rapid functional testing. Should be used like:

        $ DJANGO_SETTINGS_MODULE=footprint.settings_dev python footprint/upload_manager/geo.py dpss_offices.zip

    to simply load data into Postgres, or:

        $ DJANGO_SETTINGS_MODULE=footprint.settings_dev python footprint/upload_manager/geo.py dpss_offices.zip 1

    to create DbEntity objects.

    """
    # TODO: once this functionality stabilizes, either remove CLI
    # functionality or move it to a proper management command

    import sys
    from django.contrib.auth import get_user_model
    from footprint.upload_manager.geo import process_file
    from footprint.main.models.config.config_entity import ConfigEntity

    process_file(
        sys.argv[1],
        user=get_user_model().objects.get(email='admin@urbanfootprint.net'),
        should_create_db_entity=len(sys.argv) > 2,
        config_entity=ConfigEntity.objects.get(key='nhm')
    )
