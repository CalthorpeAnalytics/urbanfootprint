
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


from django.conf.urls import include, url, patterns
from django.views.generic import TemplateView
from django.conf import settings

from tastypie.api import Api
from footprint.main.admin.views import ufadmin, config_entities
from footprint.main.publishing.data_export_publishing import export_layer, get_export_result, export_query_results, \
    export_query_summary, export_result_table
from footprint.main.resources.analysis_module_resource import AnalysisModuleResource
from footprint.main.resources.analysis_tool_resource import AnalysisToolResource
from footprint.main.resources.behavior_resources import BehaviorResource, FeatureBehaviorResource, IntersectionResource, \
    JoinTypeResource, GeographicIntersectionResource, AttributeIntersectionResource
from footprint.main.resources.built_form_resources import BuiltFormResource, BuiltFormSetResource, PlacetypeResource, \
    PlacetypeComponentResource, BuildingUseDefinitionResource, \
    BuildingUsePercentResource, BuildingAttributeSetResource, BuiltFormExampleResource, \
    PlacetypeComponentPercentResource, PrimaryComponentResource, PrimaryComponentPercentResource, \
    PlacetypeComponentCategoryResource, BuildingResource, BuildingTypeResource, UrbanPlacetypeResource, CropResource, \
    CropTypeResource, LandscapeTypeResource, AgricultureAttributeSetResource

from footprint.main.resources.category_resource import CategoryResource, DbEntityCategoryResource, \
    ConfigEntityCategoryResource
from footprint.main.resources.client.client_land_use_definition_resource import ClientLandUseDefinitionResource


from footprint.main.resources.config_entity_resources import GlobalConfigResource, RegionResource, ProjectResource, \
    ScenarioResource, ConfigEntityResource, FutureScenarioResource, BaseScenarioResource
from footprint.main.resources.db_entity_resources import DbEntityResource
from footprint.main.resources.environmental_constraint_resources import EnvironmentalConstraintUpdaterToolResource, \
    EnvironmentalConstraintPercentResource

from footprint.main.resources.feature_resources import FeatureResource, FeatureVersionResource, TemplateFeatureResource, \
    FeatureCategoryAttributeResource, FeatureQuantitativeAttributeResource
from footprint.main.resources.flat_built_form_resource import FlatBuiltFormResource
from footprint.main.resources.group_hierarchy_resource import GroupHierarchyResource
from footprint.main.resources.layer_resources import LayerResource, LayerLibraryResource
from footprint.main.resources.layer_selection_resource import LayerSelectionResource
from footprint.main.resources.medium_resources import MediumResource, LayerStyleResource
from footprint.main.resources.merge_resources import MergeUpdaterToolResource
from footprint.main.resources.policy_resources import PolicyResource, PolicySetResource
from footprint.main.resources.presentation_medium_resource import PresentationMediumResource
from footprint.main.resources.presentation_resources import PresentationResource
from footprint.main.resources.result_resources import ResultLibraryResource, ResultResource
from footprint.main.resources.revision_resource import RevisionResource
from footprint.main.resources.tag_resource import TagResource, BuiltFormTagResource, DbEntityTagResource
from footprint.main.resources.user_resource import GroupResource
from footprint.main.resources.user_resource import UserResource
from footprint.main.user_management.views import users, user, add_user, login, logout
from tilestache_uf.views import vectors
from footprint.upload_manager.views import upload, upload_test, upload_results
from footprint.main.views import get_project_data, get_scenario_data

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='footprint/index.html')),
    url(r'^(?P<api_key>[^/]+)/export_layer/(?P<layer_id>[^/]+)', export_layer),
    url(r'^(?P<api_key>[^/]+)/get_export_result/(?P<hash_id>[^/]+)', get_export_result),
    url(r'^(?P<api_key>[^/]+)/export_query_results/(?P<layer_selection_unique_id>[^/]+)', export_query_results),
    url(r'^(?P<api_key>[^/]+)/export_query_summary/(?P<layer_selection_unique_id>[^/]+)', export_query_summary),
    url(r'^(?P<api_key>[^/]+)/export_result_table/(?P<result_id>[^/]+)', export_result_table),

    # User Management
    url(r'^users/$', users),
    url(r'^user/(?P<user_id>\d*)', user),
    url(r'^add_user/$', add_user),

    # Authentication
    url(r'^logout/$', logout),
    url(r'^login/$', login),

    # GeoJSON selection tiles
    url(r'^vectors/(?P<layer_key>layer:\d*,attr_id:\d*,type:selection).geojson', vectors),

    # Administration
    url(r'^ufadmin/', include('footprint.main.admin.urls')),

    # File Upload
    url(r'^upload/', upload),
    url(r'^upload_test/', upload_test),
    url(r'^upload_results/', upload_results),

    # Manual API urls
    url(r'^api/v2/project/', get_project_data),
    url(r'^api/v2/scenario/', get_scenario_data),
)

# All tastypie resources need to be listed here
v1_api = Api(api_name="v{0}".format(settings.API_VERSION))
v1_api.register(UserResource())
v1_api.register(GroupResource())
v1_api.register(GroupHierarchyResource())
v1_api.register(ConfigEntityResource())
v1_api.register(GlobalConfigResource())
v1_api.register(RegionResource())
v1_api.register(ProjectResource())
v1_api.register(ScenarioResource())
v1_api.register(FutureScenarioResource())
v1_api.register(BaseScenarioResource())
v1_api.register(DbEntityResource())

v1_api.register(PlacetypeResource())
v1_api.register(PlacetypeComponentResource())
v1_api.register(PlacetypeComponentCategoryResource())
v1_api.register(PlacetypeComponentPercentResource())
v1_api.register(PrimaryComponentResource())
v1_api.register(PrimaryComponentPercentResource())

v1_api.register(BuildingUseDefinitionResource())
v1_api.register(BuildingUsePercentResource())
v1_api.register(BuildingAttributeSetResource())
v1_api.register(BuiltFormSetResource())
v1_api.register(BuiltFormExampleResource())
v1_api.register(BuiltFormResource())

v1_api.register(EnvironmentalConstraintUpdaterToolResource())
v1_api.register(EnvironmentalConstraintPercentResource())
v1_api.register(MergeUpdaterToolResource())

v1_api.register(BuildingResource())
v1_api.register(BuildingTypeResource())
v1_api.register(UrbanPlacetypeResource())

v1_api.register(AgricultureAttributeSetResource())
v1_api.register(CropResource())
v1_api.register(CropTypeResource())
v1_api.register(LandscapeTypeResource())

v1_api.register(PolicyResource())
v1_api.register(PolicySetResource())

v1_api.register(PresentationResource())
v1_api.register(LayerLibraryResource())
v1_api.register(ResultLibraryResource())

v1_api.register(MediumResource())
v1_api.register(LayerStyleResource())

v1_api.register(PresentationMediumResource())
v1_api.register(LayerResource())
v1_api.register(LayerSelectionResource())

v1_api.register(ResultResource())

v1_api.register(CategoryResource())
v1_api.register(ConfigEntityCategoryResource())
v1_api.register(DbEntityCategoryResource())
v1_api.register(TagResource())
v1_api.register(BuiltFormTagResource())
v1_api.register(DbEntityTagResource())

#Built Form Resources
v1_api.register(ClientLandUseDefinitionResource())
v1_api.register(FlatBuiltFormResource())

v1_api.register(FeatureResource())
v1_api.register(TemplateFeatureResource())
v1_api.register(FeatureCategoryAttributeResource())
v1_api.register(FeatureQuantitativeAttributeResource())
v1_api.register(AnalysisModuleResource())
v1_api.register(AnalysisToolResource())
v1_api.register(FeatureBehaviorResource())
v1_api.register(IntersectionResource())
v1_api.register(GeographicIntersectionResource())
v1_api.register(AttributeIntersectionResource())
v1_api.register(JoinTypeResource())
v1_api.register(BehaviorResource())
v1_api.register(RevisionResource())
v1_api.register(FeatureVersionResource())

# Django Rest API
urlpatterns += patterns(
    '',
    (r'^api/', include(v1_api.urls)),
)

# Cross-domain proxying if we need it
#urlpatterns += patterns('',
#    (r'^(?P<url>.*)$', 'httpproxy.views.proxy'),
#)
#urlpatterns += staticfiles_urlpatterns() #this is meant for debug only

#from celery.task import PingTask
#from djcelery import views as celery_views

#celery webhook
#urlpatterns += patterns("",
#    url(r'^apply/(?P<task_name>.+?)/', celery_views.apply),
#    url(r'^ping/', celery_views.task_view(PingTask)),
#    url(r'^(?P<task_id>[\w\d\-]+)/done/?$', celery_views.is_task_successful,
#        name="celery-is_task_successful"),
#    url(r'^(?P<task_id>[\w\d\-]+)/status/?$', celery_views.task_status,
#        name="celery-task_status"),
#)
