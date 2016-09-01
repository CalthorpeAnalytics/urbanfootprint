
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

from django.core.exceptions import ObjectDoesNotExist
from tastypie.exceptions import ApiFieldError
from tastypie.fields import ToManyField, NOT_PROVIDED, DateTimeField, BooleanField, ToOneField
from tastypie.resources import ModelResource
from footprint.main.lib.functions import map_to_keyed_collections, flatten, merge, unique, flat_map_values, get_first
from footprint.main.lib.functions import map_to_keyed_collections, flatten, map_to_dict, merge, unique, flat_map_values, get_first
from footprint.main.models import DbEntityInterest
from footprint.main.resources.category_resource import CategoryResource
from footprint.main.resources.policy_resources import PolicySetResource
import logging
from footprint.main.resources.tag_resource import TagResource
from footprint.main.resources.caching import using_bundle_cache

__author__ = 'calthorpe_analytics'


class ToManyCustomAddField(ToManyField):
    """
        Adds the ability to place an add attribute on the field definition. The add attribute points to a lambda that specifies how to add many-to-many items to a collection. The default Tastypie method just clears the collection and adds all the items, which doesn't work for explicit through class m2ms or our RelatedCollectionAdoption sets. The add lambda accepts the bundle, which should have a reference to the fully hydrated base object at bundle.obj.
    """

    def __init__(self, to, attribute, related_name=None, default=NOT_PROVIDED,
                 null=False, blank=False, readonly=False, full=False,
                 unique=False, help_text=None, add=None, remove=None, **kwargs):
        super(ToManyCustomAddField, self).__init__(
            to, attribute, related_name=related_name, default=default,
            null=null, blank=blank, readonly=readonly, full=full,
            unique=unique, help_text=help_text, **kwargs
        )
        self.add = add
        # Optional. The add might handle removing existing instances that aren't passed in to add
        self.remove = remove


class SubclassRelatedResourceMixin(object):
    """
        Mixin that allows related items to be subclasses by fetching the resource subclass instead of the base resource
        Make sure that the query is actually returning subclasses by using select_subclasses()
    """
    def get_related_resource(self, related_instance):
        """
        Instantiates the related resource. Override this method to subclass according to the related instance, rather
        than just using the to class of the Field
        """
        related_resource_class = get_first(filter(
            # Check for object_class since some of our dynamic resources lack one
            lambda resource_class: resource_class._meta.object_class and issubclass(related_instance.__class__, resource_class._meta.object_class),
            self.to_class().__class__.__subclasses__()), None)
        related_resource = related_resource_class() if related_resource_class else self.to_class()

        if related_resource._meta.api_name is None:
            if self._resource and self._resource._meta.api_name is not None:
                related_resource._meta.api_name = self._resource._meta.api_name

        # Try to be efficient about DB queries.
        related_resource.instance = related_instance
        return related_resource

    def resource_from_uri(self, fk_resource, uri, request=None, related_obj=None, related_name=None):
        """
        Given a URI is provided, the related resource is attempted to be
        loaded based on the identifiers in the URI.
        """
        try:
            obj = fk_resource.get_via_uri(uri, request=request)
            subclassed_obj = obj.__class__.objects.filter(id=obj.id).get_subclass()
            related_resource = self.get_related_resource(subclassed_obj)
            bundle = related_resource.build_bundle(
                obj=subclassed_obj,
                request=request
            )
            return related_resource.full_dehydrate(bundle)
        except ObjectDoesNotExist:
            raise ApiFieldError("Could not find the provided object via resource URI '%s'." % uri)


class ToManyFieldWithSubclasses(SubclassRelatedResourceMixin, ToManyField):
    """
        Mixes in the ability to subclass items
    """
    pass


class ToManyCustomAddFieldWithSubclasses(SubclassRelatedResourceMixin, ToManyCustomAddField):
    """
        Mixes in the ability to subclass items
    """
    pass


class ToOneFieldWithSubclasses(SubclassRelatedResourceMixin, ToOneField):
    """
        Mixes in the ability to subclass the item
    """
    pass


class BuiltFormSetsResourceMixin(ModelResource):
    @using_bundle_cache
    def built_form_sets_query(bundle):
        return bundle.obj.computed_built_form_sets()

    def add_built_form_sets(bundle, *built_form_sets):
        return bundle.obj.add_built_form_sets(*built_form_sets)

    def remove_built_form_sets(bundle, *built_form_sets):
        bundle.obj.remove_built_form_sets(*built_form_sets)

    built_form_sets = ToManyCustomAddField(
        'footprint.main.resources.built_form_resources.BuiltFormSetResource',
        attribute=built_form_sets_query,
        add=add_built_form_sets,
        remove=remove_built_form_sets,
        full=False,
        null=True)


class PolicySetsResourceMixin(ModelResource):
    @using_bundle_cache
    def policy_sets_query(bundle):
        return bundle.obj.computed_policy_sets()
    add_policy_sets = lambda bundle, *policy_sets: bundle.obj.add_policy_sets(*policy_sets)
    remove_policy_sets = lambda bundle, *policy_sets: bundle.obj.remove_policy_sets(*policy_sets)
    policy_sets = ToManyCustomAddField(
        PolicySetResource,
        attribute=policy_sets_query,
        add=add_policy_sets,
        remove=remove_policy_sets,
        full=False,
        null=True)


class DbEntityResourceMixin(ModelResource):
    # We always filter out provisional DbEntities, because they are not complete enough to deliver
    @using_bundle_cache
    def db_entities_query(bundle):
        return bundle.obj.computed_db_entities(setup_percent_complete=100)

    # We don't support adding DbEntities from the client. It can only be done by the server
    # So this is readonly
    db_entities = ToManyField(
        'footprint.main.resources.db_entity_resources.DbEntityResource',
        attribute=db_entities_query,
        readonly=True,
        full=False,
        full_list=False,
        null=True)


class PresentationResourceMixin(ModelResource):
    # Select the subclasses since we divide up Presentations by their subclass to help the API user and Sproutcore
    @using_bundle_cache
    def presentations_query(bundle):
        return bundle.obj.presentation_set.all().select_subclasses()
    # Read-only subclassed presentations
    presentations = ToManyFieldWithSubclasses('footprint.main.resources.presentation_resources.PresentationResource',
                                              attribute=presentations_query, null=True, readonly=True)

    def map_uri_to_class_key(self, uri):
        if 'result_library' in uri:
            return 'results'
        if 'layer_library' in uri:
            return 'layers'
        else:
            raise Exception("Unknown Presentation class for uri {0}".format(uri))

    def dehydrate_presentations(self, bundle):
        """
            Separates the presentations by type into a dict to make them easier to digest on the client.
            Any Presentation of type Presentations goes under 'maps'. Any of type ResultPage goes under 'results'. This
            is done because Sproutcore can't easily handle having multiple classes in a single list. But really, it's
            better for an API consumer to see them separated anyway.
        :param bundle:
        :return:
        """
        return map_to_keyed_collections(lambda presentation_uri: self.map_uri_to_class_key(presentation_uri), bundle.data['presentations'])

    def hydrate_presentations(self, bundle):
        """
            Does the reverse of dehydrate_presentations. If the user actually wanted to create new presentations via the
            API they'd simply save a presentation pointing to the correct configEntity, so we could probably just
            disregard this list on post/patch/put.
        :param bundle:
        :return:
        """
        if bundle.data.get('id', 0) == 0:
            # We can't handle presentations on new config_entities yet.
            # One problem is that tastypie/django doesn't like presentations that are actually
            # layer_libraries and result_libraries that have layers and results, respectively
            bundle.data['presentations'] = None
            return bundle

        if bundle.data.get('presentations', None):
            bundle.data['presentations'] = flatten(bundle.data['presentations'].values()) if isinstance(bundle.data['presentations'], dict) else bundle.data['presentations']
        else:
            bundle.data['presentations'] = []
        return bundle


def add_categories(bundle, *submitted_categories):
    """
            When the user updates the values of one or more categories, we assume that they want to delete the current Category instances with the same keys and replace them with the selected Category value. For instance, if a scenario has the Category key:'category' value:'smart' and the user chooses 'dumb' for the new value, we want to delete the Category instance valued by 'smart' and insert the one valued by 'dumb'. But we don't want to mess with Category instances that have different keys
    """
    logger = logging.getLogger(__name__)
    try:
        submitted_categories_by_key = map_to_keyed_collections(lambda category: category.key, submitted_categories)
        existing_categories_by_key = map_to_keyed_collections(lambda category: category.key, bundle.obj.categories.all())
        categories_to_add_or_maintain = flat_map_values(lambda key, categories: unique(categories, lambda category: category.value),
                                                        merge(existing_categories_by_key, submitted_categories_by_key))
        bundle.obj.categories.clear()
        bundle.obj.categories.add(*categories_to_add_or_maintain)
    except Exception, e:
        logger.critical(e.message)


class CategoryResourceMixin(ModelResource):
    # Allow this to be null since categories are currently copied on the server when cloning.
    # They could easily be done on the client
    categories = ToManyCustomAddField(
        CategoryResource,
        'categories',
        null=True,
        # No need for remove. Categories clears itself on add, so any exiting categories are removed
        add=add_categories
    )


class TagResourceMixin(ModelResource):
    tags = ToManyField(TagResource, 'tags', null=True)


class TimestampResourceMixin(ModelResource):
    created = DateTimeField(attribute='created', readonly=True)
    updated = DateTimeField(attribute='updated', readonly=True)


class PublisherControlMixin(ModelResource):
    """
        A simple flag to indicate that post presentation should be disabled.
    """
    no_post_save_publishing = BooleanField(attribute='no_post_save_publishing')


class CloneableResourceMixin(ModelResource):
    origin_instance = ToOneField('self', 'origin_instance', full=False, null=True)
