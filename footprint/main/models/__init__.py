# coding=utf-8

# UrbanFootprint v1.5
# Copyright (C) 2017 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

# from constants import Constants

import logging

from django.core.exceptions import ImproperlyConfigured
from django.contrib import admin
from django.db import models

from south.modelsinspector import add_introspection_rules
add_introspection_rules([],  [r"^footprint.main.models.config.model_pickled_object_field.ModelPickledObjectField",
                              r"^footprint.main.models.config.model_pickled_object_field.SelectionModelsPickledObjectField"])

from footprint.main.models.config.model_pickled_object_field import ModelPickledObjectField
from footprint.main.models.config.model_pickled_object_field import SelectionModelsPickledObjectField

import geospatial

# These import statements are compulsory. Models will not be recognized without them
# There are some tricks published online to import all classes dynamically, but doing so in
# practice has yet been unsuccessful

from footprint.main.models.geospatial.behavior import Behavior
from footprint.main.models.analysis_module.analysis_module import AnalysisModule
from footprint.main.models.analysis.agriculture_feature import AgricultureFeature

from footprint.main.models.base.canvas_feature import CanvasFeature
from footprint.main.models.analysis.core_increment_feature import CoreIncrementFeature
from footprint.main.models.analysis.fiscal_feature import FiscalFeature
from footprint.main.models.analysis.energy_feature import EnergyFeature
from footprint.main.models.analysis.water_feature import WaterFeature
from footprint.main.models.analysis.swmm_feature import SwmmFeature
from footprint.main.models.analysis.public_health_features.ph_variables_feature import \
    PhVariablesFeature
from footprint.main.models.analysis.public_health_features.ph_grid_outcomes_feature import \
    PhGridOutcomesFeature
from footprint.main.models.analysis.public_health_features.ph_block_group_outcomes_feature import \
    PhBlockGroupOutcomesFeature
from footprint.main.models.analysis.vmt_features.vmt_feature import VmtFeature
from footprint.main.models.analysis.vmt_features.vmt_variables_feature import VmtVariablesFeature
from footprint.main.models.analysis.vmt_features.vmt_trip_lengths_feature import VmtTripLengthsFeature
from footprint.main.models.analysis.climate_zone_feature import ClimateZoneFeature
from footprint.main.models.database.information_schema import PGNamespace

from footprint.main.models.analysis.climate_zone_feature import ClimateZoneFeature

from footprint.main.models.built_form.built_form import BuiltForm
from footprint.main.models.geospatial.db_entity import DbEntity
from footprint.main.models.geospatial.behavior import Behavior
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.config.config_entity import ConfigEntity

from footprint.main.models.policy.energy.commercial_energy_baseline import CommercialEnergyBaseline
from footprint.main.models.policy.energy.residential_energy_baseline import ResidentialEnergyBaseline
from footprint.main.models.policy.water.evapotranspiration_baseline import EvapotranspirationBaseline

from footprint.main.models.base.census_rates_feature import CensusRatesFeature
from footprint.main.models.base.transit_stop_feature import TransitStopFeature

from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.built_form.flat_built_form import FlatBuiltForm
from footprint.main.models.base.census_blockgroup import CensusBlockgroup
from footprint.main.models.base.census_block import CensusBlock
from footprint.main.models.base.census_tract import CensusTract
from footprint.main.models.analysis.public_health_features.ph_grid_feature import PhGridFeature
from footprint.main.models.analysis.public_health_features.ph_outcomes_summary import PhOutcomesSummary

from footprint.main.models.built_form.primary_component import PrimaryComponent
from footprint.main.models.built_form.primary_component_percent import PrimaryComponentPercent
from footprint.main.models.built_form.placetype_component import PlacetypeComponent
from footprint.main.models.built_form.placetype_component_percent import PlacetypeComponentPercent
from footprint.main.models.built_form.placetype import Placetype

from footprint.main.models.built_form.urban.urban_placetype import UrbanPlacetype
from footprint.main.models.built_form.urban.building_attribute_set import BuildingAttributeSet
from footprint.main.models.built_form.urban.building_use_definition import BuildingUseDefinition
from footprint.main.models.built_form.urban.building_use_percent import BuildingUsePercent
from footprint.main.models.built_form.urban.building import Building
from footprint.main.models.built_form.urban.building_type import BuildingType

from footprint.main.models.built_form.agriculture.crop import Crop
from footprint.main.models.built_form.agriculture.crop_type import CropType
from footprint.main.models.built_form.agriculture.landscape_type import LandscapeType
from footprint.main.models.built_form.agriculture.agriculture_attribute_set import AgricultureAttributeSet

from footprint.main.models.config.db_entity_interest import DbEntityInterest

from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.interest import Interest
from footprint.main.models.config.policy_set import PolicySet
from footprint.main.models.config.region import Region
from footprint.main.models.config.project import Project
from footprint.main.models.config.scenario import Scenario
from footprint.main.models.base.canvas_feature import CanvasFeature
from footprint.main.models.base.cpad_holdings_feature import CpadHoldingsFeature
from footprint.main.models.geographies.geography import Geography
from footprint.main.models.geographies.parcel import Parcel
from footprint.main.models.geographies.grid_cell import GridCell
from footprint.main.models.geographies.taz import Taz
from footprint.main.models.presentation.chart import Chart
from footprint.main.models.presentation.geo_library import GeoLibrary
from footprint.main.models.presentation.geo_library_catalog import GeoLibraryCatalog
from footprint.main.models.presentation.grid import Grid
from footprint.main.models.presentation.layer_chart import LayerChart
from footprint.main.models.presentation.layer_library import LayerLibrary
from footprint.main.models.presentation.map import Map
from footprint.main.models.presentation.medium import Medium
from footprint.main.models.presentation.presentation import Presentation
from footprint.main.models.presentation.presentation_medium import PresentationMedium
from footprint.main.models.presentation.report import Report
from footprint.main.models.presentation.result.result import Result
from footprint.main.models.presentation.result_library import ResultLibrary
from footprint.main.models.presentation.style import Style
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.presentation_configuration import PresentationConfiguration
from footprint.main.models.sort_type import SortType
from footprint.main.models.presentation.layer_selection import LayerSelection

from footprint.main.models.analysis_module.public_health_module.public_health_updater_tool import PublicHealthOutcomeAnalysis

from footprint.main.models.analysis_module.environmental_constraint_module.environmental_constraint_percent import \
    EnvironmentalConstraintPercent
from footprint.main.models.analysis_module.environmental_constraint_module.environmental_constraint_updater_tool import \
    EnvironmentalConstraintUpdaterTool
from footprint.main.models.analysis_module.merge_module.merge_updater_tool import MergeUpdaterTool
from footprint.main.models.analysis_module.environmental_constraint_module.environmental_constraint_union_tool import EnvironmentalConstraintUnionTool

from footprint.main.models.group_hierarchy import GroupHierarchy

logger = logging.getLogger(__name__)

# Enable generic browsing of all models exported above in the Django
# admin interface.  But first, make a copy of locals so we can iterate
# it without it changing.
_l = dict(locals())
for key, cls in _l.iteritems():
    try:
        if issubclass(cls, models.Model):
            admin.site.register(cls)
    except (ImproperlyConfigured, TypeError):
        # Ignore
        pass
    except Exception as e:
        logging.exception('Ignoring admin error')
        print "(Save to ignore, this is just for admin interface)"

# This is required to wire the adoption signals at startup.
# TODO move signals to a Django startup hook
import signals
