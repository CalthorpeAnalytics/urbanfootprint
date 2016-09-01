
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

from footprint.main.lib.functions import compact, map_dict
from footprint.main.models.geospatial.geometry_type_keys import GeometryTypeKey, StyleTypeKey
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.style_attribute import StyleValueContext, Style

__author__ = 'calthorpe_analytics'

def create_layer_style_for_parent_model(parent_model, style_value_context_resolver, related_field=None):
    """
        Creates the LayerStyle for the given model by iterating through all of its child instances and styling
        its parent foreign_key (e.g. BuiltForm subclasses' parent foreign key is built_form_id)
        The object created is a LayerStyle instance in the following format
        LayerStyle(
            style_attributes=[
                StyleAttribute(
                    attribute='land_use_definition__id' (or anything else representing a BuiltForm id),
                    style_value_contexts=[
                        StyleValueContext(
                            value=1,
                            symbol='=',
                            default_style: Style(
                                polygon-fill='#FFFFCC'
                            )
                        ),
                        StyleValueContext(
                            value=2,
                            symbol='=',
                            default_style: Style(
                                polygon-fill='#99FF99'
                            )
                        ),
                        ...
                    ]
                )
            ]
        )
    :param parent_model: The model that has a parent foreign key
    :param style_value_context_resolver: A function that accepts the instance as an argument and returns the correct color.
    :param related_field: Optional string to specify the related field name to reach the model whose parent
    is specified here. For instance if FooFeatures has ManyToMany built_forms, which is a collection of BuiltForm subclass instance,
    then related_field should be 'built_forms'. If built_form is simply a ForeignKey on the source model, then
    this field isn't needed
    :return: A complete default context_dict for all instances of the give model
    """
    # Using the parent foreign key (e.g. builtform_id instead of id, seems unneeded)
    parent_foreign_key = '%s' % parent_model._meta.pk.attname
    attribute = '{0}__{1}'.format(related_field, parent_foreign_key) if related_field else parent_foreign_key
    instances = list(parent_model.objects.all())

    return dict(
        geometry_type=GeometryTypeKey.POLYGON,
        style_attributes=[
            dict(
                attribute=attribute,
                opacity=1,
                style_type=StyleTypeKey.CATEGORICAL,
                style_value_contexts=compact(map(
                    # Find the StyleValueContext associated with the instance
                    style_value_context_resolver,
                    sorted(instances, key=lambda instance: instance.id)))
            )
        ]
    )

# Various utility functions for creating LayerStyle instances specific to a model instance
# These are merged with the class/(attribute) LayerStyle to create the final LayerStyle

def create_layer_style_for_related_field(related_field_path, related_model, color_lookup, color_lookup_field, visible):
    """
        Creates the CSS context_dict to use in a LayerStyle instance for the given ForeignKey model field
    :param related_field_path: If the field is a many-to-many, specify this, e.g. 'built_form__id'.
    :param related_model - Model object having items with a color_lookup_field
    :param color_lookup: A dict that maps a field of the ForeignKey model class to a color
    :param color_lookup_field: The field of the ForeignKey model that matches the keys of the color_lookup
    :return: A complete default context_dict for the give model field
    """

    def create_style_value_context(lookup_field_value, color):
        if color:
            try:
                foreign_key = related_model.objects.get(**{color_lookup_field: lookup_field_value}).id
                return StyleValueContext(
                    value=foreign_key,
                    symbol='=',
                    style=Style(
                        polygon_fill=color,
                        polygon_opacity=0.8,
                        line_color='#d2d2d5',
                        line_opacity=0.7,
                        line_width=.5
                    )
                )
            except:
                return None
        return None

    return dict(
        geometry_type=GeometryTypeKey.POLYGON,
        style_attributes=[
            dict(
                attribute=related_field_path,
                opacity=1,
                visible=visible,

                style_type=StyleTypeKey.CATEGORICAL,
                style_value_contexts=[null_style_value_context()] +
                    sorted(compact(map_dict(
                        create_style_value_context,
                        color_lookup
                    )), key=lambda style_value_context: style_value_context.value)
            )
        ]
    )

def null_style_value_context():
    """
        A simple StyleValueContext that matches 'null'
    :return:
    """
    return StyleValueContext(
        value=None,
        symbol='=',
        style=Style(
            polygon_fill='#f8fcff',
            polygon_opacity=.2,
            line_color='#CCCCCC',
            line_opacity=0.2
        )
    )


def default_model_layer_style(attribute):
    """
        TODO No longer supported. All LayerConfigurations must define layer_style dicts
        Creates a default LayerStyle for Layers that have no attribute to style.
        This will be merged with a LayerStyle subclass that matches the class and attribute
        being styled to create the final LayerStyle
    :param attribute: Creates an unstyled StyleAttribute for this attribute
    :return:
    """
    raise Exception("Empty layer style definitions are no longer supported. All Layer configurations must have a layer_style dict with at least one attribute styled")
