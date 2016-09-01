
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

from django.db import models
from picklefield import PickledObjectField
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.key import Key
from footprint.main.models.geospatial.token import Token
from footprint.main.models.keys.keys import Keys
from footprint.main.utils.model_utils import classproperty

__author__ = 'calthorpe_analytics'

class JoinTypeKey(Keys):
    """
        A key class to describe table joins
    """
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            # No prefix is used, since these aren't stored as keys in a key column
            return ''
    # Intersect based on an attribute of the feature
    ATTRIBUTE = 'attribute'
    GEOGRAPHIC = 'geographic'

class GeographicKey(Keys):
    """
        A key class to describe geographic query types
    """
    # Intersect based on the polygon of the feature
    POLYGON = 'polygon'
    # Intersect based on the centroid of the feature
    CENTROID = 'centroid'


class JoinType(Key):
    """
        Simple class to define an attribute join and a geographic join
    """

    objects = GeoInheritanceManager()

    class Meta(object):
        abstract = False
        app_label = 'main'

class GeographicType(Key):
    """
        Simple class to define geography function by key, such as POLYGON and CENTROID
    """
    objects = GeoInheritanceManager()

    class Meta(object):
        abstract = False
        app_label = 'main'

class Intersection(models.Model):
    """
        Describes an intersection from on geographic table to another.
        The tree is a Token object defined for a subclass that can embed 0 to many more Tokens recursively.
        The tree describes an intersection query completely or can use parameters in the form {param_name} to provide
        spaces that are filled in by field values of subclasses
    """

    objects = GeoInheritanceManager()
    # Holds a default Token tree in memory. We don't store this in the database since it is constant.
    default_tree = None,
    # IF the customization of the default Token tree is needed, it is stored in the database here
    tree = PickledObjectField(default=None, null=True)
    # Class constant indicating the join type
    # This helps the front-end determine what kind of UI to show
    join_type_key = None
    # This is set True to indicate that the Intersection is a template instance that is shared among
    # instances, such as Behaviors, that never update the Intersection
    is_template = models.BooleanField(default=False)
    # feature_behavior is implicitly created by Django, since FeatureBehavior has a toOne

    @property
    def join_type(self):
        if not self.join_type_key:
            raise Exception("Class %s does not define a join_type_key" % self.__class__.__name__)
        return JoinType.objects.get(key=self.join_type_key)

    @property
    def subclassed(self):
        """
            Return the subclassed version of the Intersection. If not yet persisted the intersection instance
            will be a subclass or null
        :return:
        """
        return Intersection.objects.get_subclass(id=self.id) if\
            self.id else\
            self

    @property
    def feature_behavior(self):
        """
            This is justed used by the API to back-dirty the feature_behavior from the Intersection.
            It should probably be handled exclusively in the front- end
        :return:
        """
        if self.is_template:
            # Multiples possible, so return None
            return None
        return list(self.featurebehavior_set.all())[0]

    class Meta(object):
        abstract = False
        app_label = 'main'


class GeographicIntersection(Intersection):

    objects = GeoInheritanceManager()

    class Meta(object):
        abstract = False
        app_label = 'main'

    join_type_key = JoinTypeKey.GEOGRAPHIC
    # The default Token tree for a Geographic intersection uses st_intersects as the equality token
    # and uses the geographic functions as the left and right operator.
    default_tree = Token(
        leftSide=Token(
            tokenType='FUNCTION',
            tokenValue='{from_geography}',
            parameters=[
                Token(
                    tokenType="PROPERTY",
                    tokenValue="{from_attribute}"
                )
            ]
        ),
        rightSide=Token(
            tokenType='FUNCTION',
            tokenValue='{to_geography}',
            parameters=[
                Token(
                    tokenType="PROPERTY",
                    tokenValue="{to_attribute}"
                )
            ]
        ),
        tokenType="intersects",
        tokenValue="intersects"
    )

    # A geographic shape for the Primary Geography or similar DbEntity joining
    # to the the DbEntity whose FeatureBehavior has this Intersection
    # IntersectionKey.(POLYGON|CENTROID)
    from_geography = models.CharField(max_length=50, null=True)
    # A geographic shape for the target DbEntity whose FeatureBehavior has this Intersection
    # IntersectionKey.(POLYGON|CENTROID)
    to_geography = models.CharField(max_length=50, null=True)

    # These are hard-coded for now. If they need to be variable then we'll store them in the database
    from_attribute = 'wkb_geometry'
    to_attribute = 'wkb_geometry'

    @classproperty
    def polygon_to_polygon(cls):
        """
            Gets/Create a template instance that joins from polygon to polygon
        """
        return cls.objects.get_or_create(
            is_template=True,
            from_geography=GeographicKey.POLYGON,
            to_geography=GeographicKey.POLYGON)[0]


    @classproperty
    def polygon_to_centroid(cls):
        """
            Gets/Create a template instance that joins from polygon to centroid
        """
        return cls.objects.get_or_create(
            is_template=True,
            from_geography=GeographicKey.POLYGON,
            to_geography=GeographicKey.CENTROID)[0]

    @classproperty
    def centroid_to_polygon(cls):
        """
            Gets/Create a template instance that joins from polygon to centroid
        """
        return cls.objects.get_or_create(
            is_template=True,
            from_geography=GeographicKey.CENTROID,
            to_geography=GeographicKey.POLYGON)[0]


class AttributeIntersection(Intersection):
    """
        Indicates an Attribute-based intersection.
        Since the attribute values are specific to the DbEntities, there are no attributes here yet.
        The attributes are on the FeatureBehaviorIntersection
    """

    objects = GeoInheritanceManager()

    class Meta(object):
        abstract = False
        app_label = 'main'

    join_type_key = JoinTypeKey.ATTRIBUTE
    # The default Token tree for a Geographic intersection uses st_intersects as the equality token
    # and uses the geographic functions as the left and right operator.
    default_tree = Token(
        leftSide=Token(tokenType='PROPERTY', tokenValue='{from_attribute}'),
        rightSide=Token(tokenType='PROPERTY', tokenValue='{to_attribute}'),
        tokenType="=",
        tokenValue="="
    )

    # The attribute of the Primary Geography DbEntity used for attribute joins
    from_attribute = models.CharField(max_length=50, null=True)
    # The attribute of the target DbEntity used for attribute joins
    to_attribute = models.CharField(max_length=50, null=True)

    @classproperty
    def default_template(cls):
       return cls.objects.get_or_create(is_template=True)
