
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



__author__ = 'calthorpe_analytics'

class ConfigEntityRelatedCollectionAdoption(object):
    """
        ConfigEntity QuerySet mixin that enables collections of the parent_config_entity to be inherited or merged with the child's own collection
    """

    def computed_policy_sets(self, **query_kwargs):
        """
            Return this instance's policy_sets if they are not an empty list, otherwise traverses the parent hierarchy until a non-empty policy_sets list or the GlobalConfig is encountered. The list of that ancestor is returned
            :param **query_kwargs - optional filtering to apply to the results
        :return: The computed results
        """
        return self._computed('policy_sets', **query_kwargs)

    def computed_built_form_sets(self, **query_kwargs):
        """
            Return this instance's built_form_sets if they are not an empty list, otherwise traverses the parent hierarchy until a non-empty policy_sets list or the GlobalConfig is encountered. The list of that ancestor is returned
            :param **query_kwargs - optional filtering to apply to the results
        :return: The computed results
        """
        return self._computed('built_form_sets', **query_kwargs)

    def computed_db_entities(self, **query_kwargs):
        """
            Return this instance's db_entities_interests if they are not an empty list, otherwise traverses the parent hierarchy until a non-empty db_entities list or the GlobalConfig is encountered. The list of that ancestor is returned
            :param **query_kwargs - optional filtering to apply to the results
        :return:
        """
        db_entities = self._computed_related('db_entities', **query_kwargs)
        for db_entity in db_entities:
            if db_entity.schema not in self.schema() and db_entity.schema != 'global':
                self._computed_related('db_entities', **query_kwargs)
                raise Exception("For some reason the DbEntity schema {0} of DbEntity {1} is not part of the ConfigEntity schema hierarchy {2}".format(
                    db_entity.schema, db_entity.key, self.schema()))
        return db_entities

    def computed_db_entity(self, **query_kwargs):
        return self.computed_db_entities(**query_kwargs).get()

    def valid_computed_db_entities(self, **query_kwargs):
        """
            Filters out non-valid db_entities and then returns a query matching the valid ones
        """
        return self.computed_db_entities(id__in=map(lambda db_entity: db_entity.id, filter(lambda db_entity: db_entity.is_valid,
                      self.computed_db_entities(**query_kwargs))))

    def computed_db_entity_interests(self, **query_kwargs):
        """
            Like computed_db_entities, but returns the through DbEntityInterest instance instead of the DbEntityInterest
        :param query_kwargs:
        :return:
        """
        return self._computed('db_entities', **query_kwargs)
