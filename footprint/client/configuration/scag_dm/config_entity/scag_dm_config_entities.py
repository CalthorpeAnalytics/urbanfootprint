
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

from footprint.client.configuration.default.config_entity.default_project import project_key
from footprint.client.configuration.fixture import ConfigEntitiesFixture, MediumFixture
from footprint.client.configuration.default.config_entity.default_config_entities import ConfigEntityMediumKey
from django.conf import settings
from footprint.main.models.category import Category
from footprint.main.models.config.scenario import BaseScenario
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.utils.fixture_list import FixtureList
from django.contrib.gis.geos import MultiPolygon, Polygon

__author__ = 'calthorpe_analytics'



class ScagDmDbEntityKey(DbEntityKey):
    #SCAG regional datasets
    FLOOD_ZONES = 'flood_zones'
    CPAD_HOLDINGS = 'cpad_holdings'
    FARMLAND = 'farmland'
    ENDANGERED_SPECIES = 'endangered_species'
    HABITAT_CONSERVATION_AREA = 'habitat_conservation_areas'
    COUNTY_BOUNDARY = 'county_boundary'
    HIGH_QUALITY_TRANSIT_AREAS = 'high_quality_transit_areas'
    HIGH_QUALITY_TRANSIT_AREAS_2012 = 'high_quality_transit_areas_2012'
    HIGH_QUALITY_TRANSIT_AREAS_2040 = 'high_quality_transit_areas_2040'
    HIGH_QUALITY_TRANSIT_CORRIDORS = 'high_quality_transit_corridors'
    HIGH_QUALITY_TRANSIT_CORRIDORS_2012 = 'high_quality_transit_corridors_2012'
    HIGH_QUALITY_TRANSIT_CORRIDORS_2040 = 'high_quality_transit_corridors_2040'
    MAJOR_TRANSIT_STOPS = 'major_transit_stops'
    MAJOR_TRANSIT_STOPS_2012 = 'major_transit_stops_2012'
    MAJOR_TRANSIT_STOPS_2040 = 'major_transit_stops_2040'
    TRANSIT_PRIORITY_AREAS = 'transit_priority_areas'
    TRANSIT_PRIORITY_AREAS_2012 = 'transit_priority_areas_2012'
    TRANSIT_PRIORITY_AREAS_2040 = 'transit_priority_areas_2040'
    SUB_REGION = 'sub_region'
    CENSUS_TRACTS = 'census_tracts'

    EXISTING_LAND_USE_PARCELS_2012 = 'existing_land_use_parcels_2012'
    EXISTING_LAND_USE_PARCELS_2016 = 'existing_land_use_parcels_2016'
    REGION_EXISTING_LAND_USE_PARCELS = 'region_existing_land_use_parcels'
    PROJECT_EXISTING_LAND_USE_PARCELS = 'project_existing_land_use_parcels'

    GENERAL_PLAN_PARCELS = 'general_plan_parcels'
    REGION_GENERAL_PLAN_PARCELS = 'region_general_plan_parcels'

    ENTITLEMENT_PARCELS_2016 = 'entitlement_parcels_2016'
    REGION_ENTITLEMENT_PARCELS_2016 = 'region_entitlement_parcels_2016'

    SCENARIO_PLANNING_ZONES = 'scenario_planning_zones'
    REGION_SCENARIO_PLANNING_ZONES = 'region_scenario_planning_zones'

    JURISDICTION_BOUNDARY = 'jurisdiction_boundary'
    REGION_JURISDICTION_BOUNDARY = 'region_jurisdiction_boundary'

    SPHERE_OF_INFLUENCE = 'sphere_of_influence'
    REGION_SPHERE_OF_INFLUENCE = 'region_sphere_of_influence'

    TIER2_TAZ = 'tier2_taz'
    REGION_TIER2_TAZ = 'region_tier2_taz'

    CITY_BOUNDARY = 'city_boundary'
    REGION_CITY_BOUNDARY = 'region_city_boundary'
    PROJECT_CITY_BOUNDARY = 'project_city_boundary'
    BIKE_LANE = 'bike_lane'
    SEA_LEVEL_RISE = 'sea_level_rise'


class ScagDmConfigEntitiesFixture(ConfigEntitiesFixture):
    def regions(self, region_keys=None, class_scope=None):
        return FixtureList([
            dict(
                key='scag',
                name='The SCAG Region',
                description='Jurisdictions of the SCAG Region',
                media=[
                    MediumFixture(key=ConfigEntityMediumKey.Fab.ricate('scag_logo'), name='SCAG Logo',
                                    url='/static/client/{0}/logos/scag_dm.png'.format(settings.CLIENT))
                ],
                #defaulting to an Irvine view for the moment
                bounds=MultiPolygon([Polygon((
                    (-117.869537353516, 33.5993881225586),
                    (-117.869537353516, 33.7736549377441),
                    (-117.678024291992, 33.7736549377441),
                    (-117.678024291992, 33.5993881225586),
                    (-117.869537353516, 33.5993881225586),
                ))])
            )
        ]).matching_keys(key=region_keys).matching_scope(class_scope=class_scope)


    def projects(self, region=None, region_keys=None, project_keys=None, class_scope=None):
        # All SCAG jurisdictions
        imperial        = [ 'Brawley', 'Calexico', 'Calipatria', 'El Centro', 'Holtville',
                            'Imperial', 'Unincorporated: Imperial', 'Westmorland' ]

        los_angeles    = [ 'Agoura Hills', 'Alhambra', 'Arcadia', 'Artesia', 'Avalon',
                           'Azusa', 'Baldwin Park', 'Bell', 'Bell Gardens', 'Bellflower',
                           'Beverly Hills', 'Bradbury', 'Burbank', 'Calabasas', 'Carson',
                           'Cerritos', 'Claremont', 'Commerce', 'Compton', 'Covina', 'Cudahy',
                           'Culver City', 'Diamond Bar', 'Downey', 'Duarte', 'El Monte',
                           'El Segundo', 'Gardena', 'Glendale', 'Glendora', 'Hawaiian Gardens',
                           'Hawthorne', 'Hermosa Beach', 'Hidden Hills', 'Huntington Park',
                           'Industry', 'Inglewood', 'Irwindale', 'La Canada Flintridge',
                           'La Habra Heights', 'La Mirada', 'La Puente', 'La Verne',
                           'Lakewood', 'Lancaster', 'Lawndale', 'Lomita', 'Long Beach',
                           'Los Angeles', 'Lynwood', 'Malibu', 'Manhattan Beach', 'Maywood',
                           'Monrovia', 'Montebello', 'Monterey Park', 'Norwalk', 'Palmdale',
                           'Palos Verdes Estates', 'Paramount', 'Pasadena', 'Pico Rivera',
                           'Pomona', 'Rancho Palos Verdes', 'Redondo Beach', 'Rolling Hills',
                           'Rolling Hills Estates', 'Rosemead', 'San Dimas', 'San Fernando',
                           'San Gabriel', 'San Marino', 'Santa Clarita', 'Santa Fe Springs',
                           'Santa Monica', 'Sierra Madre', 'Signal Hill', 'South El Monte',
                           'South Gate', 'South Pasadena', 'Temple City', 'Torrance',
                           'Unincorporated: Los Angeles', 'Vernon', 'Walnut', 'West Covina',
                           'West Hollywood', 'Westlake Village', 'Whittier' ]

        orange         = [ 'Aliso Viejo', 'Anaheim', 'Brea', 'Buena Park', 'Costa Mesa', 'Cypress',
                           'Dana Point', 'Fountain Valley', 'Fullerton', 'Garden Grove', 'Huntington Beach',
                           'Irvine', 'La Habra', 'La Palma', 'Laguna Beach', 'Laguna Hills', 'Laguna Niguel',
                           'Laguna Woods', 'Lake Forest', 'Los Alamitos', 'Mission Viejo', 'Newport Beach',
                           'Orange', 'Placentia', 'Rancho Santa Margarita', 'San Clemente',
                           'San Juan Capistrano', 'Santa Ana', 'Seal Beach', 'Stanton', 'Tustin',
                           'Unincorporated: Orange', 'Villa Park', 'Westminster', 'Yorba Linda' ]

        riverside      = [ 'Banning', 'Beaumont', 'Blythe', 'Calimesa', 'Canyon Lake', 'Cathedral City',
                           'Coachella', 'Corona', 'Desert Hot Springs', 'Eastvale', 'Hemet',
                           'Indian Wells', 'Indio', 'Jurupa Valley', 'La Quinta', 'Lake Elsinore',
                           'Menifee', 'Moreno Valley', 'Murrieta', 'Norco', 'Palm Desert', 'Palm Springs',
                           'Perris', 'Rancho Mirage', 'Riverside', 'San Jacinto', 'Temecula',
                           'Unincorporated: Riverside', 'Wildomar']

        san_bernardino = [ 'Adelanto', 'Apple Valley', 'Barstow', 'Big Bear Lake', 'Chino',
                           'Chino Hills', 'Colton', 'Fontana', 'Grand Terrace', 'Hesperia',
                           'Highland', 'Loma Linda', 'Montclair', 'Needles', 'Ontario',
                           'Rancho Cucamonga', 'Redlands', 'Rialto', 'San Bernardino',
                           'Twentynine Palms', 'Unincorporated: San Bernardino', 'Upland',
                            'Victorville', 'Yucaipa', 'Yucca Valley' ]

        ventura         = [ 'Camarillo', 'Fillmore', 'Moorpark', 'Ojai', 'Oxnard', 'Port Hueneme',
                            'San Buenaventura', 'Santa Paula', 'Simi Valley', 'Thousand Oaks',
                            'Unincorporated: Ventura']

        jurisdictions = imperial + los_angeles + orange + riverside + san_bernardino + ventura

        # Create only a small subset of jurisdictions for the dev environments
        if settings.USE_SAMPLE_DATA_SETS:
            jurisdictions = ["Anaheim", 'Irvine']

        configurations = map(lambda jurisdiction_name: {
            'key': project_key(jurisdiction_name),
            'import_key': jurisdiction_name.lower().replace(' ', '_').replace(':', ''),
            'name': jurisdiction_name,
            'description': "City of %s" % jurisdiction_name,
            'base_year': 2014,
            'region_key': 'scag',
            'media': [
                    MediumFixture(key=ConfigEntityMediumKey.Fab.ricate(jurisdiction_name.lower().replace(' ', '_') + '_logo'),
                                  name='%s Logo' % jurisdiction_name,
                                  url='/static/client/{0}/logos/{1}_logo.png'.format(settings.CLIENT, jurisdiction_name.lower().replace(' ', '_')))
                ]
        }, jurisdictions)

        return FixtureList(configurations).matching_keys(region_keys=region_keys, key=project_keys).matching_scope(class_scope=class_scope)


    def scenarios(self, project=None, region_keys=None, project_keys=None, scenario_keys=None, class_scope=None):

        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate
        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        return FixtureList([
            {
                'class_scope': BaseScenario,
                'key': '{0}_s'.format(project.key),
                'scope': project.schema(),
                'name': '{0}'.format(project.name),
                'description': '{0} layers {1}'.format('2014', project.name),
                'year': 2014,
                'behavior': get_behavior('base_scenario'),
                'categories': [Category(key='category', value='base_year')]
            }]).matching_keys(region_key=region_keys, project_key=project.key if project else project_keys, key=scenario_keys).\
           matching_scope(class_scope=class_scope)
