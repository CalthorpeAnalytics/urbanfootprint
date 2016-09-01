
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

from django.contrib.gis.db.models import GeometryField
from footprint.main.utils.utils import parse_schema_and_table

__author__ = 'calthorpe_analytics'

import keyword
from django.db import connections
# KEEP all below for eval
from django.contrib.gis.db import models

class InlineInspectDb():
    """
        Inline version of Django management tool inspectdb. This is a copy of that logic retrofited
        to produce the fields of a class based on introspection of a database table
    """

    requires_model_validation = False
    db_module = 'django.db'

    @classmethod
    def get_table_description(self, cursor, table, schema, connection):
        """
            Returns a description of the table, with the DB-API cursor.description interface."
            As cursor.description does not return reliably the nullable property,
            we have to query the information_schema (#7783)
        """
        cursor.execute("""
            SELECT column_name, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = %s""", [table, schema])
        null_map = dict(cursor.fetchall())
        cursor.execute("SELECT * FROM %s.%s LIMIT 1" %
                       (connection.ops.quote_name(schema), connection.ops.quote_name(table)))
        return [tuple([item for item in line[:6]] + [null_map[line[0]]==u'YES'])
                for line in cursor.description]

    @classmethod
    def get_fields(cls, table_name):
        """
            Modifies the original handle_inspection to instead get all the fields of the table described by the db_entity
        :param db_entity:
        :return: A dict keyed by field named and valued by models.Field or variant instance
        """

        connection = connections['default']

        table2model = lambda table_name: table_name.title().replace('_', '').replace(' ', '').replace('-', '')

        cursor = connection.cursor()

        try:
            relations = connection.introspection.get_relations(cursor, table_name)
        except NotImplementedError:
            relations = {}
        try:
            indexes = connection.introspection.get_indexes(cursor, table_name)
        except NotImplementedError:
            indexes = {}

        schema, table = parse_schema_and_table(table_name)
        # Fill this dict with field definitions
        fields = {}
        for i, row in enumerate(cls.get_table_description(cursor, table, schema, connection)):
            column_name = row[0]
            att_name = column_name.lower()
            comment_notes = [] # Holds Field notes, to be displayed in a Python comment.
            extra_params = {}  # Holds Field parameters such as 'db_column'.

            # If the column name can't be used verbatim as a Python
            # attribute, set the "db_column" for this Field.
            if ' ' in att_name or '-' in att_name or keyword.iskeyword(att_name) or column_name != att_name:
                extra_params['db_column'] = column_name

            # Add primary_key and unique, if necessary.
            if column_name in indexes:
                if indexes[column_name]['primary_key']:
                    extra_params['primary_key'] = True
                elif indexes[column_name]['unique']:
                    extra_params['unique'] = True

            # Modify the field name to make it Python-compatible.
            if ' ' in att_name:
                att_name = att_name.replace(' ', '_')
                comment_notes.append('Field renamed to remove spaces.')

            if '-' in att_name:
                att_name = att_name.replace('-', '_')
                comment_notes.append('Field renamed to remove dashes.')

            if column_name != att_name:
                comment_notes.append('Field name made lowercase.')

            if i in relations:
                rel_to = relations[i][1] == table_name and "'cls'" or table2model(relations[i][1])
                field_type = 'ForeignKey(%s' % rel_to
                if att_name.endswith('_id'):
                    att_name = att_name[:-3]
                else:
                    extra_params['db_column'] = column_name
            else:
                # Calling `get_field_type` to get the field type string and any
                # additional paramters and notes.
                field_type, field_params, field_notes = cls.get_field_type(connection, table_name, row)
                extra_params.update(field_params)
                comment_notes.extend(field_notes)

                field_type += '('

            if keyword.iskeyword(att_name):
                att_name += '_field'
                comment_notes.append('Field renamed because it was a Python reserved word.')

            if att_name[0].isdigit():
                att_name = 'number_%s' % att_name
                extra_params['db_column'] = unicode(column_name)
                comment_notes.append("Field renamed because it wasn't a "
                                     "valid Python identifier.")

            # Don't output 'id = meta.AutoField(primary_key=True)', because
            # that's assumed if it doesn't exist.
            if att_name == 'id' and field_type == 'AutoField(' and extra_params == {'primary_key': True}:
                continue

            # Add 'null' and 'blank', if the 'null_ok' flag was present in the
            # table description.
            if row[6]: # If it's NULL...
                extra_params['blank'] = True
                # Don't know why these are here, commenting out
                #if not field_type in ('TextField(', 'CharField('):
                extra_params['null'] = True

            field_desc = 'models.%s' % field_type
            if extra_params:
                if not field_desc.endswith('('):
                    field_desc += ', '
                field_desc += ', '.join(['%s=%r' % (k, v) for k, v in extra_params.items()])
            field_desc += ')'
            if comment_notes:
                field_desc += ' # ' + ' '.join(comment_notes)
            # Set the dict key/value to the field name and the evaluated field description
            fields[att_name] = eval(field_desc)
            fields[att_name].name = att_name
        return fields

    @classmethod
    def get_field_type(cls, connection, table_name, row):
        """
        Given the database connection, the table name, and the cursor row
        description, this routine will return the given field type name, as
        well as any additional keyword parameters and notes for the field.
        """
        field_params = {}
        field_notes = []

        try:
            field_type = connection.introspection.get_field_type(row[1], row)
        except KeyError:
            field_type = 'TextField'
            field_notes.append('This field type is a guess.')

        # This is a hook for DATA_TYPES_REVERSE to return a tuple of
        # (field_type, field_params_dict).
        if type(field_type) is tuple:
            field_type, new_params = field_type
            field_params.update(new_params)

        # Add max_length for all CharFields.
        if field_type == 'CharField' and row[3]:
            field_params['max_length'] = row[3]

        if field_type == 'DecimalField':
            # TODO These are reading the wrong values sometimes, returning 65535 for both.
            # So minimize them
            field_params['max_digits'] = min(row[4], 100)
            field_params['decimal_places'] = min(row[5], 20)

        return field_type, field_params, field_notes
