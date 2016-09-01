
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

from optparse import make_option
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import connection
from footprint.main.management.commands.footprint_init import create_scenario_clone
from footprint.main.models.config.scenario import Scenario
import logging
from footprint.main.models.database.information_schema import SmartDatabaseIntrospection
from footprint.main.utils.uf_toolbox import table_exists

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'


class Command(BaseCommand):
    """
        This command clears all layer_selections
    """
    option_list = BaseCommand.option_list + (
        make_option('--from', default='', help='schema.table for import scenario data'),
        make_option('--to', default='', help='String matching a key of or more Scenario to run'),
        make_option('--name', default=None, help='The name for the new scenario, if not specifying a destination scenario'),
        # make_option('--type', default='table', help='The type of source data'),
        make_option('--join_on', default='source_id', help='The id field from the source table to use in the join'),
        make_option('--join_to', default='source_id', help='The id field from the destination table to use in the join'),
        make_option('--full', default=True, help='Use all columns from the source table - must match schema exactly')
    )

    def handle(self, *args, **options):
        full_source_table = options.get('from')
        source = full_source_table.split('.')
        assert source, "you must provide a source for the import scenario data"
        if len(source) == 1:
            source_table = source[0]
            source_schema = 'public'
        elif len(source) == 2:
            source_table = source[1]
            source_schema = source[0]
        else:
            raise Exception("invalid format for source data - please use 'schema'.'table'")
        full_source_table = '"{schema}"."{table}"'.format(schema=source_schema, table=source_table)
        name = options.get('name')
        assert table_exists(source_table, source_schema), "the source table you provided does not exist in the database"

        if options.get('to'):
            scenario = Scenario.objects.get(name=options.get('to'))
        else:
            assert name, "you must provide a name for the scenario with the --name option"

            scenario = create_scenario_clone()[0]
            scenario.name = options.get('name')

            previous = scenario._no_post_save_publishing
            scenario._no_post_save_publishing = True
            scenario.save()
            scenario._no_post_save_publishing = previous

        end_state = scenario.db_entity_by_key('scenario_end_state')
        cursor = connection.cursor()

        source_columns = {
            c.name: c for c in SmartDatabaseIntrospection(connection).describe_table_columns(cursor, full_source_table)
        }

        destination_columns = {
            c.name: c for c in SmartDatabaseIntrospection(connection).describe_table_columns(cursor, end_state.full_table_name)
        }
        del destination_columns['id']

        join_on = options.get('join_on')
        assert join_on in source_columns, "The join column {c} is not in your source table.".format(c=join_on)
        assert 'built_form_key' in source_columns, "The source data has no built_form_key field"

        join_to = options.get('join_to')
        assert join_to in ['geography_id', 'source_id', 'id']
        if join_to == 'geography_id':
            raise NotImplementedError("Complex query using rel_id's not implemented - use source_id (default) for join")
        user_id = User.objects.get(username="admin").id

        if options.get('full'):
            from_column_check = source_columns.copy()

            for k, v in destination_columns.items():
                from_column_check.pop(k)

            destination_columns.pop('built_form_base')

            columns = [k for k, v in destination_columns.items()]

            equations = ''

            for c in columns:
                equations += '\n{column} = source.{column},'.format(column=c)

            equations = equations[:-1]
            import_query = "update {destination_table} as destination set {equations} from {source_table} as source " \
            "where destination.{join_to} = source.{join_on};".format(destination_table=end_state.full_table_name,
                                                                    source_table=full_source_table,
                                                                    equations=equations,
                                                                    join_to=join_to,
                                                                    join_on=join_on)


            rel_table = '"{0}"."{1}"'.format(end_state.schema, 'scenario_end_staterel')

            rel_join = "coreendstatefeature{db_entity_id}_ptr_id".format(db_entity_id=end_state.id)


            rel_update_query = """
            UPDATE {rel_table} AS rel SET
              updater_id = {user_id},
              built_form_id = b.built_form_id,
              updated = CURRENT_TIMESTAMP
              FROM (
               SELECT endstate.id, endstate.built_form_key, bf.id AS built_form_id
               FROM {destination_table} AS endstate
               LEFT JOIN main_builtform bf ON (endstate.built_form_key = bf.key)) b
              WHERE rel.{rel_join} = b.id""".format(destination_table=end_state.full_table_name,
                                                                      user_id=user_id, rel_join=rel_join, rel_table=rel_table)
            # insert = "insert into {table} as destination ({columns}) (select {columns} from {source});".format(
            #     table=end_state.full_table_name, source=full_source_table, columns=columns_str)
            logger.info(import_query)
            cursor.execute(import_query)
            logger.info("Imported {count} rows to the scenario".format(count=cursor.rowcount))

            logger.info(rel_update_query)
            cursor.execute(rel_update_query)
            logger.info("Imported {count} rows to the scenario".format(count=cursor.rowcount))

        else:

            optional_columns = {
                'dev_pct': 1,
                'density_pct': 1,
                'gross_net_pct': 1,
                'dirty_flag': True,
                'clear_flag': False,
                'redevelopment_flag': False,
                'developable_proportion': 1,
            }

            #todo really what else do we need?
            required_columns = ['built_form_key']

            select_columns = filter(lambda c: (c in optional_columns or c in required_columns), source_columns)
            default_columns = filter(lambda c: c not in source_columns, optional_columns)

            equations = ''
            for c in select_columns:
                equations += '{column} = source.{column},'.format(column=c)
            for c in default_columns:
                logger.warning("No source data for {column}, using default of {default}".format(column=c,
                                                                                                default=default_columns[c]))
                equations += "{column} = {default},".format(column=c, default=default_columns[c])

            equations = equations[:-1]
            import_query = "update {destination_table} as destination set {equations} from {source_table} as source " \
            "where destination.{join_to} = source.{join_on};".format(destination_table=end_state.full_table_name,
                                                                    source_table=full_source_table,
                                                                    equations=equations,
                                                                    join_to=join_to,
                                                                    join_on=join_on)
            cursor = connection.cursor()
            logger.info("Importing scenario {0}".format(scenario.key))

            cursor.execute(import_query)
            logger.info("Updated {count} rows in the rel table".format(count=cursor.rowcount))

        # todo populate increment table with diff between base and end state
        increment_table = scenario.db_entity_by_key('scenario_increment')
        base_table = scenario.db_entity_by_key('base_feature').full_table_name
        update_increment = """
        update {increment} a set
        land_development_category = b.land_development_category ,
        pop = b.pop,
        hh = b.hh,
        du = b.du,
        du_detsf = b.du_detsf,
        du_detsf_ll= b.du_detsf_ll,
        du_detsf_sl = b.du_detsf_sl,
        du_attsf = b.du_attsf,
        du_mf = b.du_mf,
        emp = b.emp,
        emp_ret = b.emp_ret,
        emp_off = b.emp_off,
        emp_pub = b.emp_pub,
        emp_ind = b.emp_ind,
        emp_ag = b.emp_ag,
        emp_military = b.emp_military,
        emp_retail_services = b.emp_retail_services,
        emp_restaurant = b.emp_restaurant, emp_accommodation = b.emp_accommodation,
        emp_arts_entertainment = b.emp_arts_entertainment, emp_other_services = b.emp_other_services,
        emp_office_services = b.emp_office_services, emp_education = b.emp_education,
        emp_public_admin = b.emp_public_admin, emp_medical_services = b.emp_medical_services,
        emp_wholesale = b.emp_wholesale, emp_transport_warehousing = b.emp_transport_warehousing,
        emp_manufacturing = b.emp_manufacturing, emp_utilities = b.emp_utilities,
        emp_construction = b.emp_construction, emp_agriculture = b.emp_agriculture, emp_extraction = b.emp_extraction

        FROM (select
        a.id, a.land_development_category,
        a.pop - b.pop as pop, a.hh - b.hh as hh,
        a.du - b.du as du, a.du_detsf - b.du_detsf as du_detsf,
        a.du_detsf_ll - b.du_detsf_ll as du_detsf_ll, a.du_detsf_sl - b.du_detsf_sl as du_detsf_sl,
        a.du_attsf - b.du_attsf as du_attsf, a.du_mf - b.du_mf as du_mf,
        a.emp - b.emp as emp, a.emp_ret - b.emp_ret as emp_ret, a.emp_off - b.emp_off as emp_off,
        a.emp_ind - b.emp_ind as emp_ind, a.emp_pub - b.emp_pub as emp_pub, a.emp_ag - b.emp_ag as emp_ag,
        a.emp_military - b.emp_military as emp_military,
        a.emp_retail_services - b.emp_retail_services as emp_retail_services,
        a.emp_restaurant - b.emp_restaurant as emp_restaurant,
        a.emp_arts_entertainment - b.emp_arts_entertainment as emp_arts_entertainment,
        a.emp_accommodation - b.emp_accommodation as emp_accommodation,
        a.emp_other_services - b.emp_other_services as emp_other_services,
        a.emp_office_services - b.emp_office_services as emp_office_services,
        a.emp_education - b.emp_education as emp_education,
        a.emp_public_admin - b.emp_public_admin as emp_public_admin,
        a.emp_medical_services - b.emp_medical_services as emp_medical_services,
        a.emp_wholesale - b.emp_wholesale as emp_wholesale,
        a.emp_transport_warehousing - b.emp_transport_warehousing as emp_transport_warehousing,
        a.emp_manufacturing - b.emp_manufacturing as emp_manufacturing,
        a.emp_utilities - b.emp_utilities as emp_utilities,
        a.emp_construction - b.emp_construction as emp_construction ,
        a.emp_agriculture - b.emp_agriculture as emp_agriculture,
        a.emp_extraction - b.emp_extraction as emp_extraction
        from {end_state} a
        left join {base} b on a.id = b.id) b
        where a.id = b.id;
        """.format(increment=increment_table.full_table_name, end_state=end_state.full_table_name, base=base_table)

        cursor.execute(update_increment)

        increment_rel = '"{0}"."{1}"'.format(increment_table.schema, increment_table.table + "rel")
        rel_join = "coreincrementfeature{db_entity_id}_ptr_id".format(db_entity_id=increment_table.id)

        update_increment_built_form = """
          update {increment} as increment
          set built_form_key = b.built_form_key
          from (
            select endstate.id as endstate_id, base.id as base_id,
            base.built_form_key as built_form_base, endstate.built_form_key as built_form_key
            from {endstate} as endstate
            LEFT JOIN {base} as base on endstate.id = base.id) as b
        WHERE b.endstate_id = increment.id and b.built_form_base != b.built_form_key
        """.format(increment=increment_table.full_table_name, endstate=end_state.full_table_name, base=base_table)

        update_increment_rel = """
            UPDATE {rel_table} AS rel SET
              updater_id = {user_id},
              built_form_id = b.built_form_id,
              updated = CURRENT_TIMESTAMP
              FROM (
               SELECT increment.id, increment.built_form_key, bf.id AS built_form_id
               FROM {destination_table} AS increment
               LEFT JOIN main_builtform bf ON (increment.built_form_key = bf.key)) b
              WHERE rel.{rel_join} = b.id""".format(destination_table=increment_table.full_table_name,
                                                      user_id=user_id, rel_join=rel_join, rel_table=increment_rel)
        logger.info(update_increment_built_form)
        cursor.execute(update_increment_built_form)
        logger.info("Updated {count} rows in the increments tableq".format(count=cursor.rowcount))

        logger.info(update_increment_rel)
        cursor.execute(update_increment_rel)
        logger.info("Updated {count} rows in the increments rel table".format(count=cursor.rowcount))

        # mgmt_kwargs = {'skip': True, 'import': True, "config_entity_keys": scenario.key}
        #
        # # logger.info("Running import for scenario key {key}".format(key=scenario.key))
        # # management.call_command('footprint_init', **mgmt_kwargs)
