
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


# Hand-crafted basic fixture classes
# This stuff might be replaced by Django's json style fixtures in the future.
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from footprint.client.configuration.utils import resolve_fixture, resolve_parent_fixture
from footprint.main.lib.functions import unique, flat_map
from footprint.main.models.config.region import Region
from footprint.main.models.config.project import Project
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.utils.fixture_list import FixtureList
from footprint.main.utils.utils import expect

import logging
logger = logging.getLogger(__name__)
class Fixture(object):
    def __init__(self, schema, *args, **kwargs):
        """
            Creates a fixture instance
        :param schema: __-separated string that matches a ConfigEntity schema. This is used to designate what scope
         the fixture represents. If None, the Fixture is global/default. If one segment, the fixture represents
         a region (as of now equivalent to a settings.CLIENT). If two segments, it's scoped to a project within a
         region. If three segments (rare), it's scoped to a Scenario within a project.
        :param args: optional args used by the fixture
        :param kwargs: optional args used by a fixture. The most common is config_entity, which provides a fixture
        with a reference to its scoped config_entity in cases where the latter already exists and the fixture is
        provided configuration to that config_entity (e.g. layers)
        :return:
        """
        super(Fixture, self).__init__()
        # The default subclass of the Fixture. This is delegated to when a client-specific fixture calls the super
        # version of its methods. That way all default fixtures can be combined with custom client fixtures
        self.schema = schema
        self.init_args(**kwargs)
        self.args = args
        self.kwargs = kwargs
        self.expect(*self.expect_kwargs())

    def expect_kwargs(self):
        """
            Returns the required kwargs for a subclass. Default is none
        :return: An array of attribute strings.
        """
        return []

    # Class scope variables indicating the schema-relative module location of the fixture
    module = None,
    module_fragment = None

    @property
    def base_class(self):
        """
        Returns the base class is this class hierarchy that is used for matching the parent_fixture and default_fixture
        :return:
        """
        return None

    _parent_fixture = None

    # A reference to the parent fixture instance of this instance. The parent is the fixture represented by the
    # next level up of the schema string. So if self.schema is region__project, the parent is that with schema region.
    # If already at the region scope, the parent fixture is the default (global) fixture.
    # If nothing is defined for a given schema, the default will be returned. The config_entity will always
    # be the original config_entity, while the schema_config_entity will be the parent of the config_entity and the schema
    # will represent the parent.
    @property
    def parent_fixture(self):
        self._parent_fixture = self._parent_fixture or \
                               resolve_parent_fixture(self.module, self.module_fragment, self.base_class, self.schema, *self.args, **self.kwargs)
        if hasattr(self, 'schema_config_entity') and self.schema_config_entity and self._parent_fixture.config_entity == self.schema_config_entity:
            raise Exception("For fixture %s , the parent fixture of %s has the same config_entity %s" % (self, self._parent_fixture, self.config_entity))
        return self._parent_fixture

    @property
    def ancestor_config_entity(self):
        """
            Resolves the parent_config_entity for moving up the hierarchy.
            This uses the schema_config_entity if defined or else the config_entity, or else returns None
            schema_config_entity is used in case two or more levels of the hierarchy use the default_fixture.
            This allows us to track the current config_entity in the hierarchy with schema_config_entity but
            to retain config_entity in order to match the scope specified in certain individual fixtures.
        """
        if hasattr(self, 'schema_config_entity'):
            return self.schema_config_entity.parent_config_entity_subclassed
        if hasattr(self, 'config_entity'):
            return self.config_entity.parent_config_entity_subclassed
        return None

    def init_args(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def expect(self, *args):
        """
            Pass arg strings that are required by self to validate.
        :param args:
        :return:
        """
        # This is the utils version
        expect(self, *args)


class InitFixture(Fixture):
    module = None
    module_fragment = 'init'
    client = None

    @property
    def client_path(self):
        # The base pass of the client fixture
        return "{server_root}/footprint/client/configuration/{client}".format(
            server_root=settings.ROOT_PATH,
            client=self.client)


    @property
    def base_class(self):
        return InitFixture

    def import_database(self):
        """
            Optionally configure an import database for the client. The result dict is sent to import_data.ImportData
            dict(
                host=HOST_DB_IP
                database=DB_NAME
                user=DB_USER
                password=DB_PW)
        :return:
        """
        return None

    def model_class_modules(self):
        """
            Returns an array of tuples with each tuple in the form (module, module_fragment) where module is a string
            that indicates a module under initialization.client.[client], such as 'built_form' or 'presentation'.
            module_fragment is the name of the sub module without the client name, such as 'tilestache' to indicate
            [client]_tilestache under the presentation package
        :return:
        """
        return []

    def populate_models(self):
        pass

class ConfigEntitiesFixture(Fixture):
    module = 'config_entity'
    module_fragment = 'config_entities'

    @property
    def base_class(self):
        return ConfigEntitiesFixture

    def regions(self, region_keys=None, class_scope=None):
        return []

    def projects(self, region=None, region_keys=None, project_keys=None, class_scope=None):
        """
            Looks for the projects of the specified region or all regions of self.regions()
            Regions must already be saved to the database at this point.
        :param region:
        :return:
        """
        regions = [region] if region else map(lambda region: Region.objects.get(key=region['key']), self.regions())
        local_class_scope = class_scope
        def projects_of_region(region):
            class_scope = local_class_scope or region.schema()
            region_config_entities = resolve_fixture("config_entity", "config_entities", ConfigEntitiesFixture, class_scope)
            return region_config_entities.projects(region)

        return flat_map(lambda region: projects_of_region(region), regions)

    def scenarios(self, project=None, region_keys=None, project_keys=None, scenario_keys=None, class_scope=None):
        """
            Looks for the scenarios of the specified project or all projects of self.projects()
            Projects must already be saved to the database at this point.
            :param project Optional Project to specify to limit the scenarios returned to those whose project_key
            matches the project.key and to those who have no project_key
            :param class_scope Optional Scenario subclass by which to filter the fixtures according to the
                fixture's class_scope attribute
        :return: A list of scenario fixtures
        """
        local_class_scope = class_scope
        projects = [project] if project else map(lambda project: Project.objects.get(key=project['key']), self.projects())

        def scenarios_of_project(project):
            project_config_entities = resolve_fixture("config_entity", "config_entities", ConfigEntitiesFixture, local_class_scope or project.schema())
            return project_config_entities.scenarios(project, region_keys=region_keys, project_keys=project_keys, scenario_keys=scenario_keys, class_scope=class_scope)

        return flat_map(lambda project: scenarios_of_project(project), projects)

    def import_scenarios(self, origin_instance):
        return self.parent_fixture.import_scenarios(origin_instance)

    def default_config_entity_permissions(self, **kwargs):
        """
            A mapping of UserGroup keys to a PermissionKey
            This is defined in default_config_entities.py and in any fixture that needs to override
            the values for the ConfigEntities at or below the fixture's scope
        :param kwargs:
        :return:
        """
        parent_fixture = self.parent_fixture
        return parent_fixture.default_config_entity_permissions(**kwargs) if parent_fixture else {}

class BuiltFormFixture(Fixture):
    module = 'built_form'
    module_fragment = 'built_form'
    config_entity = None

    def expect_kwargs(self):
        return ['config_entity']

    @property
    def base_class(self):
        return BuiltFormFixture

    def built_forms(self):
        """
            Returns fully instantiated client-specific BuiltForm subclass instances plus the default ones.
        :return: A dictionary keyed by the BuiltForm subclass name or similar, valued by the instances
        """


    def built_form_sets(self):
        """
            Returns client specific BuiltFormSets as a dictionary of fixtures
        :return:
        """
        return []


    def built_form_styles(self):
        """
            Returns a symbology dict keyed by the name of a client-specific built_form to its color
            :return:
        """

    @staticmethod
    def construct_client_land_uses(client_built_form_class, prefix):

        land_use_symbology_fixture = resolve_fixture(
            "presentation",
            "land_use_symbology",
            LandUseSymbologyFixture,
            settings.CLIENT)
        land_use_color_lookup = land_use_symbology_fixture.land_use_color_lookup()

        def update_or_create_template(land_use_definition):
            logger.debug("creating template for landuse: {lu}".format(lu=land_use_definition.land_use))
            key = '%s__%s' % (prefix,
                              land_use_definition.land_use if isinstance(land_use_definition.land_use, int) else
                              slugify(str(land_use_definition.land_use)).replace('-', '_'))

            logger.debug("Land Use Key: {key}".format(key=key))

            built_form = client_built_form_class.objects.update_or_create(
                key=key,
                defaults=dict(
                    creator=get_user_model().objects.get(username=UserGroupKey.SUPERADMIN),
                    updater=get_user_model().objects.get(username=UserGroupKey.SUPERADMIN),
                    name=land_use_definition.land_use,
                    land_use_definition=land_use_definition,
                    ))[0]
            built_form.medium = client_built_form_class.update_or_create_built_form_layer_style(
                key,
                land_use_color_lookup.get(land_use_definition.land_use, None)
            )
            built_form.save()
        return map(
            update_or_create_template,
            client_built_form_class.objects.all())


class PolicyConfigurationFixture(Fixture):
    module = 'policy'
    module_fragment = 'policy'

    def policy_sets(self):
        pass

    @property
    def base_class(self):
        return PolicyConfigurationFixture


class ConfigEntityFixture(Fixture):
    """
        Base Class to configure DbEntities at a certain ConfigEntity scope (e.g. Project)
    """

    # The config_entity is required for default_db_entities, but not for feature_class_lookup
    config_entity = None

    def default_remote_db_entities(self):
        # A list of simple dictionaries containing a key, url and optional hosts array, that describe how to
        # configure a remote db_entity. If this method is not overridden, it simply delegates to the parent fixture
        is_own_parent = self.parent_fixture.__class__ == self.__class__
        return self.parent_fixture.default_remote_db_entities() if self.ancestor_config_entity and not is_own_parent else FixtureList([])

    def default_db_entities(self, **kwargs):
        """
            Creates client-specific db_entity_and_class configurations
            kwargs - overrides is a dict used to override values in the config. For instance:
                dict(Keys.DB_ABSTRACT_FEATURE=dict(name='Foo')) could be used to override the name of a DbEntitySetup.
            The usage of the overrides is up to the receiving method
        :return:
        """
        return self.parent_fixture.default_db_entities()

    def default_config_entity_groups(self, **kwargs):
        """
            Returns the base groups which should be used to create Groups specific to the
            given ConfigEntity
        :param kwargs:
        :return:
        """
        return self.parent_fixture.default_config_entity_groups(**kwargs)

    def default_db_entity_permissions(self, **kwargs):
        """
            Returns the a dict of default permissions for DbEntities of the owning ConfigEntity
            specified by self.config_entity. These permission also indicate the ability to
            CRUD the Features of the DbEntity, although the DbEntityPermissionKey.APPROVE
            limits who can approve the edit of a feature. Only approved features can be merged
            from a draft to master scenario. Permission to merge comes form ConfigEntityPermissionKey.MERGE
        :param kwargs:
        :return: The dict form matches that of DbEntity.group_permission_configuration. Keys
        are GroupKey strings and values are PermissionKey strings.
        Example: {UserGroupKey.ADMIN: PermissionKey.ALL, UserGroupKey.PLANNER: PermissionKey.VIEW}.
        All unspecified groups that are superior to one of those specified will be assigned
        the same permissions as their subordinate.
        """
        return self.parent_fixture.default_db_entity_permissions(**kwargs)

    def import_db_entity_configurations(self, **kwargs):
        return self.parent_fixture.import_db_entity_configurations(**kwargs)

    def feature_class_lookup(self):
        """
            A ConfigEntity-independent lookup of DbEntity keys to Feature classes. The same information is
            provided by default_db_entities but the latter is ConfigEntity instance-specific
        :return:
        """
        return dict()

    def non_default_owned_db_entities(self):
        """
            Return all DbEntities that are owned by this config_entity but not from this fixture, meaning they were created by the user
            or some kind of import process.
        """
        default_db_entities = self.default_db_entities()
        default_db_entity_keys = map(lambda db_entity: db_entity.key, default_db_entities)
        additional_db_entity_keys = set(map(lambda db_entity: db_entity.key, self.config_entity.owned_db_entities())) - set(default_db_entity_keys)
        return self.config_entity.computed_db_entities(key__in=additional_db_entity_keys)

    @property
    def parent_fixture(self):
        return super(ConfigEntityFixture, self).parent_fixture

    _parent_config_entity_fixture = None
    @property
    def parent_config_entity_fixture(self):
        """
            Returns the ConfigEntityFixture subclass of the parent_config_entity.
            This is different than parent_fixture, which returns the save ConfigEntityFixture subclass but moves up the schema hierarchy.
            For example, this method resaves a ProjectConfigEntityFixture for project foo of region bar to a RegionConfigEntityFixture of region bar
            parent_fixture resolves the same ProjectConfigEntityFixture to the ProjectConfigEntityFixture of region bar (if one is defined)
        """
        if self.config_entity:
            if self.ancestor_config_entity:
                self._parent_config_entity_fixture = self._parent_config_entity_fixture or \
                                   self.__class__.resolve_config_entity_fixture(self.ancestor_config_entity)
                return self._parent_config_entity_fixture
            else:
                return None
        else:
            # Use the parent_fixture if no config_entity is specified or we are at the GlobalConfig
            # The former case is for initialization only, before ConfigEntity instances have been created
            return self.parent_fixture


    @classmethod
    def resolve_config_entity_fixture(cls, config_entity):
        from footprint.main.models.config.scenario import Scenario
        from footprint.main.models.config.project import Project
        from footprint.main.models.config.region import Region
        from footprint.main.models.config.global_config import GlobalConfig
        if isinstance(config_entity, Scenario):
            module_fragment, subclass = ("scenario", ScenarioFixture)
        elif isinstance(config_entity, Project):
            module_fragment, subclass = ("project", ProjectFixture)
        elif isinstance(config_entity, Region):
            module_fragment, subclass = ("region", RegionFixture)
        elif isinstance(config_entity, GlobalConfig):
            module_fragment, subclass = ("global_config", GlobalConfigFixture)
        else:
            raise Exception("config_entity %s doesn't match an expected type" % config_entity)
        return resolve_fixture(
            "config_entity",
            module_fragment,
            subclass,
            config_entity.schema(),
            config_entity=config_entity)

class GlobalConfigFixture(ConfigEntityFixture):
    module = 'config_entity'
    module_fragment = 'global_config'

    @property
    def base_class(self):
        return GlobalConfigFixture


class RegionFixture(ConfigEntityFixture):
    module = 'config_entity'
    module_fragment = 'region'

    @property
    def base_class(self):
        return RegionFixture

class ProjectFixture(ConfigEntityFixture):
    module = 'config_entity'
    module_fragment = 'project'

    @property
    def base_class(self):
        return ProjectFixture

class ScenarioFixture(ConfigEntityFixture):
    module = 'config_entity'
    module_fragment = 'scenario'

    @property
    def base_class(self):
        return ScenarioFixture


class PresentationConfigurationFixture(Fixture):
    # Some calls will require putting a config_entity in scope via init, but not all
    config_entity = None

    # Subclasses can override this to setup media. Then specific fixture classes can override
    # it to provide defaults.
    #This is only used by Result and not by Layer
    def update_or_create_media(self, config_entity, db_entity_keys=None):
        if self.parent_fixture:
            return self.parent_fixture.update_or_create_media(config_entity, db_entity_keys)

class LayerConfigurationFixture(PresentationConfigurationFixture):
    module = 'presentation'
    module_fragment = 'layer'

    @property
    def base_class(self):
        return LayerConfigurationFixture

    def layer_libraries(self, layers=None):
        """
            Creates a PresentationConfiguration instance used to configure a LayerLibrary for a certain ConfigEntity
            class scope
        :param layers override the layers
        :return:
        """
        pass

    def layers(self):
        """
            A list of LayerConfiguration instances that configure visible layers based on db_entities. This
            function should merge in the result of background_layers.
        :return: An array of LayerConfigurations with the background_layers merged in
        """
        return []

    def background_layers(self):
        """
            A subset of layers used as background layers. These are also LayerConfigurations
        :return: An Array of LayerConfigurations
        """
        return []

    def import_layer_configurations(self, geometry_type):
        """
            Generic LayerConfigurations (no db_enity_key) that are used for the layers of imported
            db_entities/features tables.
            :param geometry_type:
        """
        return []

    def update_or_create_layer_style(self, config_entity, layer_configuration, layer):
        """
            Creates the LayerStyle of the layer
        :param config_entity:
        :param layer_configuration:
        :return:
        """
        return self.parent_fixture.update_or_create_layer_style(config_entity, layer_configuration, layer)

class LandUseSymbologyFixture(Fixture):
    module='presentation'
    module_fragment='land_use_symbology'

    @property
    def base_class(self):
        return LandUseSymbologyFixture

    def land_use_color_lookup(self):
        """
            Maps an attribute of a client-specific class to a color.
        :return:
        """
        return dict()

class ResultConfigurationFixture(PresentationConfigurationFixture):
    """
        Fixtures related to result presentations, such as ResultLibrary and Result instances
    """
    module='presentation'
    module_fragment='result'

    # TODO this doesn't belong in here
    @property
    def employment_breakdown_query(self):
        return 'SELECT SUM(emp_ret) as emp_ret__sum, '\
            'SUM(emp_off) as emp_off__sum, '\
            'SUM(emp_ind + emp_ag) as emp_ind__sum, '\
            'SUM(emp_pub) as emp_pub__sum, '\
            'SUM(emp_military) as emp_military__sum FROM %({0})s'.format

    @property
    def base_class(self):
        return ResultConfigurationFixture

    def result_libraries(self):
        """
            Returns the ResultLibrary configurationsscoped for the class of self.config_entity
        :return:
        """
        return self.parent_fixture.result_libraries()

    def results(self):
        """
            Returns ResultConfiguration instances. These configure a Result that is created for each config_entity
            whose scope matches or inherits that the ResultConfiguration.class_scope
        :return:
        """
        return self.parent_fixture.results()

    @staticmethod
    def simple_aggregate(result_config):
        return [
            # self.aggregate(Sum('column1'), ...)
            ('aggregate', map(
                lambda attribute: dict(Sum=result_config.db_column_lookup[attribute]),
                result_config.attributes))
        ]

# This is more of a literal fixture.
class MediumFixture(Fixture):
    def __init__(self, *args, **kwargs):
        super(MediumFixture, self).__init__('global', *args, **kwargs)

    def expect_kwargs(self):
        return ['key', 'name']

class AnalysisModuleFixture(Fixture):
    def default_analysis_module_configurations(self, **kwargs):
        return self.parent_fixture.default_analysis_module_configurations(**kwargs)

class BehaviorFixture(Fixture):
    """
        Base class for defining Behavior fixtures
    """

    def behaviors(self, **kwargs):
        """
            Override to define Behavior fixtures.
            By default this delegates to the parent fixture if one exists
        """
        return self.parent_fixture.behaviors() if self.ancestor_config_entity else []

class AttributeGroupFixture(Fixture):
    """
        Base class for defining AttributeGroup fixtures
    """
    def expect_kwargs(self):
        return []

    def attribute_groups(self, **kwargs):
        """
            Override to define AttributeGroup fixtures.
            By default this delegates to the parent fixture if one exists
        """
        return self.parent_fixture.behaviors() if self.ancestor_config_entity else []

class UserFixture(Fixture):
    """
        Base class for defining User and Group fixtures
    """
    def users(self, **kargs):
        """
            returns a list of dicts in the form
            dict(username=UserGroupKey.X, group=UserGroupKey.X, password='x', email='x'),
            where the username becomes the User.username and the group is the Group.name
            of the Group to join
        """
        return []

    def groups(self, **kargs):
        """
            returns a list of dicts in the form
            dict(name=UserGroupKey.X, superiors=[UserGroupKey.X]),
            where the name is the name to use for the group and superiors
            are the names of pre-existing groups connected with the GroupHierarchy class
            superiors exist to inherit the highest permission among their inferiors.
            This way intermediate group permissions don't needed to be explicitly declared
        """
        return []

def region_fixtures(**kwargs):
    """
        Convenience method to fetch all region features of a client. Normally there is only one
    """
    return unique(map(
        lambda schema: resolve_fixture("config_entity", "region", RegionFixture, schema, **kwargs),
        region_schemas_of_client()), lambda fixture: fixture.__class__)

def project_specific_project_fixtures(**kwargs):
    """
        Convenience method to find ProjectFixture instances for all projects of the client.
        :kwargs: Optional arguments for resolve_fixture, such as the config_entity
    :return:
    """
    return unique(map(
        lambda schema: resolve_fixture("config_entity", "project", ProjectFixture, schema, **kwargs),
        project_schemas_of_client()), lambda fixture: fixture.__class__)

def project_specific_scenario_fixtures(**kwargs):
    """
        Convenience method to find ScenarioFixture instances for all projects of the client.
        :kwargs: Optional arguments for result_fixture, such as the config_entity
    :return:
    """
    return unique(map(
        lambda schema: resolve_fixture("config_entity", "scenario", ScenarioFixture, schema, **kwargs),
        project_schemas_of_client()), lambda fixture: fixture.__class__)

def region_schemas_of_client(**kwargs):
    """
        All region schemas of the client. Normally there is only one
    """
    client_config_entities = resolve_fixture("config_entity", "config_entities", ConfigEntitiesFixture, settings.CLIENT, **kwargs)
    return map(lambda region_config: '%s__%s' % (client_config_entities.schema, region_config['key']), client_config_entities.regions())

def project_schemas_of_client(**kwargs):
    """
        Extract all the schemas under of the settings.CLIENT in [client]_config_entities.project
        :kwargs: Optional arguments for result_fixture, such as the config_entity
    :return:
    """
    client_config_entities = resolve_fixture("config_entity", "config_entities", ConfigEntitiesFixture, settings.CLIENT, **kwargs)
    return map(lambda project_config: '%s__%s' % (client_config_entities.schema, project_config['key']), client_config_entities.projects())
