
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

from tastypie.constants import ALL_WITH_RELATIONS, ALL
from tastypie.fields import CharField
from tastypie import fields

from footprint.main.models.config.project import Project
from footprint.main.models.config.region import Region
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.scenario import Scenario
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.config.scenario import BaseScenario, FutureScenario
from footprint.main.resources.behavior_resources import BehaviorResource
from footprint.main.resources.medium_resources import MediumResource
from footprint.main.resources.mixins.editor_resource_mixin import EditorResourceMixin
from footprint.main.resources.mixins.permission_resource_mixin import PermissionResourceMixin
from footprint.main.resources.model_dict_field import ModelDictField
from footprint.main.resources.mixins.mixins import PolicySetsResourceMixin, BuiltFormSetsResourceMixin, DbEntityResourceMixin, PresentationResourceMixin, CategoryResourceMixin, \
    CloneableResourceMixin
from footprint.main.resources.footprint_resource import FootprintResource
from footprint.main.resources.user_resource import UserResource


__author__ = 'calthorpe_analytics'


class CustomModelDictField(ModelDictField):
    def key_dehydrate_override(self):
        return {'db_entities': 'db_entities'}

    def instance_dehydrate_override(self):
        return {'db_entities':
                lambda config_entity, db_entity: config_entity.dbentityinterest_set.filter(db_entity=db_entity)[0]
        }

    def key_hydrate_override(self):
        return {'db_entities': 'db_entities'}

    def instance_hydrate_override(self):
        return {'db_entities': lambda config_entity, db_entity_interest: db_entity_interest.db_entity}


class ConfigEntityResource(FootprintResource,
                           PolicySetsResourceMixin,
                           BuiltFormSetsResourceMixin,
                           DbEntityResourceMixin,
                           PresentationResourceMixin,
                           CategoryResourceMixin,
                           CloneableResourceMixin,
                           PermissionResourceMixin,
                           EditorResourceMixin):

    def get_object_list(self, request):
        return self.permission_get_object_list(request, super(ConfigEntityResource, self).get_object_list(request))

    media = fields.ToManyField(MediumResource, 'media', full=False, null=True)
    # These should never be written, they are calculated automatically
    behavior = fields.ToOneField(BehaviorResource, 'behavior', full=False, null=True)
    creator = fields.ToOneField(UserResource, 'creator', full=True, null=True, readonly=True)
    updater = fields.ToOneField(UserResource, 'updater', full=True, null=True)

    # The GroupHierarchies associated with the ConfigEntity. This is a reverse relationship and is thus readonly
    # groups_map = lambda bundle: Group.objects.filter(group_hierarchy__in=bundle.obj.group_hierarchies.all())
    # groups = fields.ToManyField(GroupResource, attribute=groups_map, readonly=True)

    schema = CharField(attribute='schema', readonly=True)
    scope = CharField(attribute='scope', readonly=True)
    # The client of the ConfigEntity. client is the top-level region in the ConfigEntity's ancestry.
    # Thus GlobalConfig has no client
    client = CharField(attribute='client', readonly=True, null=True)
    _content_type_ids = None
    _perm_ids = None

    def hydrate(self, bundle):
        """
            Set the user who created the ConfigEntity
        :param bundle:
        :return:
        """
        if not bundle.obj.id:
            bundle.obj.creator = self.resolve_user(bundle.request.GET)
            # Mark the ConfigEntity as incomplete if new. This will be 100 after the post-save finished
            bundle.obj.setup_percent_complete = 0
            bundle.obj.updater = self.resolve_user(bundle.request.GET)
        return super(ConfigEntityResource, self).hydrate(bundle)


    class Meta(FootprintResource.Meta):
        abstract = True
        always_return_data = True
        queryset = ConfigEntity.objects.filter(deleted=False)
        resource_name = 'config_entity'
        filtering = {
            # Accept the parent_config_entity to limit the ConfigEntity instances to a certain id
            # (i.e. parent_config_entity__id=n)
            "parent_config_entity": ALL_WITH_RELATIONS,
            "id": ALL,
            "name": ("exact",)
        }


class GlobalConfigResource(ConfigEntityResource):
    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = GlobalConfig.objects.filter(deleted=False)
        resource_name = 'global_config'


class RegionResource(ConfigEntityResource):
    parent_config_entity = fields.ToOneField(ConfigEntityResource, 'parent_config_entity', full=False)

    class Meta(ConfigEntityResource.Meta):
        always_return_data = True
        # Hack to block Client level region
        queryset = Region.objects.filter(deleted=False)
        resource_name = 'region'


class ProjectResource(ConfigEntityResource):
    parent_config_entity = fields.ToOneField(RegionResource, 'parent_config_entity', full=False)

    class Meta(ConfigEntityResource.Meta):
        always_return_data = True
        queryset = Project.objects.filter(deleted=False)
        resource_name = 'project'


class ScenarioResource(ConfigEntityResource):
    parent_config_entity = fields.ToOneField(ProjectResource, 'parent_config_entity', full=False)

    class Meta(ConfigEntityResource.Meta):
        abstract = False
        always_return_data = True
        queryset = Scenario.objects.filter(deleted=False)
        resource_name = 'scenario'


class BaseScenarioResource(ScenarioResource):
    parent_config_entity = fields.ToOneField(ProjectResource, 'parent_config_entity', full=False)

    class Meta(ConfigEntityResource.Meta):
        always_return_data = True
        queryset = BaseScenario.objects.filter(deleted=False)
        resource_name = 'base_scenario'


class FutureScenarioResource(ScenarioResource):
    parent_config_entity = fields.ToOneField(ProjectResource, 'parent_config_entity', full=False)

    class Meta(FootprintResource.Meta):
        always_return_data = True
        # Don't ever load deleted ConfigEntities or those that didn't complete cloning post save
        queryset = FutureScenario.objects.filter(deleted=False, setup_percent_complete=100)
        resource_name = 'future_scenario'
