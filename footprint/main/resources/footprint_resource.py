
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
import traceback
from collections import defaultdict
from django import http
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Field
from django.http import HttpResponse
from django.utils.timezone import is_naive
from tastypie.authentication import ApiKeyAuthentication
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest
from tastypie.authorization import DjangoAuthorization
from tastypie import fields
from tastypie.contrib.gis.resources import ModelResource
from tastypie.http import HttpAccepted
from tastypie.models import ApiKey
from tastypie.resources import csrf_exempt
from tastypie.utils.mime import build_content_type

from footprint.main.lib.functions import map_dict_to_dict, merge, map_dict
from footprint.main.utils.dynamic_subclassing import get_dynamic_resource_class
from footprint.main.utils.model_utils import limited_api_fields
from footprint.main.utils.subclasses import match_subclasses
from footprint.main.utils.utils import clear_many_cache, has_explicit_through_class, foreign_key_field_of_related_class
from tastypie.serializers import Serializer

logger = logging.getLogger(__name__)
__author__ = 'calthorpe_analytics'


class FootprintSerializer(Serializer):
    def format_datetime(self, data):
        """
        Our own serializer to format datetimes in ISO 8601 but with timezone
        offset.
        """
        # If naive or rfc-2822, default behavior...
        if is_naive(data) or self.datetime_formatting == 'rfc-2822':
            return super(FootprintSerializer, self).format_datetime(data)
        # Remove the pesky 6 digits of microseconds, javascript can't handle it
        return data.replace(microsecond=0).isoformat()


class FootprintHttpAccepted(HttpAccepted):
    def __init__(self, content='', mimetype=None, status=None, content_type=None, objects=None):
        super(FootprintHttpAccepted, self).__init__(content, mimetype, status, content_type)
        self.objects = objects


class FootprintResource(ModelResource):
    """
        Adds django revision with the tastypie ModelResource
    """
    def full_hydrate(self, bundle):
        """
        Given a populated bundle, distill it and turn it back into
        a full-fledged object instance.
        """
        if bundle.obj is None:
            bundle.obj = self._meta.object_class()

        bundle = self.hydrate(bundle)

        for field_name, field_object in self.fields.items():
            if field_object.readonly is True:
                continue

            # Check for an optional method to do further hydration.
            method = getattr(self, "hydrate_%s" % field_name, None)

            if method:
                bundle = method(bundle)

            if field_object.attribute:
                value = field_object.hydrate(bundle)

                # NOTE: We only get back a bundle when it is related field.
                if isinstance(value, Bundle) and value.errors.get(field_name):
                    bundle.errors[field_name] = value.errors[field_name]

                if value is not None or field_object.null:
                    # We need to avoid populating M2M data here as that will
                    # cause things to blow up.
                    if not getattr(field_object, 'is_related', False):
                        setattr(bundle.obj, field_object.attribute, value)
                    elif not getattr(field_object, 'is_m2m', False):
                        if value is not None:
                            try:
                                setattr(bundle.obj, field_object.attribute, value.obj)
                            except AttributeError:
                                raise Exception("Can't set attribute %s" % field_object.attribute)
                        elif field_object.blank:
                            continue
                        elif field_object.null:
                            try:
                                setattr(bundle.obj, field_object.attribute, value)
                            except:
                                raise Exception("Can't set attribute %s" % field_object.attribute)
        return bundle

    # Class level logger
    logger = logging.getLogger(__name__)

    def __init__(self):
        # Get an instance of a logger for the instance
        self.logger = logging.getLogger(__name__)
        super(FootprintResource, self).__init__()

    class Meta(object):
        always_return_data = True
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = FootprintSerializer()

    # From http://django-tastypie.readthedocs.org/en/latest/cookbook.html
    def dispatch(self, request_type, request, **kwargs):

        try:
            self._resource_cache = {}
            self._cache_hits = defaultdict(int)
            if request.method in ['POST', 'PATCH']:
                self.pre_save(request, **kwargs)

            response = super(ModelResource, self).dispatch(request_type, request, **kwargs)
            if request.method in ['POST', 'PATCH']:
                self.post_save(request, response, **kwargs)
        except (BadRequest, fields.ApiFieldError) as e:
            self.logger.exception(
                'Response 400 %s' % e.args[0])
            raise
        except ValidationError as e:
            self.logger.exception(
                'Response 400 %s' % e.messages)
            raise
        except Exception as e:
            if hasattr(e, 'response'):
                self.logger.exception(
                    'Response %s %s %s' %
                    (e.response.status_code, e.response.content, traceback.format_exc()))
            else:
                self.logger.exception('Response 500: %s' % e.message)
            raise
        finally:
            hits = sum(self._cache_hits.itervalues())
            if hits:
                self.logger.info('Got %d hits across %d queries from resource bundle caching', hits, len(self._cache_hits))
            del self._resource_cache
            del self._cache_hits

        return response

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        Extracts the common "which-format/serialize/return-response" cycle.

        Mostly a useful shortcut/hook.

        Overridden to include the original bundle, which is normally discard at this point
        """
        if response_class == HttpAccepted:
            response_class = FootprintHttpAccepted
        else:
            return super(FootprintResource, self).create_response(request, data, response_class, **response_kwargs)

        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        objects = map(lambda bundle: bundle.obj, data.get('objects'))
        return response_class(content=serialized, content_type=build_content_type(desired_format),
                              **merge(response_kwargs,
                                      dict(objects=objects) if response_class == FootprintHttpAccepted else dict()))

    def get_resource_uri(self, bundle_or_obj=None, url_name='api_dispatch_list'):
        # Hand-roll the URI when we can as it turns out to be very expensive to look up every time.
        if hasattr(bundle_or_obj, 'obj'):
            obj = bundle_or_obj.obj
        else:
            obj = bundle_or_obj
        if obj is not None:
            id = getattr(obj, 'id', None)
            if id is None:
                id = getattr(obj, 'pk', None)
        if obj is None or id is None:
            uri = super(FootprintResource, self).get_resource_uri(bundle_or_obj=bundle_or_obj, url_name=url_name)
        else:
            uri = '/footprint/api/{api_name}/{resource_name}/{id}/'.format(
                api_name=self._meta.api_name,
                resource_name=self._meta.resource_name,
                id=id)
        return uri

    def full_dehydrate(self, bundle, for_list=False):
        if hasattr(self, '_resource_cache'):
            bundle._resource_cache = self._resource_cache
            bundle._cache_hits = self._cache_hits

        return super(FootprintResource, self).full_dehydrate(bundle, for_list=for_list)

    def save_m2m(self, bundle):
        """
            Overrides the super method in order to handle saving many-to-many collection instances of an explicit through class. For some reason tastypie has no handling for this, but we want to deliver the through class instances to the user that have references to the related attribute (e.g. DbEntityInterest instances are delivered and each has a reference to DbEntity). We also want to allow the client to modify, add, and remove these instances. Thus we must intercept them here and save them properly. Tastypie assumes non-explict Through classes and just dumbly tries to add them to the related field with add(), which fails for explicitly through classes.
        :param bundle:
        :return:
        """
        # This is an exact copy of the super method up until the add() line
        for field_name, field_object in self.fields.items():
            if not getattr(field_object, 'is_m2m', False):
                continue

            if not field_object.attribute:
                continue

            if field_object.readonly:
                continue

            # Get the manager.
            related_mngr = None

            if isinstance(field_object.attribute, basestring):
                related_mngr = getattr(bundle.obj, field_object.attribute)
            elif callable(field_object.attribute):
                related_mngr = field_object.attribute(bundle)

            if related_mngr is None:
                continue

                # This condition is an enhancement to the super method. It allows an add method defined on the field to indicate how to add the many-to-many items
                # We don't use this since our items are handled more carefully below
                #if hasattr(related_mngr, 'clear'):
                # Clear it out, just to be safe.
            #    related_mngr.clear()

            existing_related_objs = related_mngr.all()
            related_objs_to_add = []

            # TODO handle remove and clear
            if hasattr(field_object, 'add'):
                # This condition is an enhancement to the super method.
                # It allows an add method defined on the field to indicate how to add the many-to-many items
                related_objs_to_add = map(lambda bundle: bundle.obj, bundle.data[field_name])
                # Call the custom defined add
                field_object.add(bundle, *related_objs_to_add)
                related_objs_to_remove = list(set(existing_related_objs)-set(related_objs_to_add))
                # Optionally call remove. The add function might take care of removing existing instances instead
                if hasattr(field_object, 'remove') and hasattr(field_object.remove, '__call__'):
                    field_object.remove(bundle, *related_objs_to_remove)
            else:
                explicit_through_class = has_explicit_through_class(bundle.obj, field_object.instance_name)
                if explicit_through_class:
                    to_model_attr = foreign_key_field_of_related_class(related_bundle.obj.__class__, bundle.obj.__class__).name,
                existing_related_objs = related_mngr.all()
                for related_bundle in bundle.data[field_name]:
                    # This if statement is a change from the super method. If we are handling explict through instances we need to give the incoming instance a reference to the bundle.obj. The through instances are never dehydrated with this reference since it simply refers back to the container (bundle.data)
                    if explicit_through_class:
                        # Set one side of the relationship to bundle.obj. This might have already been done on the client, but this overrides
                        setattr(
                            related_bundle.obj,
                            # Figure out the correct field
                            to_model_attr,
                            bundle.obj)
                    # Save the relatedd instance instance no matter what if the toMany relationship is full
                    # We never want to save references because nothing can be changed in
                    # the toMany reference except membership in the toMany
                    if field_object.full:
                        related_bundle.obj.save()
                    # Create a list of objects to add to the manager
                    related_objs_to_add.append(related_bundle.obj)
                # Create the set of objects to remove (ones that existed but weren't in the incoming related_bundle)
                related_objs_to_remove = list(set(existing_related_objs)-set(related_objs_to_add))
                # If we are handling explict through instances the save above is adequate. We don't want to try to add the item to the manager.
                # These methods are thus only for implicit related fields (no explicit through class)
                if hasattr(related_mngr, 'add'):
                    related_mngr.add(*related_objs_to_add)
                if hasattr(related_mngr, 'remove'):
                    related_mngr.remove(*related_objs_to_remove)

    def wrap_view(self, view):
        """
            Overrides wrap_view to allow processing of dynamic resource classes. Special parameters such as config_entity_id are used to resolve the correct resource subclass.
        :param view:
        :return:
        """
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            # Dynamic resources based on a ConfigEntity instance need to pass the config_entity__id so that we can properly construct the dynamic resource
            if hasattr(self.Meta, 'abstract') and self.Meta.abstract:
                wrapped_view = self.subclass_resource_if_needed(view, request)
                # During the subclassing process we may have removed parameters needed only to resolve
                # the dynamic Resource class. We don't want those parameters to be used by the dynamic
                # resource for filtering
                filter = getattr(request, '_filters', request.GET)

                # request.GET is used for filtering along with kwargs['GET']. They are combined (see get_object_list)
                encoding = request.GET.encoding
                request._original_params = request.GET.copy()

                # Make sure the values are singular so we don't
                # get weird array values back
                request.GET = http.QueryDict(
                    '&'.join(
                        map_dict(lambda key, value: '%s=%s' % (key, value[-1] if isinstance(value, list) else value), filter)
                    ),
                    encoding=encoding
                )
            else:
                wrapped_view = super(ModelResource, self).wrap_view(view)

            return wrapped_view(request, *args, **kwargs)
        return wrapper

    def deserialize(self, request, data, format='application/json; charset=utf-8'):
        """
        Given a request, data and a format, deserializes the given data.

        It relies on the request properly sending a ``CONTENT_TYPE`` header,
        falling back to ``application/json`` if not provided.

        Mostly a hook, this uses the ``Serializer`` from ``Resource._meta``.
        """
        deserialized = self._meta.serializer.deserialize(data, format=request.META.get('CONTENT_TYPE', 'application/json; charset=utf-8'))
        return deserialized

    def subclass_resource_if_needed(self, view, request):
        """
            Called to dynamically subclass abstract resources that wrap dynamic model classes, such as abstract subclasses of Feature. The subclassing happens if the current resource class (self) is a subclass of DynamicResource and self is abstract, the latter needed to prevent infinite recursion. The subclassed resource wraps the view and thus becomes the resource executing the request

        :param request: The request with certain required parameters in GET. Important parameters are config_entity, which is a ConfigEntity id and layer, which is a Layer id. If a ConfigEntity id is given an the resource is a FeatureResource subclass, then a ConfigEntity-specific dynamic subclass is found
        :return: The wrapped view of the dynamic resource class instance or simply the wrapped view of self if no dynamic subclassing is needed.
        """

        # By default don't subclass, just call the super class wrap_view on the existing view
        return super(ModelResource, self).wrap_view(view)

    def pre_save(self, request, **kwargs):
        """
            Presave operations to perform for the model class after
            POST, PUT, and PATCH. We don't have access to the objects
            like on post_save, so this is only useful to turn off
            class-scope presentation and similar
        """
        params = request.GET
        user_id = ApiKey.objects.get(key=params['api_key']).user_id
        model_class = self._meta.queryset.model
        if hasattr(model_class, 'pre_save'):
            model_class.pre_save(user_id, **kwargs)

    def post_save(self, request, response, **kwargs):
        """
            Optional operations to perform after POST, PUT, and PATCH
        :param request:
        :return:
        """
        objects = response.objects if hasattr(response, 'objects') else None
        params = request.GET
        user_id = ApiKey.objects.get(key=params['api_key']).user_id
        model_class = self._meta.queryset.model

        if hasattr(model_class, 'post_save'):
            logger.warn("Calling post_save for model class %s" % model_class.__name__)
            model_class.post_save(user_id, objects, **kwargs)

    def hydrate(self, bundle):
        """
            Always get the user from the request
        :param bundle:
        :return:
        """
        bundle.obj.user = self.resolve_user(bundle.request.GET)
        return bundle

    def resolve_user(self, params):
        return get_user_model().objects.get(username=params['username'])

    @classmethod
    def resolve_resource_class(cls,
                               model_class,
                               related_descriptors=None,
                               queryset=None,
                               base_resource_class=None,
                               object_class=None,
                               no_cache=False,
                               use_version_fields=False,
                               only_abstract_resources=True,
                               additional_fields_dict=None,
                               is_join_query=False,
                               limit_fields=None,
                               for_template=False):
        """
            Match the model_class to an existing resource class by iterating through subclasses of self.__class__
            If no match occurs generate one if db_entity is specified, else None
        :param model_class:
        :param related_descriptors: Optionally provided a dictionary of related descriptors of the model_class to use to create related resource fields
        in the case of dynamic resource creation. If unspecified, related_descriptors are found using the base resource class's resolve_related_descriptors method
        :param no_cache: Don't use cached resources. Specifying queryset also prevents the cache being consulted
        :param use_version_fields: Special case for versioned models. Instructs the resource class creation
         to create dynamic fields to look in the model_class's Revisionable._version_field_dict to resolve
         the value of a field before looking at the database (current object) version of the field.
        :param additional_fields_dict. Optional dict that gives the resource class additional fields
        with values. This is not for related fields, rather special cases like passing the layer_selection
        to the FeatureResource.
        :param for_template: Currently just used for Features, but this indicates a template version of the
        resource is being sought
        :param is_join_query: True if the is a join query
        table or similar. This means that the queryset isn't actually valid yet
        :return: The matching or created resource
        """
        # Never seek a cached resource if a queryset or no_cache is specified
        allow_caching = queryset is None and not no_cache

        cls.logger.info("Resolving Resource Class for model_class %s with query %s and allow_caching %s and only_abstract_resources %s and base_resource_class %s",
            model_class.__name__, queryset, allow_caching, only_abstract_resources, base_resource_class)
        if not base_resource_class and allow_caching:
            # Try to get a cached resource if a base_resource_class is present and we allow caching
            # of this resource. We never allow caching if the queryset changes from request to request
            # Instead we subclass the best matching existing resource class
            resources = FootprintResource.match_existing_resources(model_class)
            if len(resources) > 1:
                logging.warn("Too many resources for model class: %s. Resources; %s" % (model_class, resources))
            if (len(resources) > 0):
                cls.logger.info("Found existing resource class %s for model class %s" % (resources[0], model_class))
                # Done, return the existing resource
                return resources[0]

        # If we don't allow caching or no resource was found
        if only_abstract_resources:
            # See if we can match an abstract resource to be our base.
            # We look for the best matching resource who's model class matches or is a superclass or our model class.
            base_resource_classes = FootprintResource.match_existing_resources(model_class, only_abstract_resources=True)
            cls.logger.info("Matching abstract base resource classes: %s" % base_resource_classes)
            base_resource_class = base_resource_classes[0] if len(base_resource_classes)==1 else base_resource_class
        else:
            # Fist try to find a concrete one that we already created
            concrete_base_resource_classes = FootprintResource.match_existing_resources(model_class, allow_abstract_resources=False)
            if len(concrete_base_resource_classes)==1:
                # Found a concrete resource class that was already created for this model
                # If this isn't a join query we can return this resource class
                base_resource_class = concrete_base_resource_classes[0]
                if not is_join_query:
                    return base_resource_class
            else:
                # Try to find an abstract one
                all_base_resource_classes = FootprintResource.match_existing_resources(model_class, only_abstract_resources=True)
                cls.logger.info("Matching abstract base resource classes: %s" % all_base_resource_classes)
                base_resource_class = all_base_resource_classes[0] if len(all_base_resource_classes)==1 else base_resource_class

        if is_join_query:
            # Join queries must pass in the limited fields from the layer_selection.result_map.result_fields
            limit_api_fields = limit_fields
        else:
            # Non-join queries find their fields from the model_class
            limit_api_fields = limited_api_fields(model_class, for_template=for_template)

        resource_class = base_resource_class or cls
        if base_resource_class:
            cls.logger.info("Resolved base_resource_class: %s" % base_resource_class)
        else:
            cls.logger.info("Could not resolve a base_resource_class. Using resource class %s" % cls)
        related_descriptors = related_descriptors or \
                              resource_class.resolve_related_descriptors(model_class) or \
                              {}

        cls.logger.info("Creating a resource subclass of %s for model_class %s with the following related descriptors %s" % (
            resource_class,
            model_class,
            ', '.join(map_dict(
                lambda related_field_name, related_descriptor: related_field_name,
                related_descriptors
            ))))
        related_fields = merge(additional_fields_dict or {}, map_dict_to_dict(
            lambda related_field_name, relationship_dict: cls.related_resource_field(
                related_field_name,
                merge(
                    dict(
                        # This is passed in, but might be overriden in the relationship_dict
                        use_version_fields=use_version_fields
                    ),
                    # Already a relationship dict
                    relationship_dict if isinstance(relationship_dict, dict) else dict(),
                    # Not a relationship dict, just a descriptor, wrap it
                    dict(descriptor=relationship_dict) if not isinstance(relationship_dict, dict) else dict(),
                ),
                # Always allow cached related resource classes.
                # I think this is always safe
                no_cache=False),
            related_descriptors))
        meta = merge(
            dict(fields=limit_api_fields) if limit_api_fields else
                dict(excludes=(resource_class.Meta.excludes if hasattr(
                  resource_class.Meta, 'excludes') else []) + cls.dynamic_excludes(
                model_class)),
            dict(queryset=queryset, object_class=object_class) if queryset else dict())
        return get_dynamic_resource_class(
            resource_class,
            model_class,
            # Created related fields from the related_descriptors
            fields=related_fields,
            # Optionally set the fields and queryset on the Meta class
            meta_fields=meta
        )

    @classmethod
    def dynamic_excludes(cls, model_class):
        """
            Finds fields that should be exclude from the query results, like the base class toOne attribute
        """
        return model_class.objects.field_names_to_omit_from_query_values() if\
            hasattr(model_class.objects, 'field_names_to_omit_from_query_values') else\
            []

    @classmethod
    def related_resource_field(cls, related_field_name, relationship_dict, no_cache=False):
        """
           Returns a tuple of the related_field resource name and resource field. ManyToMany and ForeignKey is currently supported
        :param related_field_name: The related name on the model class
        :param relationship_dict: A dict describing the relationship with keys
            descriptor: The related ReverseSingleRelatedObjectDescriptor (or similar) of the model class. Expected is an instance of models.ManyToMany, or models.ForeignKey
            field: (Alternative to descriptor. A related Field
            full: Tastypie field param
            null: Tastypie field param
            no_cache: Don't use a cached resource for this field's dynamic resource class
            use_version_fields: Explained below
        :param no_cache: Default False. True to avoid using a cached resource class
        :return: A tuple with the field.name or singularized version and the created resource field.
        All fields created have full=False and null=True with the assumption that the value is optional and a need not be nested
        """

        cls.logger.info("Resolving related resource field with name %s and no_cache %s" % (related_field_name, no_cache))
        callable_attribute = None
        full = None
        null = True
        use_version_fields = False
        if isinstance(relationship_dict, Field):
            # related_descriptor is a Field
            related_field = relationship_dict
        elif isinstance(relationship_dict, dict):
            related_field = relationship_dict['descriptor'].field if\
                relationship_dict.get('descriptor') else\
                relationship_dict['field']
            callable_attribute = relationship_dict.get('callable_attribute')
            full = relationship_dict.get('full', False)
            null = relationship_dict.get('null', True)
            no_cache = relationship_dict.get('no_cache', True)
            # Enable lookup of this field and the resource fields of Revisionable._version_field_dict
            use_version_fields = relationship_dict.get('use_version_fields', False)
        else:
            # ReverseManyToMany and similar
            related_field = relationship_dict.field
        related_resource_class = FootprintResource.resolve_resource_class(
            related_field.rel.to,
            no_cache=no_cache,
            use_version_fields=use_version_fields,
            only_abstract_resources=False)
        # Clear the related object field caches in case it didn't pick up the dynamic many-to-many field of cls's model
        clear_many_cache(related_field.rel.to)
        name = related_field.name or related_field_name
        if callable_attribute:
            # Explicit callable_attribute defined for this attribute
            attribute = callable_attribute
        elif use_version_fields:
            # If this is set it means we set the Revisionable._version_field_dict
            # Tell the related field to look for a _version_field_dict key matching the attribute name
            # If found return that, otherwise just return the normal object field value
            def get_attribute(bundle):
                obj = (bundle.obj._version_field_dict if
                                        hasattr(bundle.obj, '_version_field_dict') else
                                        dict())\
                    .get(name, getattr(bundle.obj, name))
                return obj
            attribute = get_attribute
        else:
            # Simply use the field name as the attribute
            attribute = name

        if isinstance(related_field, models.ManyToManyField):
            field_class = fields.ToManyField
        elif isinstance(related_field, models.ForeignKey):
            field_class = fields.ToOneField
        else:
            raise Exception("Expected ToManyField or ToOneField. Got %s" % related_field.__class__.__name__)
        return [name, field_class(related_resource_class, attribute=attribute, full=full, null=null)]

    @classmethod
    def match_existing_resources(cls, model_class, allow_abstract_resources=False, only_abstract_resources=False):
        """
            Find all subclasses of self.__class__ whose queryset model is the given model_class or superclass thereof
        :param model_class: The model class to match
        :param allow_abstract_resources: Default False, Allow abstract resource classes to match and return
        :param only_abstract_resources: Default False, Only accept abstract resource classes as a match. This prevents previously
        dynamically created resource subclass from being used.
        :return:
        """
        def matches(resource_class):
            abstract = hasattr(resource_class._meta, 'abstract') and resource_class._meta.abstract
            if (abstract and (allow_abstract_resources or only_abstract_resources)) or\
               (not abstract and not only_abstract_resources):
                    return resource_class.matches_model(model_class)

        return match_subclasses(cls, matches)

    @classmethod
    def matches_model(cls, model_class):
        """
            Determine if the given model_class matches or is a superclass of the resource model class.
            Use our special cls._meta._model property for abstract resources
        :return:
        """
        if cls._meta.queryset:
            return issubclass(model_class, cls._meta.queryset.model)
        elif hasattr(cls.Meta, '_model'):
            # If our special property for abstract classes is present
            return issubclass(model_class, cls.Meta._model)
        return False

    @classmethod
    def resolve_related_descriptors(cls, model_class):
        """
            Override to return the related descriptors of the model_class. Related descriptors are used to create
            related resource fields for dynamic resource classes
        :param model_class:
        :return:
        """
        return None
