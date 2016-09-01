
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
import time
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.analysis_module.analysis_tool import AnalysisTool
from footprint.main.models.geospatial.behavior import BehaviorKey
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.utils.uf_toolbox import drop_table, execute_sql, add_geom_idx, create_sql_calculations
from footprint.main.utils.utils import parse_schema_and_table

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'


class EnvironmentalConstraintUnionTool(AnalysisTool):

    objects = GeoInheritanceManager()

    class Meta(object):
        app_label = 'main'
        abstract = False

    def initialize(self, created):
        self.update()

    def update(self, **kwargs):

        """
            This function handles the update or creation on the environmental constraints geography producing the area
            for each layer with the environmental constraint behavior. This function will both add and remove
            constraints and produce the final constraints layer in the primary geography of the active scenario
        """
        # TODO : remove hard-coded 3310 (only works in CA), need to set an "analysis projection" in the Region
        start_time = time.time()

        current_db_entities = \
            set(self.config_entity.db_entities_having_behavior_key(BehaviorKey.Fab.ricate('environmental_constraint')))

        base_feature_class = self.config_entity.db_entity_feature_class(
            DbEntityKey.BASE_CANVAS)

        options = dict(
            project_schema=parse_schema_and_table(base_feature_class._meta.db_table)[0],
            base_table=base_feature_class.db_entity_key
        )

        logger.info('Inserting raw geographies into the environmental constraint geographies table for DbEntities: %s' % \
                    ', '.join(map(lambda db_entity: db_entity.name, current_db_entities)))

        drop_table('{project_schema}.environmental_constraint_geographies_table'.format(
            project_schema=options['project_schema'])
        )

        current_environmental_constraints = []
        for db_entity in current_db_entities:
            constraint_class = self.config_entity.db_entity_feature_class(db_entity.key)
            current_environmental_constraints.append(constraint_class.db_entity_key)

        create_id_field_format = create_sql_calculations(current_environmental_constraints, '{0}_id int')
        insert_id_field_format = create_sql_calculations(current_environmental_constraints, '{0}_id')

        pSql = '''
        create table {project_schema}.environmental_constraint_geographies_table
            (primary_id integer, wkb_geometry geometry, {create_id_field_format});
        SELECT UpdateGeometrySRID('{project_schema}', 'environmental_constraint_geographies_table', 'wkb_geometry', 3310)

        '''.format(project_schema=options['project_schema'], create_id_field_format=create_id_field_format)

        execute_sql(pSql)

        for db_entity in current_db_entities:
            logger.info('Inserting into environmental constraint geographies table for DbEntity: %s' % db_entity.full_name)

            constraint_class = self.config_entity.db_entity_feature_class(db_entity.key)

            pSql = '''
                insert into {project_schema}.environmental_constraint_geographies_table (primary_id, wkb_geometry, {constraint_db_entity_key}_id) select
                    cast(primary_id as int), wkb_geometry, {constraint_db_entity_key}_id from (
                    select
                        id as primary_id,
                        {constraint_db_entity_id} as {constraint_db_entity_key}_id,
                        st_setSRID(st_transform(st_buffer((st_dump(wkb_geometry)).geom, 0), 3310), 3310) as wkb_geometry

                    from (
                        select b.id, st_intersection(a.wkb_geometry, b.wkb_geometry) as wkb_geometry
	                    from {constraint_schema}.{constraint_db_entity_key} a,
                        {project_schema}.{base_table} b
                            where st_intersects(a.wkb_geometry, b.wkb_geometry)) as intersection
                    ) as polygons;
                '''.format(
                project_schema=options['project_schema'],
                base_table=options['base_table'],
                constraint_schema=parse_schema_and_table(constraint_class._meta.db_table)[0],
                constraint_db_entity_key=constraint_class.db_entity_key,
                constraint_db_entity_id=db_entity.id
            )

            execute_sql(pSql)

            logger.info('finished inserting db_entity: {db_entity} {time} elapsed'.format(
                time=time.time() - start_time,
                db_entity=constraint_class.db_entity_key))

        #only regenerate the merged environmental constraint whenever an envrionmental constraint is added or removed
        # from the layer

        add_geom_idx(options['project_schema'], 'environmental_constraint_geographies_table')

        logger.info('Unioning all environmental constraint geographies')
        drop_table('{project_schema}.environmental_constraint_geographies_table_unioned'.format(
            project_schema=options['project_schema'])
        )

        pSql = '''
            CREATE TABLE {project_schema}.environmental_constraint_geographies_table_unioned
                (id serial, wkb_geometry geometry, acres float, primary_id int, {create_id_field_format});
            SELECT UpdateGeometrySRID('{project_schema}', 'environmental_constraint_geographies_table_unioned', 'wkb_geometry', 3310);
        '''.format(project_schema=options['project_schema'], create_id_field_format=create_id_field_format)

        execute_sql(pSql)

        pSql = '''
        insert into {project_schema}.environmental_constraint_geographies_table_unioned (wkb_geometry, acres, primary_id, {insert_id_field_format})
               SELECT
                    st_buffer(wkb_geometry, 0) as wkb_geometry,
                    st_area(st_buffer(wkb_geometry, 0)) * 0.000247105 as acres,
                    primary_id, {insert_id_field_format}

                    FROM (
                        SELECT
                            (ST_Dump(wkb_geometry)).geom as wkb_geometry,
                            primary_id, {insert_id_field_format}

                        FROM (
                            SELECT ST_Polygonize(wkb_geometry) AS wkb_geometry, primary_id, {insert_id_field_format}   FROM (
                                SELECT ST_Collect(wkb_geometry) AS wkb_geometry, primary_id, {insert_id_field_format}   FROM (
                                    SELECT ST_ExteriorRing(wkb_geometry) AS wkb_geometry, primary_id, {insert_id_field_format}
                                        FROM {project_schema}.environmental_constraint_geographies_table) AS lines
                                            group by primary_id, {insert_id_field_format}) AS noded_lines
                                                group by primary_id, {insert_id_field_format}) as polygons
                    ) as final
                WHERE st_area(st_buffer(wkb_geometry, 0)) > 5;'''.format(
            project_schema=options['project_schema'],
            insert_id_field_format=insert_id_field_format
        )

        execute_sql(pSql)

        logger.info('finished unioning env constraints: {time} elapsed'.format(
            time=time.time() - start_time))

        #reproject table back to 4326 for integration with web viewing
        pSql = '''
        SELECT UpdateGeometrySRID('{project_schema}', 'environmental_constraint_geographies_table_unioned', 'wkb_geometry', 4326);
        update {project_schema}.environmental_constraint_geographies_table_unioned a set wkb_geometry = st_transform(st_buffer(wkb_geometry, 0), 4326);
        '''.format(
            project_schema=options['project_schema']
        )
        execute_sql(pSql)

        add_geom_idx(options['project_schema'], 'environmental_constraint_geographies_table_unioned')

        logger.info('Env Union Finished: %s' % str(time.time() - start_time))
