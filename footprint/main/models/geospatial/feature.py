
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
from django.contrib.gis.db import models
from django.contrib.gis.db.models import GeoManager
from django.db.models import Max, Min, ManyToOneRel
from django.db.models.query_utils import DeferredAttribute

from footprint.main.lib.functions import remove_keys, flatten
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.dynamic import Dynamic
from footprint.main.mixins.revisionable import Revisionable
from footprint.main.utils.model_utils import classproperty
from footprint.main.models.geospatial.built_form_feature import BuiltFormFeature

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class Feature(models.Model, Revisionable, Dynamic):
    """
        A mixin model class that references a Geography instance. The abstract Geography class and its subclasses
        represent geography authorities, so that any shared geographies like regional parcels have one authoritive
        locations. Derived classes and their instances, such as the ConfigEntityGeography derivative classes use the
        Geographic mixin to reference the authoritative geographies of the Geography class hierarchy
    """
    def __init__(self, *args, **kwargs):
        # This is for FeatureQuantitative Attribute. TODO can't this be handled in the subclass init?
        self.attribute = kwargs.get('attribute')
        super(Feature, self).__init__(*args, **remove_keys(kwargs, ['attribute']))

    API_EXCLUDED_FIELD_NAMES = ['wkb_geometry']

    # Base manager inherited by subclasses
    objects = GeoManager()

    # Used by the dynamic mixin to resolve the DynamicModelClassCreator
    dynamic_model_class_creator_class = 'footprint.main.models.feature.feature_class_creator.FeatureClassCreator'

    # The geometry imported for the feature
    wkb_geometry = models.GeometryField(geography=False)

    api_include = None
    attribute = None

    @property
    def the_unique_id(self):
        """
            (Note, we use the_ to avoid clashes with unique_id, which is a comment feature column)
            A unique id across all Feature subclass instances
            If this is a TemplateFeature based on metadata just return a fake id
        """
        from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
        return '%s_%s' % (self.db_entity.id if \
                              self.configuration.key != FeatureClassCreator.DETACHED_FROM_DB_ENTITY else \
                              FeatureClassCreator.DETACHED_FROM_DB_ENTITY,
                          self.id)

    @classproperty
    def db_entity(cls):
        """
            Resolve the DbEntity of the feature_class
        :param cls:
        :return:
        """
        return cls.config_entity.computed_db_entity(key=cls.db_entity_key)

    @classproperty
    def default_api_fields(cls):
        return ['the_unique_id', 'comment', 'updater', 'updated', 'approval_status']

    @classproperty
    def template_api_fields(cls):
        return ['config_entity', 'db_entity']

    @classmethod
    def limited_api_fields(cls, for_template=False):
        """
            Limit the api fields to api_include fields if present
            Also add defaults depending on whether or not a template Feature is needed
        :return:
        """
        # (unicode to match generated id name)
        return ([u'id'] + cls.api_include + (cls.template_api_fields if for_template else []) + cls.default_api_fields) if\
            cls.api_include else\
            None

    @classproperty
    def feature_fields(cls):
        """
            The fields of the Feature class
        """
        return cls.result_map.result_fields if cls.result_map else []

    @classproperty
    def feature_field_title_lookup(cls):
        """
            The fields to title lookup of the Feature class
        """
        return cls.result_map.title_lookup if cls.result_map else {}

    @classproperty
    def result_map(cls):
        """
            Creates an caches a result map for the Feature class. The result_map has useful meta data about
            the class
        :param cls:
        :return:
        """
        if cls._result_map:
            return cls._result_map
        from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
        feature_class_creator = FeatureClassCreator.from_dynamic_model_class(cls)
        if not feature_class_creator.dynamic_model_class_is_ready:
            return None
        cls._result_map = feature_class_creator.dynamic_model_class().objects.all().create_result_map()
        return cls._result_map
    _result_map = None

    @classmethod
    def post_save(cls, user_id, objects, **kwargs):
        """
            Optional class method to kick of analytic modules (see FutureScenarioFeature)
        """
        from footprint.main.publishing.feature_publishing import on_feature_post_save
        on_feature_post_save(cls, instance=objects, user_id=user_id)

    class Meta(object):
        abstract = True
        app_label='main'


class PaintingFeature(Feature, BuiltFormFeature):
    """
        Represents a feature that can be "painted" in the API
        TODO replace this by means of a Behavior
    """
    objects = GeoManager()

    dev_pct = models.DecimalField(max_digits=8, decimal_places=4, default=1.0000)
    density_pct = models.DecimalField(max_digits=8, decimal_places=4, default=1.0000)
    gross_net_pct = models.DecimalField(max_digits=8, decimal_places=4, default=1.0000)

    clear_flag = models.BooleanField(default=False)
    dirty_flag = models.BooleanField(default=False)

    developable_proportion = models.DecimalField(max_digits=8, decimal_places=4, default=1)
    acres_developable = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta(object):
        abstract = True
        app_label = 'main'


class FeatureGeography(models.Model):
    """
    An abstract class representing the association between a Feature class and Geography class
    """
    objects = GeoInheritanceManager()

    # Associates a Feature class to a Geography class
    # Assign these to ForeignKey fields
    feature = None
    geography = None

    def __unicode__(self):
        return "FeatureGeography:Feature:{1}, Geography:{2}".format(self.feature, self.geography)
    class Meta(object):
        app_label = 'main'
        abstract = True



class FeatureCategoryAttribute(object):

    db_entity = None
    attribute = None
    feature_class = None
    unique_values = None

    def __init__(self, db_entity, attribute):
        self.db_entity = db_entity
        self.attribute = attribute
        self.feature_class = db_entity.feature_class
        self.unique_values = flatten(map(lambda value: value.values(), self.get_unique_values))

    @property
    def get_unique_values(self):
        return self.feature_class.objects.order_by().values(self.attribute).distinct()



class FeatureQuantitativeAttribute(object):

    db_entity = None
    attribute = None
    feature_class = None
    min = None
    max = None

    def __init__(self, db_entity, attribute):
        self.db_entity = db_entity
        self.attribute = attribute
        self.feature_class = db_entity.feature_class
        self.min = self.minimum_value.values()[0]
        self.max = self.maximum_value.values()[0]

    @property
    def minimum_value(self):
        return self.feature_class.objects.all().aggregate(Min(self.attribute))

    @property
    def maximum_value(self):
        return self.feature_class.objects.all().aggregate(Max(self.attribute))
