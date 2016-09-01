
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


# Mixin that marks a resource class as needing dynamic subclassing because the model class it models needs dynamic subclassing
import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from footprint.main.lib.functions import remove_keys, merge
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.config.scenario import FutureScenario, BaseScenario
from footprint.main.resources.footprint_resource import FootprintResource
logger = logging.getLogger(__name__)

class DynamicResource(FootprintResource):

    class Meta(FootprintResource.Meta):
        pass

    def create_subclass(self, params, **kwargs):
        """
            Returns a subclass of self based on the given parameters. For example a CanvasFeatureResource will subclass
            itself based on the value of the 'config_entity_id' in params
        :param params:
        :return:
        """
        raise Exception("Must implement create_subclass")

    def resolve_model_class(self, **kwargs):
        """
            Resolve the resource's underlying dynamic model based on the kwargs
        """
        raise Exception("Must implement resolve_model_class")

    def resolve_config_entity(self, params):
        """
            Resolves the config_entity based on the layer id indicated in the param
        :param params:
        :return:
        """

        # TODO hack to handle lack of multi-level subclass relation resolution
        scenarios = FutureScenario.objects.filter(id=int(params['config_entity__id']))
        if len(list(scenarios)) > 0:
            # Scenario subclass instance
            return scenarios[0]
        else:
            scenarios = BaseScenario.objects.filter(id=int(params['config_entity__id']))
            if len(list(scenarios)) > 0:
                return scenarios[0]
            else:
                return ConfigEntity.objects.filter(id=int(params['config_entity__id'])).all().select_subclasses()[0]

    def resolve_layer(self, params):
        """
            The Layer id is used to resolve the type of Feature (via its DbEntity)
        :param params:
        :return:
        """
        return Layer.objects.get(id=params['layer__id'])

    def subclass_resource_if_needed(self, view, request):
        """
            Overrides the FootprintResource method to perform subclassing of the resource based on the request params
        :param view:
        :param request:
        :return:
        """
        params = request.GET
        # TODO cache dynamic class creation results
        # Create the dynamic resource class
        dynamic_resource_class = self.create_subclass(params, method=request.method)
        # Dynamic model classes always have a config_entity. In the case
        # where the model class is not dynamic (e.g. ClientLandUseDefinitions subclasses),
        # we expect the config_entity__id to be sent with the request, so we thusly resolve the config_entity
        config_entity = dynamic_resource_class._meta.queryset.model.config_entity if\
            hasattr(dynamic_resource_class._meta.queryset.model, 'config_entity') else\
            self.resolve_config_entity(request.GET)

        # This might not be need anymore, but it indicates what other dynamic classes were created so that
        # permissions can be added for them
        additional_classes_used = []
        # We add permissions to the current user so they can access these dynamic classes if it's the first access by the user
        # TODO permissions would ideally be done ahead of time, of if we could automatically give the user full access to all. This might be fixed in the latest Django version
        # subclasses of a certain type, but I don't see how to do that in the Django docs
        user = self.resolve_user(params)
        #logger.info("Adding permissions for user %s to dynamic_resource_class %s" % (user.username, dynamic_resource_class.__name__))
        self.add_permissions_to_user(user, self.get_or_create_permissions_for_class(dynamic_resource_class, additional_classes_used, config_entity))

        # Extract and add GET parameters
        request._config_entity = config_entity
        request._filters = remove_keys(
            merge(request.GET, self.search_params(params)),
            self.remove_params(params))

        return dynamic_resource_class().wrap_view(view)

    def search_params(self, params):
        """
        :param params
        :return: return the modified params_copy
        """
        return {}

    def remove_params(self, params):
        """
        :return: a string list of parameters to remove
        """
        return []

    def get_or_create_permissions_for_class(self, DynamicResourceClass, additional_classes_used, config_entity):
        model_class = DynamicResourceClass.Meta.object_class
        for clazz in [model_class] + additional_classes_used:
            return map(lambda action: Permission.objects.get_or_create(
                codename='{0}_{1}'.format(action, clazz.__name__.lower()),
                # Since our dynamic model doesn't have a ContentType, borrow that of the ConfigEntity
                content_type_id=ContentType.objects.get(app_label="main", model=config_entity.__class__.__name__.lower()).id,
                # 50 is the name limit
                name='Can {0} {1}'.format(action, clazz.__name__)[-50:])[0],
                       ['add', 'change', 'delete'])

    def add_permissions_to_user(self, user, permissions):
        existing = user.user_permissions.all()
        new_permissions = filter(lambda permission: permission not in existing, permissions)
        user.user_permissions.add(*new_permissions)

    def dynamic_resource_subclass(self, **kwwargs):
        """
            Subclasses may implement this to create a dynamic resource subclass of the
            abstract resource subclass
        :return:
        """
        pass
