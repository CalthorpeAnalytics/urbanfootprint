
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

from picklefield import PickledObjectField
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.name import Name
from footprint.main.mixins.scoped_key import ScopedKey
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.utils.utils import resolve_model


class PresentationConfiguration(ScopedKey, Name):
    """
        Configures what db_entities are representation as PresentationMedia in a presentation, and which of those are
        initially visible in the presentation. This class will likely add all kinds of other configuration options.
        Everything is stored in a PickledObjectField for flexibility
    """
    objects = GeoInheritanceManager()

    data = PickledObjectField()

    class Meta(object):
        app_label = 'main'


class ConfigurationData(object):
    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)

    presentation_media_configurations = []


class PresentationMediumConfiguration(object):
    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)
    db_entity_key = None
    built_form_set_key = None
    # Optional sorting priority from 1 to 100. 1 is highest priority. 0 is equivalent to no priority
    sort_priority = 0
    # Optional list of attributes of the instance. Listed from highest to lowest priority. Unlisted attributes will
    # be lower priority and sorted alphabetically
    attribute_sort_priority = []
    # Optionally specify a class name here to scope the instance to limit this configuration to the class/subclasses of the
    # given config entity
    # This needs to be a string since it will be persisted
    scope = None

    @property
    def class_scope(self):
        """
            Resolve the actual model class, since it's non-trivial to store in the database
        :return:
        """
        if not self.scope:
            return None
        model = resolve_model('main.{0}'.format(self.scope))
        if not model:
            raise Exception("Could not resolve model: " + 'main.{0}'.format(self.scope))
        return model


class LayerConfiguration(PresentationMediumConfiguration):
    """
        The data configuration for the Layer instances
    """
    def __init__(self, **kwargs):
        super(LayerConfiguration, self).__init__(**kwargs)
    # If True, make the layer initially visible in the UI. Default False
    visible = False
    library_keys = []
    # A list of class/table attributes that should be stylable by the user
    # The name used should match the attribute name on the model, whether on the main model or a related model
    # A LayerStyle that indicates what keys are needed to fill out the Layer's css template. These keys should
    # have default values and may be single values, lists, ranges, or dict themselves. The structure is set as
    # the context of the Layer's Template's LayerStyle. This dict is then copied to the Layer's context property
    # where its values can be modified by a user to customize the layer styling
    layer_style = dict()
    column_alias_lookup =dict()
    # The class upon which to create the template for the layer
    # This is only used by import layer_configurations since layer configurations derive
    # their style class from the Feature class that they represent
    # import layer_configurations will generally just set this to Feature so to match
    # the generic Feature style files
    style_class = None
    # Set true for LayerConfigurations that are used as templates for creating configurations for new layers
    is_template_layer_configuration = False
