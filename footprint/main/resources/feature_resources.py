
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

import string
import logging
from django.db.models.query import ValuesQuerySet
from tastypie import fields
from tastypie.constants import ALL
from django.db import models
from tastypie.fields import ListField
from tastypie.paginator import Paginator
from tastypie.resources import ModelResource

from footprint.upload_manager.models import UploadDatasetTask
from footprint.main.lib.functions import map_dict_to_dict, map_to_dict, merge, compact_dict, deep_merge, map_dict, \
    compact, remove_keys
from footprint.main.models import LayerSelection
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.models.geospatial.feature import Feature, FeatureCategoryAttribute, \
    FeatureQuantitativeAttribute
from footprint.main.models.geospatial.feature_version import FeatureVersionProxy, feature_revision_manager
from footprint.main.resources.config_entity_resources import ConfigEntityResource
from footprint.main.resources.db_entity_resources import DbEntityResource
from footprint.main.resources.footprint_resource import FootprintResource
from footprint.main.resources.mixins.dynamic_resource import DynamicResource
from footprint.main.resources.mixins.feature_resource_mixin import FeatureResourceMixin
from footprint.main.resources.mixins.revisionable_resource import RevisionableResource
from footprint.main.resources.pickled_dict_field import PickledDictField
from footprint.main.resources.revision_resource import VersionResource
from footprint.main.resources.user_resource import UserResource
from footprint.main.resources.caching import using_bundle_cache

logger = logging.getLogger(__name__)

class SingletonFeatureResourceMixin(ModelResource):
    pass


class FeatureResource(FeatureResourceMixin, DynamicResource, RevisionableResource):
    class Meta(DynamicResource.Meta):
        always_return_data = True
        abstract = True
        paginator_class = Paginator
        excludes = Feature.API_EXCLUDED_FIELD_NAMES
        ordering = ['id']
        filtering = {
            # Accept the django query id__in
            "id": ALL
        }
        resource_name = 'feature'
        # querysets are not allowed for abstract classes. So use a special property
        # to associate the model
        _model = Feature


    # Dehydrate the class config_entity into each instance.
    config_entity = fields.ToOneField(ConfigEntityResource, 'config_entity', null=False, readonly=True)
    # DbEntity plus id uniquely ids the features's scope
    # Only allowed to be null for TemplateFeatures based on metadata (before a DbEntity exists)
    db_entity = fields.ToOneField(DbEntityResource, 'db_entity', null=True, readonly=True)
    # The updater of the feature. We remove everything but the username for security
    updater = fields.ToOneField(UserResource, 'updater', full=True, readonly=True, null=True)
    # Unique id for the Client across all Features in the system--a combination of the DbEntity id and Feature id
    the_unique_id = fields.CharField(attribute='the_unique_id', null=False, readonly=True)

    def dehydrate_updater(self, bundle):
        """
            Expose only the username, not the whole User model instance
        :param bundle:
        :return:
        """
        updater = bundle.data.get('updater')
        return updater.data['username'] if updater else None


    def hydrate_comment(self, bundle):
        # Also write to the base feature table comments field if it exists
        if hasattr(bundle.obj, 'comments'):
            bundle.obj.comments = bundle.data['comment']
        return bundle

    def hydrate(self, bundle):
        """
           Sets the updater to the current user
        :param bundle:
        :return:
        """
        self.revisionable_hydrate(bundle)
        bundle.obj.updater = self.resolve_user(bundle.request.GET)
        return bundle

    def dehydrate(self, bundle):
        """
            Override to add in the __label attributes. These are the human readable
            version of attributes that represent objects or more appropriate formatting,
            such as for dates
        :param bundle:
        :return:
        """

        # This is a dynamic field create at the time of creating the FeatureResource subclass
        result_field_lookup = self.result_field_lookup

        # Map the fields that need special human-readable representation
        # to labels. We iterate through the result_field_lookup that
        # the LayerSelection generated for this.
        # Not the conditional statement is for the "corner" case
        # of patching Features with joins specified. Patches always
        # ignore the JoinFeature class and use the regular Feature class,
        # however the result_field_lookup still contains join fields--ignore them
        bundle.data['__labels'] = compact_dict(map_dict_to_dict(
            lambda field_name, field_lambda: [
                field_name,
                field_lambda(getattr(bundle.obj, self.client_field_name(field_name)))
            ] if '__' not in field_name else None,
            result_field_lookup
        ))
        return super(FeatureResource, self).dehydrate(bundle)

    def client_field_name(self, field_name):
        """
            Normally the server field_name is represented the same way on the client
            See JoinFeatureResource for an override of this
        :param field_name:
        :return:
        """
        return field_name


    def dynamic_resource_subclass(self, layer_selection=None, db_entity=None, feature_class=None, config_entity=None, metadata=None, params=None, **kwargs):
        """
            Creates the dynamic Feature Resource class by passing in a layer_selection, db_entity, or feature_class
        :param layer_selection: Required if db_entity or metadata aren't present
        :param db_entity: Required if layer_selection or metadata aren't present
        :param metadata: Required along with config_entity if layer_selection or db_entity aren't present
        :param kwargs:
        :return:
        """
        feature_class_configuration = None
        if layer_selection:
            # Coming in relative to a LayerSelection, which puts us in the context of the LayerSelection's
            # feature query for this Feature subclass
            layer = layer_selection.layer
            # If we pass in a ConfigEntity it means we want to scope the Feature class to its scope.
            # The ConfigEntity defaults to that of the Layer, but we can override it to be a lower
            # scope to make sure that we have access to lower DbEntities of performing joins
            config_entity = config_entity.subclassed if config_entity else layer.config_entity.subclassed
            logger.debug("Resolving FeatureResource subclass for layer_selection: {0}, config_entity: {1}".format(layer_selection.unique_id, config_entity.id))
            # Resolve the dynamic Feature class with the given config_entity so that we can access all DbEntities
            # of the ConfigEntity for joins
            feature_class = config_entity.db_entity_feature_class(layer.db_entity.key)
        elif db_entity:
            # Coming in relative to a DbEntity, meaning we don't care about a particular LayerSelection's
            # feature query for this Feature subclass
            config_entity = db_entity.config_entity
            logger.debug("Resolving FeatureResource subclass for db_entity: {0}, config_entity: {1}".format(db_entity.id, config_entity.id))
            # Resolve the dynamic Feature class with the given config_entity so that we can access all DbEntities
            # of the ConfigEntity for joins
            feature_class = config_entity.db_entity_feature_class(db_entity.key)
        elif metadata:
            # Coming in with metadata, meaning this is and uploaded or ArcGis table with no DbEntity yet
            # We need to construct a FeatureClass from the metadata
            logger.debug("Resolving FeatureResource subclass for metadata: {0}, config_entity: {1}".format(metadata, config_entity.id))
            feature_class_creator = FeatureClassCreator(
                config_entity
            )
            feature_class_configuration = feature_class_creator.feature_class_configuration_from_metadata(metadata['schema'])
            feature_class = FeatureClassCreator(
                config_entity,
                feature_class_configuration
            ).dynamic_model_class()

        if not feature_class_configuration:
            # If we didn't already ensure all dynamic model classes have been created
            # This only need to run once to get all dynamic feature subclasses into memory,
            # in case they are needed by an association, join, or something similar
            feature_class_creator = FeatureClassCreator.from_dynamic_model_class(feature_class)
            feature_class_creator.ensure_dynamic_models()

        logger.debug("Resolving resource for Feature subclass: {0}".format(feature_class))

        # Resolve the FeatureResource subclass based on the given Feature subclass
        # If self is already a subclass, just return self
        # Else, return a preconfigured subclass or one dynamically created. The latter will probably be the only way in the future.
        # If not already subclassed
        is_singleton_feature = issubclass(self.__class__, SingletonFeatureResourceMixin)
        is_template_feature = self.__class__ == TemplateFeatureResource
        if self.__class__ in [FeatureResource, TemplateFeatureResource, FeatureCategoryAttributeResource,
                              FeatureQuantitativeAttributeResource]:
            if is_singleton_feature or params.get('is_feature_attribute'):
                queryset = feature_class.objects.none()
            elif kwargs.get('method', None) == 'PATCH':
                # It's possible to PATCH with an active join query.
                # But we don't want to use a join query when patching
                queryset = feature_class.objects.all()
            else:
                # Get the queryset stored by the layer_selection or an empty query if we don't have a layer_selection
                queryset = layer_selection.selected_features_or_values if\
                    layer_selection else \
                    feature_class.objects.none()

                if layer_selection and not (is_singleton_feature or kwargs.get('query_may_be_empty')) and queryset.count()==0:
                    raise Exception(
                        "Unexpected empty queryset for layer_selection features: %s" %
                        queryset.query)
            is_values_queryset = isinstance(queryset, ValuesQuerySet)

            #returns queryset ordered by the table id
            queryset = queryset.order_by('id')

            if is_values_queryset:
                join_feature_class = layer_selection.create_join_feature_class() if is_values_queryset else feature_class
                logger.info("Created join_feature_class: %s" % join_feature_class)
                # Force the queryset to our new class so that Tastypie can map the dict results to it
                queryset.model = join_feature_class

                return self.__class__.resolve_resource_class(
                    join_feature_class,
                    queryset=queryset,
                    base_resource_class=self.join_feature_resource_class(join_feature_class),
                    additional_fields_dict=dict(
                        # Pass these to the feature resource to help it resolve
                        # field mappings and add related fields (just need for join_feature_class)
                        # Use the layer_selection if it exists since it might have filtered or extra query fields
                        result_field_lookup=(layer_selection or db_entity).result_field_lookup if not metadata else {},
                        related_field_lookup=(layer_selection or db_entity).related_field_lookup if not metadata else {},
                        # We use these in the FeatureResource to create a unique id for each join Feature
                        join_model_attributes=layer_selection and layer_selection.result_map.join_model_attributes
                    ),
                    is_join_query=True,
                    limit_fields=layer_selection.result_map['result_fields']
                )
            else:
                abstract_feature_resource_class = self.__class__
                resource_class = abstract_feature_resource_class.resolve_resource_class(
                    feature_class,
                    queryset=queryset,
                    # Give FeatureResource a reference to the layer_selection
                    additional_fields_dict=merge(
                        dict(
                            # Pass this to the feature resource to help it resolve field mappings
                            result_field_lookup=(layer_selection or db_entity).result_field_lookup if not metadata else {}
                        ),
                        dict(
                            # Not sure why it doesn't work to just stick this on the TemplateFeatureResource
                            feature_fields=ListField(attribute='feature_fields', null=True, blank=True, readonly=True),
                            feature_field_title_lookup=PickledDictField(attribute='feature_field_title_lookup', null=True, blank=True, readonly=True),
                        ) if is_template_feature else dict()
                    ),
                    for_template=is_template_feature
                )
                return resource_class
        return self

    def create_subclass(self, params, **kwargs):
        """
            Subclass this class to create a resource class specific to the config_entity.
        :param params.layer__id or db_entity__id: The layer id. Optional. Used to resolve the Feature/FeatureResource subclasses if we are in FeatureResource (not in a subclass)
        :return: The subclassed resource class
        """

        if params.get('file_dataset__id'):
            # A FileDataset corresponds to an UploadDatasetTask
            # We receive this parameter for unsaved DbEntities that are requesting feature metdata
            uploadDatasetTask = UploadDatasetTask.objects.get(id=int(params.get('file_dataset__id')))
            metadata = uploadDatasetTask.metadata
            return self.dynamic_resource_subclass(
                **merge(
                    dict(config_entity=uploadDatasetTask.upload_task.config_entity.subclassed, metadata=metadata, params=params),
                    kwargs
                )
            )
        else:
            # Resolve the LayerSelecton of the Layer in context of the DbEntity if one exists. This gives us a predefined
            # queryset of the features. If no LayerSelection exists (because no Layer exists) we resolve the subclass
            # with the db_entity. The latter implies that we want the full queryset.
            config_entity = self.resolve_config_entity(params)
            layer_selection = self.resolve_layer_selection(params)
            logger.debug("For FeatureResource resolved config_entity %s and layer %s" % (
                config_entity.key, layer_selection.layer.db_entity.key if layer_selection else 'None'
            ))
            return self.dynamic_resource_subclass(
                **merge(
                    dict(config_entity=config_entity, layer_selection=layer_selection) if layer_selection else dict(db_entity=self.resolve_db_entity(params)),
                    dict(params=params),
                    kwargs
                )
            )

    @classmethod
    def resolve_related_descriptors(cls, feature_class):
        """
            Resolve the related descriptors of the feature_class. These are the fields defined on the Feature subclass's
            Rel table.
        :param feature_class:
        :return: A dictionary of RelatedDescriptors
        """
        return feature_class.dynamic_model_class_creator.related_descriptors()

    def join_feature_resource_class(self, join_feature_class):
        class JoinFeatureResource(FeatureResource):
            # When we represent model relationships in Django queries, we use '__'
            # We use _x_ to represent this (internally) on the client, because the '__' can
            # confuse Django or Tastypie in some situation (I forget exactly when)
            FIELD_RELATION_SERVER = '__'
            FIELD_RELATION_CLIENT = '_x_'

            def dehydrate(self, bundle):
                bundle = super(JoinFeatureResource, self).dehydrate(bundle)
                def map_related_to_field_and_label(field_name, related_model):
                    """
                        Creates a mapping from the _id attribute of ForeignKeys to
                        to the related attribute (e.g. built_form_id to built_form).
                        It puts the related attribute in the main dict with its resource_uri
                        and puts a label representation in the __labels dict so that
                        the related attribute can map from its id to a label. This
                        is similar to what the regular FeatureResource does but it is
                        more manual since we only have the _id attribute and must
                        resolve the related instance ourselves
                    """
                    client_field_name = self.client_field_name(field_name)
                    related_id = getattr(bundle.obj, client_field_name) if hasattr(bundle.obj, client_field_name) else None
                    if related_id:
                        related_model_instance = related_model.objects.get(id=related_id)
                        related_field_name = field_name.replace('_id', '')
                        return {
                            # Get the resource class of the related model so we can make a uri
                            related_field_name: FootprintResource.resolve_resource_class(related_model)().get_resource_uri(related_model_instance),
                            # The label representation
                            '__labels': {related_field_name: LayerSelection.resolve_instance_label(related_model_instance)}
                        }
                    return None

                related_field_lookup = self.related_field_lookup
                if related_field_lookup:
                    # For join queries, we need to manually add related models--not the joins,
                    # rather related models on the main feature, such as a BuiltForm reference
                    bundle.data = deep_merge(bundle.data, *compact(map_dict(
                        map_related_to_field_and_label,
                        related_field_lookup
                    )))
                return bundle

            def full_dehydrate(self, bundle, for_list=False):
                # Convert the dict to the unmanaged join_feature_class instance
                # Since our JoinFeatureClass uses the client field names, we must map them back to server names
                # To do the lookup below
                field_name_lookup = map_to_dict(
                    lambda field: [string.replace(field.name, self.FIELD_RELATION_CLIENT, self.FIELD_RELATION_SERVER), True],
                    join_feature_class._meta.fields)

                # Map mapping fields from __ to _x_ so Tastypie|Django isn't confused by them
                dct = map_dict_to_dict(
                    lambda key, value: [self.client_field_name(key), value] if
                        field_name_lookup.get(key) else
                        None,
                    bundle.obj)
                obj = join_feature_class()
                for key, value in dct.items():
                    setattr(obj, key, value)
                # The object needs a pk to create its resource_uri
                setattr(obj, 'pk', obj.id)
                new_bundle = self.build_bundle(obj=obj, request=bundle.request)
                # This isn't automatically included like for the normal FeatureResource
                # The unique id must be unique across all joined Feature classes
                new_bundle.data['the_unique_id'] = '_'.join(
                    [obj.the_unique_id] +\
                    map(lambda attr: str(getattr(obj, attr)), self.join_model_attributes)
                )
                return super(JoinFeatureResource, self).full_dehydrate(new_bundle, for_list)

            def client_field_name(self, field_name):
                return string.replace(field_name, self.FIELD_RELATION_SERVER, self.FIELD_RELATION_CLIENT)

        return JoinFeatureResource

    _model_subclass = None
    def model_subclass(self, db_entity, config_entity):
        """
            Returns the Feature subclass
        :param params:
        :return:
        """
        if self._model_subclass:
            return self._model_subclass
        # Use the abstract resource class queryset model or given db_entity_key to fetch the feature subclass
        # Cache the result since this is expensive
        self._model_subclass = self.resolve_model_class(config_entity=config_entity, db_entity=db_entity)
        return self._model_subclass

class FeatureVersionResource(FeatureResourceMixin, VersionResource):
    # object_version is created dynamically according to the object class
    #object_version = ToOneField(FeatureResource, full=True, null=False)
    class Meta(VersionResource.Meta):
        always_return_data = True
        abstract = True
        filtering = {
            # Accept the django query id__in
            "id": ALL
        }
        resource_name = 'feature_version'

    def create_subclass(self, params, **kwargs):
        """
            Subclass this class to create a resource class specific to the Feature
        :param params.layer__id or db_entity__id: The Layer id or DbEntity id. Optional. Used to resolve the Feature/FeatureResource subclasses if we are in FeatureResource (not in a subclass)
        :return: The subclassed resource class
        """

        db_entity = self.resolve_db_entity(params)
        config_entity = db_entity.config_entity.subclassed
        feature_class = self.model_subclass(db_entity, config_entity)
        instance = self.resolve_instance(params, feature_class)
        return self.dynamic_resource_subclass(instance, **merge(kwargs, dict(feature_class=feature_class)))


    def dynamic_resource_subclass(self, instance, **kwargs):
        """
            Creates a dynamic resource using reversion to get the queryset of revisions for the instance
        :param instance:
        :param kwargs:
        :return:
        """

        feature_class = kwargs['feature_class']

        def get_versioned_version(feature_version, feature_class, key):
            """
                Return the related object for related attribute indicated by this key for the give feature_version
            :param feature_version:
            :param key:
            :return:
            """
            related_descriptor = getattr(feature_class, key)
            return related_descriptor.field.rel.to.objects.get(id=feature_version.field_dict[key])

        @using_bundle_cache
        def feature(bundle):
            # Get the current version of the Feature instance
            feature_instance = feature_class.objects.get(id=bundle.obj.field_dict['id'])
            # Update it (without saving). This doesn't take care of our related fields
            feature_instance.__dict__.update(**bundle.obj.field_dict)
            # Take care of our related fields by settings the Revisionable mixin's _version_field_dict
            # We instruct the related Resource field to check this _version_field_dict
            # to grab the versioned value
            feature_instance._version_field_dict = map_dict_to_dict(
                lambda key, value: [key, get_versioned_version(bundle.obj, feature_class, key)],
                feature_class.dynamic_model_class_creator.related_descriptors())

            # Set the magic version property so that we grab the right meta data
            feature_instance._version = bundle.obj
            return feature_instance

        return self.__class__.resolve_resource_class(
            FeatureVersionProxy,
            related_descriptors=merge(
                dict(
                    # Instruct the dynamic resource class to create a dynamic FeatureResource class
                    # for the related field.
                    feature=dict(
                        field=models.ForeignKey(feature_class),
                        callable_attribute=feature,
                        full=True,
                        null=True,
                        # Instruct the dynamic resource dehydrate related fields
                        # by replacing the default model_class field value with the _* version
                        # of the field if defined. This allows us to set the _* on our in-memory
                        # versioned Feature and read those _* field instead of the database (current version)
                        # field values
                        use_version_fields=True
                    )
                )
            ),
            queryset=feature_revision_manager.get_for_object(instance))


class TemplateFeatureResource(FeatureResource, SingletonFeatureResourceMixin):
    """
        Returns a single unsaved instance of the feature representing class-level version of the feature for meta-field info
        This will get subclassed just like the FeatureResource
    """

    class Meta(FeatureResource.Meta):
        abstract = True
        resource_name = 'template_feature'
        filtering = {
            # Accept the django query id__in
            "id": ALL
        }

    def dehydrate(self, bundle):
        # Use Resource's innate capability to add the schema of each field
        # to the results. Filter out meta fields and other things that the front-end doesn't need
        bundle.data['schemas'] = remove_keys(
            self.build_schema()['fields'],
            ['feature_field_title_lookup', 'feature_fields', 'resource_uri', 'config_entity', 'db_entity', 'the_unique_id']
        )
        return super(TemplateFeatureResource, self).dehydrate(bundle)

    def get_object_list(self, request):
        """
            Create a new instance with id 0 from our model class
        :param request:
        :return:
        """
        return [self._meta.queryset.model(id=0)]

    def apply_filters(self, request, applicable_filters):
        """
        Override for the template feature case
        """
        return self.get_object_list(request)

    def authorized_read_list(self, object_list, bundle):
        """
        Override for the template feature case
        """
        return object_list


class FeatureAttributeResource(FeatureResource, SingletonFeatureResourceMixin):
    """
    """
    class Meta(FeatureResource.Meta):
        abstract = True
        resource_name = 'feature_attribute'
        filtering = {
            # Accept the django query id__in
            "id": ALL
        }

    def get_object_list(self, request):
        """
            We ask the DbEntity to return its template_feature, which gives a feature
            that contains useful class-level info like the feature fields
        :param request:
        :return:
        """
        params = request._original_params
        db_entity = self.resolve_db_entity(params)
        config_entity = db_entity.config_entity.subclassed
        feature_class = self.model_subclass(db_entity, config_entity)
        return [feature_class.db_entity.feature_attribute(params['attribute'])]

    def apply_filters(self, request, applicable_filters):
        """
        Override for the template feature case
        """
        return self.get_object_list(request)

    def authorized_read_list(self, object_list, bundle):
        """
        Override for the template feature case
        """
        return object_list


class FeatureCategoryAttributeResource(FeatureAttributeResource):
    """
    """
    class Meta(FeatureResource.Meta):
        abstract = True
        resource_name = 'feature_category_attribute'
        filtering = {
            # Accept the django query id__in
            "id": ALL
        }

    def dehydrate(self, bundle):
        #Filter out meta fields and other things that the front-end doesn't need
        bundle.data = remove_keys(merge(bundle.data,
                            FeatureCategoryAttribute(bundle.obj.db_entity, bundle.obj.attribute).__dict__),
                                  ['db_entity', 'feature_class', 'config_entity', 'updated', 'updater', 'year'])
        return super(FeatureAttributeResource, self).dehydrate(bundle)


class FeatureQuantitativeAttributeResource(FeatureAttributeResource):
    """
    """
    class Meta(FeatureResource.Meta):
        abstract = True
        resource_name = 'feature_quantitative_attribute'
        filtering = {
            # Accept the django query id__in
            "id": ALL
        }

    def dehydrate(self, bundle):
        #Filter out meta fields and other things that the front-end doesn't need
        bundle.data = remove_keys(merge(bundle.data,
                            FeatureQuantitativeAttribute(bundle.obj.db_entity, bundle.obj.attribute).__dict__),
                                  ['db_entity', 'feature_class', 'config_entity', 'updated', 'updater', 'year'])
        return super(FeatureAttributeResource, self).dehydrate(bundle)
