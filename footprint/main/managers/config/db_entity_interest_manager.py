
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

from footprint.main.lib.functions import unique
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.config.interest import Interest
from footprint.main.models.geospatial.db_entity import DbEntity
from footprint.main.models.database.information_schema import InformationSchema
from footprint.main.models.keys.keys import Keys

__author__ = 'calthorpe_analytics'

class DbEntityInterestManager(GeoInheritanceManager):

    def sync_db_table_entities(self, config_entity):
        """
            Syncs the db_entities representing tables with the tables in the this instance's schema. This should only
            be used when tables are added or removed from the system outside of the UrbanFootprint application.
            Normally the db_entries will stay synced automatically. No DbEntry instances representing queries, views,
            or other table-based representations are added or deleted here.
        """
        # Load the db_entities that represent tables
        table_entities = config_entity.db_entities.filter(table__isnull=False, query__isnull=True)
        table_entity_names = map(lambda table_entity: table_entity.table, table_entities)
        # Load the physical tables in the schema
        table_names = unique(
            map(
                lambda information_schema: information_schema.table_name,
                InformationSchema.objects.filter(table_schema=config_entity.schema())))
        # Compare table names to find new tables for which to create entries
        owner_interest = Interest.objects.get(key=Keys.INTEREST_OWNER)
        for new_table_name in set(table_names) - set(table_entity_names):
            # Create the DbEntity and join it to the ConfigEntity with an owner DbEntityInterest
            table_entity = DbEntity.objects.create(name=new_table_name, schema=config_entity.schema(), table=new_table_name)
            self.create(config_entity=config_entity, db_entity=table_entity, interest=owner_interest)

        # Compare table names to find deleted tables for which to delete entries
        for table_entity in table_entities:
            if not table_entity.table in table_names:
                table_entity.delete()
