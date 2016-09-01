
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

import logging
import zipfile

import os
from django.conf import settings

from footprint.main.database.import_data import ImportData
from footprint.main.models.database.information_schema import InformationSchema
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.publishing.data_import_publishing import create_and_populate_relations, add_primary_key_if_needed
from footprint.main.publishing.import_processor import ImportProcessor
from footprint.main.utils.utils import file_url_to_path, apply_regexes_to_file

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'


class ZippedSqlFileProcessor(ImportProcessor):
    """
        Imports the contents of a zipped SQL file that creates one or more postresql feature tables
    """

    def __init__(self, **kwargs):
        self.srid = kwargs['db_entity'].srid # Required
        super(ZippedSqlFileProcessor, self).__init__()

    def importer(self, config_entity, db_entity, **kwargs):
        """
            Replaces the normal ImportProcessor importer with one to import a sql from disk
        """
        if InformationSchema.objects.table_exists(db_entity.schema, db_entity.table):
            # The table already exists. Skip the import an log a warning
            logger.warn("The target table for the feature table import already exists. Skipping table import.")
        else:
            # We don't store the upload_id alone, so pull it off the url
            upload_id = db_entity.url.replace('file:///tmp/', '').replace('.sql.zip', '')
            # Unpack the zipfile and return the path the sql file was placed at
            if db_entity.url.startswith('file://'):
                file_path = db_entity.url[len('file://'):]

            logger.warn(file_path)
            path = unpack_zipfile(file_path, upload_id)
            # The file is always the name of the table defined therein
            table_name = path.split('/')[-1].split('.')[0].lower()
            db_entity.url = 'file://%s' % path
            # Update the db_entity.url from the zip file url to the file_path
            # This lets ImportData find it.
            logger.info("Url of DbEntity is %s" % db_entity.url)
            db_entity.save()

            # Perform some sed updates to get the sql file ready for import
            regex_substitutions = []
            sql_file_path = file_url_to_path(db_entity.url)

            # Add IF EXISTS to the drop table to prevent an error if IF EXISTS doesn't exist yet
            regex_substitutions.append((r'DROP TABLE (?!IF EXISTS)', r'DROP TABLE IF EXISTS'))

            # TODO temp, fix an AC bug. It seems that using a capitalized column is problematic (?)
            # The suggested solution is to double quote it, but quotes cause other problems, so we simply lowercase
            regex_substitutions.append((r' OGC_FID ', ' ogc_fid ', (4, 4)))  # only line 4
            regex_substitutions.append((r'PRIMARY KEY \(ogc_fid\)', 'PRIMARY KEY (ogc_fid)', (4, 4)))  # only line 4
            # TODO end temp fix

            # Update the index name to include the schema. This format matches that created for preconfigured feature
            # tables (see import_data.py)
            spatial_index_name = '{schema}_{key}_geom_idx'.format(schema=db_entity.schema, key=db_entity.key)
            regex_substitutions.append((r'CREATE INDEX ".*" ON', 'CREATE INDEX "%s" ON' % spatial_index_name, (6, 6)))  # only line 6 6

            # Remove the reference to the geometry_columns, since we use a materialized view
            regex_substitutions.append((r'^DELETE FROM geometry_columns', '--DELETE FROM geometry_columns', (2, 2)))

            # Update the sql to have a unique table name which matches the DbEntity key
            # Also change public to our import schema to keep it from causing trouble in the public schema
            # Otherwise we run into all kinds of trouble trying to get the SQL into the system
            regex_substitutions.append((r'"public"."%s"' % table_name, '"import"."%s"' % db_entity.key))

            regex_substitutions.append((r"'%s'" % table_name, "'%s'" % db_entity.key, (2, 5)))

            regex_substitutions.append((r'"%s_pk"' % table_name, '"%s_pk"' % db_entity.key, (4, 4)))

            # Update public to the import schema
            regex_substitutions.append((r"AddGeometryColumn\('public'", "AddGeometryColumn('%s'" % settings.IMPORT_SCHEMA, (5, 5)))

            regex_substitutions.append((r'"%s_wkb_geometry_geom_idx"' % table_name, '"%s_wkb_geometry_geom_idx"' % db_entity.key, (6, 6)))

            for command in regex_substitutions:
                logger.info("Applying the following substitution %s" % ', '.join(command[0:2]))
            apply_regexes_to_file(sql_file_path, regex_substitutions)

            ImportData(config_entity=config_entity, db_entity_key=db_entity.key).run()

        # Add our normal primary key in the id column if negit eded
        add_primary_key_if_needed(db_entity)

        feature_class_creator = FeatureClassCreator(config_entity, db_entity)
        # Inspect the imported table to create the feature_class_configuration
        feature_class_configuration = feature_class_creator.feature_class_configuration_from_introspection()

        # Merge the created feature_class_configuration with the on already defined for the db_entity
        feature_class_creator.update_db_entity(feature_class_configuration)
        logger.info("Finished import for DbEntity: %s, feature_class_configuration: %s" % (db_entity, db_entity.feature_class_configuration))

        # Create association classes and tables and populate them with data
        create_and_populate_relations(config_entity, feature_class_creator.db_entity)


def unpack_zipfile(zip_archive, upload_id):
    """
        Unzips the given zipfile with only one .sql file expected therein
        to the media directory under a directory
        named after the given upload_id.
    :param zip_archive:
    :param upload_id:
    :return: The full path to the extracted file
    """

    archive = zipfile.ZipFile(zip_archive, 'r')
    archive_contents = archive.namelist()

    # We only expect one .sql file in the zip file
    archive_file = archive_contents[0]

    # Extract the file to a unique directory based on the upload id
    upload_media_path = os.path.join(settings.MEDIA_ROOT, 'uploads', upload_id)
    logger.debug("Extracting zipfile to {0}".format(upload_media_path))
    archive.extractall(path=upload_media_path)

    # Calculate the current absolute path of the archive file
    imported_path = os.path.join(upload_media_path, archive_file)
    return imported_path
