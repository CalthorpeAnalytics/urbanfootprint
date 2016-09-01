
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

from inflection import titleize
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.geospatial.db_entity import DbEntity
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.models.geospatial.feature_class_configuration import FeatureClassConfiguration
from footprint.main.lib.functions import dual_map_to_dict, map_to_dict, get_first, merge
from footprint.main.models.presentation.medium import Medium
from footprint.main.models.keys.keys import Keys
from footprint.main.utils.utils import expect

__author__ = 'calthorpe_analytics'

def initialize_result_media(sender, **kwargs):
    """
        This fires when the application initializes or updates the GlobalConfig and all other ConfigEntity instances.
        It creates style templates and their default contexts for the results based on any fixtures of the given ConfigEntity
    :param sender:
    :param kwargs:
    :return:
    """
    from footprint.client.configuration.fixture import ResultConfigurationFixture
    from footprint.client.configuration.utils import resolve_fixture


class ResultLibraryKey(Keys):
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            return 'result_library'

    # The default ResultLibrary. All Results are always in this Library
    DEFAULT = Fab.ricate('default')
    # The ResultLibrary that is independent of an AnalysisModule
    APPLICATION = Fab.ricate('application')
    # The following show when the corresponding analysis module is selected
    WATER = Fab.ricate('water')
    ENERGY = Fab.ricate('energy')
    VMT = Fab.ricate('vmt')
    FISCAL = Fab.ricate('fiscal')
    AGRICULTURE_ANALYSIS = Fab.ricate('agriculture_analysis')
    PUBLIC_HEALTH = Fab.ricate('public_health')

class ResultKey(Keys):
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            return 'result'
    BASE_EMPLOYMENT_BY_TYPE = Fab.ricate('base_employment_by_type')
    BASE_DWELLING_UNITS_BY_TYPE = Fab.ricate('base_dwelling_units_by_type')
    INCREMENTS = Fab.ricate('increments')
    INCREMENTS_EMPLOYMENT_BY_TYPE = Fab.ricate('increments_employment_by_type')
    INCREMENTS_DWELLING_UNITS_BY_TYPE = Fab.ricate('increments_dwelling_units_by_type')
    INCREMENTS_BARS = Fab.ricate('increments_bars')
    END_STATE = Fab.ricate('end_state')
    END_STATE_EMPLOYMENT_BY_TYPE = Fab.ricate('end_state_employment_by_type')
    END_STATE_DWELLING_UNITS_BY_TYPE = Fab.ricate('end_state_dwelling_units_by_type')
    END_STATE_BARS = Fab.ricate('end_state_bars')
    FISCAL = Fab.ricate('fiscal')
    VMT = Fab.ricate('vmt')
    VMT_PER_CAPITA = Fab.ricate('vmt_per_capita')
    VMT_FUEL = Fab.ricate('vmt_fuel')
    VMT_COSTS = Fab.ricate('vmt_costs')
    VMT_EMISSIONS = Fab.ricate('vmt_emissions')

    WATER = Fab.ricate('water')
    WATER_TOTAL = Fab.ricate('water_total')
    WATER_INDOOR_OUTDOOR = Fab.ricate('water_indoor_outdoor')
    WATER_COSTS_TOTAL = Fab.ricate('water_costs_total')

    AGRICULTURE = Fab.ricate('agriculture')
    AGRICULTURE_ROI = Fab.ricate('agriculture_roi')

    SOCIOECONOMIC_BASE = Fab.ricate('socio_economic_base')
    SOCIOECONOMIC_FUTURE = Fab.ricate('socio_economic_future')

    SOCIOECONOMIC12 = Fab.ricate('socio_economic_12')
    SOCIOECONOMIC20 = Fab.ricate('socio_economic_20')
    SOCIOECONOMIC35 = Fab.ricate('socio_economic_35')
    SOCIOECONOMIC40 = Fab.ricate('socio_economic_40')

    POPULATION_BY_YEAR = Fab.ricate('pop_by_year')
    HOUSEHOLDS_BY_YEAR = Fab.ricate('hh_by_year')
    EMPLOYMENT_BY_YEAR = Fab.ricate('emp_by_year')

    ENERGY = Fab.ricate('energy')
    ENERGY_TOTAL = Fab.ricate('energy_total')
    ENERGY_RES_USE = Fab.ricate('energy_res_use')
    ENERGY_COM_USE = Fab.ricate('energy_com_use')
    ENERGY_COSTS_TOTAL = Fab.ricate('energy_costs')
    ENERGY_EMISSIONS_TOTAL = Fab.ricate('energy_emissions')

    FISCAL_CHART = Fab.ricate('fiscal_chart')

    PH_WALKING_MINUTES = Fab.ricate('ph_walking_minutes')
    PH_AUTO_MINUTES = Fab.ricate('ph_auto_minutes')
    PH_REC_PA_MINUTES = Fab.ricate('ph_rec_pa_minutes')
    PH_OUTCOMES_TABLE = Fab.ricate('ph_outcomes_table')


class ResultMediumKey(ResultKey):
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            return 'result__medium'

    # The default medium for all results
    DEFAULT = Fab.ricate('default')
    BASE_EMPLOYMENT_BY_TYPE = Fab.ricate('base_employment_by_type')
    BASE_DWELLING_UNITS_BY_TYPE = Fab.ricate('base_dwelling_units_by_type')
    INCREMENTS = Fab.ricate('increments')
    INCREMENTS_DWELLING_UNITS_BY_TYPE = Fab.ricate('increments_dwelling_units_by_type')
    INCREMENTS_EMPLOYMENT_BY_TYPE = Fab.ricate('increments_employment_by_type')
    END_STATE = Fab.ricate('end_state')
    END_STATE_EMPLOYMENT_BY_TYPE = Fab.ricate('end_state_employment_by_type')
    END_STATE_DWELLING_UNITS_BY_TYPE = Fab.ricate('end_state_dwelling_units_by_type')
    END_STATE_BARS = Fab.ricate('end_state_bars')
    WATER_TOTAL = Fab.ricate('water_total')
    WATER_INDOOR_OUTDOOR = Fab.ricate('water_indoor_outdoor')
    WATER_COSTS_TOTAL = Fab.ricate('water')
    ENERGY_TOTAL = Fab.ricate('energy_total')
    ENERGY_RES_USE = Fab.ricate('energy_res_use')
    ENERGY_COM_USE = Fab.ricate('energy_com_use')
    ENERGY_COSTS_TOTAL = Fab.ricate('energy_costs')
    ENERGY_EMISSIONS_TOTAL = Fab.ricate('energy_emissions')
    VMT_PER_CAPITA = Fab.ricate('vmt_per_capita')
    VMT_FUEL = Fab.ricate('vmt_fuel')
    VMT_COSTS = Fab.ricate('vmt_costs')
    VMT_EMISSIONS = Fab.ricate('vmt_emissions')

    FISCAL_CHART = Fab.ricate('fiscal_chart')

class ResultLibraryConfiguration(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        expect(self, 'key', 'name', 'description')
        # The optional ConfigEntity class scope of the Result. Only config_entities that match or inherit this will create a result_library
    class_scope=None,
    key=None,
    name=None,
    description=None

class ResultConfiguration(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    # The optional ConfigEntity class scope of the Result. Only config_entities that match or inherit this will create a result
    class_scope = None
    # The keys of the ResultLibrary to which this Result belongs
    # All results always go in the Default ResultLibrary
    library_keys = None
    # The result type 'bar_graph', 'analytic_bars'
    result_type = None
    # The key of the created DbEntity for the Result. These must be unique across a config_entity
    result_db_entity_key = None,
    name = None,
    # The class attributes to show in the result. These are used for column names, data, control totals, etc.
    attributes = [],
    # Localized and presentable name for attributes, by matching array order
    labels = [],
    # A dict mapping each attribute to the database column name returned by the query, without the __sum, __avg, etc suffix
    db_column_lookup = {},
    # Maps each attribute to a dict with a min and max to use for extents for result presentations that need them static
    extent_lookup = {},
    # Is the bar graph stackable
    stackable = False,
    # Is the bar graph stacked initially
    is_stacked = False,
    # Indicates that control total lines should be drawn on the graph
    include_control_totals = True
    # The source DbEntity from which the Result's DbEntity is cloned
    source_db_entity_key = None
    # Query lambda for the Result
    create_query = None

    def get_presentation_medium_configuration(self):
        """
            Extracts the essential information needed by the Result configuration attribute
        :return:
        """
        return dict(
            # Create a dict that translates the column names to labels
            column_to_label=self.create_column_to_label(),
            # Create a dict that translates the column names to attribute names (used by the UI)
            attribute_to_column=self.db_column_lookup,
            # fixes attribute order
            attributes=self.attributes,
            extent_lookup=self.extent_lookup,
            stackable=self.stackable,
            is_stacked=self.is_stacked,
            result_type=self.result_type,
            # Set a control total to 0 for each column
            control_totals=self.create_control_totals() if self.include_control_totals else [],
            sort_priority=self.sort_priority
        )

    def update_or_create_db_entity_interest(self, config_entity, existing_db_entity_interest):
        """
            Clone the DbEntity from the increments DbEntity
            This means the queryset is run on the Increments class manager
        :param config_entity:
        :param the existing_db_entity_interest if one exists
        :return: Return the DbEntity
        """

        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate
        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))
        return self.clone_db_entity_and_interest_for_result(
            config_entity,
            existing_db_entity_interest,
            self.source_db_entity_key,
            key=self.result_db_entity_key,
            name=titleize(self.name),
            query=self.create_query(self),
            feature_behavior=FeatureBehavior(
                behavior=get_behavior('result')
            )
        )

    def clone_db_entity_and_interest_for_result(self, config_entity, existing_db_entity_interest, reference_db_entity_key, **kwargs):
        """
            Clone the selected db_entity of key reference_db_entity and replace any of its attributes with those
            specified in **kwargs. **kwargs should contain a unique key property
        :param config_entity
        :param existing_db_entity_interest: The existing DbEntityInterest if one exists
        :param reference_db_entity_key: key of the DbEntity to clone
        :param kwargs: replacement values containing at the very least 'key'
        :return: The DbEntityInterest which references the cloned db_entity
        """
        source_db_entity = config_entity.computed_db_entities().get(key=reference_db_entity_key)
        # Avoid circular reference
        from footprint.main.publishing.db_entity_publishing import clone_or_update_db_entity_and_interest

        db_entity_interest = clone_or_update_db_entity_and_interest(
            config_entity,
            source_db_entity,
            DbEntity(**merge(
                kwargs,
                dict(
                    feature_class_configuration=FeatureClassConfiguration(
                        **merge(source_db_entity.feature_class_configuration.__dict__,
                                dict(feature_class_owner=reference_db_entity_key))),
                )
            )),
            existing_db_entity_interest=existing_db_entity_interest,
            override_on_update=True
        )
        # Run this manually here. It should be triggered by saving the DbEntity, but something
        # is disabling the publisher
        # TODO the DbEntity publihser should be turned on here so this should be neeed
        from footprint.main.publishing.user_publishing import on_db_entity_post_save_user
        on_db_entity_post_save_user(None, instance=db_entity_interest)
        return db_entity_interest

    def create_column_to_label(self):
        """
            Create a mapping between table column names and labels, based on the attribute names
        :return:
        """
        return dual_map_to_dict(
            lambda attribute, label: [self.db_column_lookup[attribute], label],
            self.attributes,
            self.labels)

    def create_control_totals(self):
        """
            Create a dict of initial control totals
        :return:
        """
        return map_to_dict(
            lambda column: [column, 0],
            self.attributes)

    def resolve_result_medium(self):
        """
            Get the Medium of the result key or default
        :return:
        """
        return get_first(
            # See if a Medium exists with a key corresponding to the result
            # Default to the default Medium for results
            Medium.objects.filter(key=self.result_db_entity_key.replace('result', 'result__medium')),
            default=Medium.objects.get(key=ResultMediumKey.DEFAULT)
        )

class ResultSort(object):
    FUTURE = 10
    BASE = 20
    OTHER = 60
    BACKGROUND = 80
