
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
from inflection import dasherize
import re
from footprint.main.lib.functions import map_to_dict, map_dict, compact_dict, merge
from footprint.main.models.geospatial.geometry_type_keys import GeometryTypeKey
from footprint.main.models.keys.content_type_key import ContentTypeKey
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.style_attribute import StyleAttribute
from footprint.main.utils.model_utils import model_dict

__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)


def update_or_create_layer_style(layer_style_configuration, style_key, existing_layer_style=None):
    """
        Creates a LayerStyle the StyleAttribute for cartocss styling.
        A Template is not specific to a Layer instance, rather specific to underlying Feature clss of the Layer
    :param layer_style_configuration: A dict() containing values specific to the model (i.e. the Feature subclass).
    This will be merged with layer_style that matches the subclass and 0 or more attributes of the Feature subclass
    that the Layer represents.
    :param style_key: The unique key of the template. Use the same key to share the template among instances
    :param existing_layer_style. The optional layer style class upon which the template key is named. If this is omitted,
    a generic template is created that doesn't load any predefined style info from the system.
        TODO There is no particular purpose for a Template based on only a db_entity_key at this point.
        The one based on a styled_class (Feature class) can load the template matching the class and attributes to
        provide default styling for the layer. We might have a case for having various generic default styling for a
        layer that is not based on a feature_class.
    :return:
    """
    logger.info("existing_layer_style %s" % model_dict(existing_layer_style))

    layer_style, created, updated = LayerStyle.objects.update_or_create(
        key=style_key,
        defaults=merge(
            # look first for whether the layer style exists and update otherwise create it
            model_dict(existing_layer_style) if existing_layer_style else dict(),
            dict(
                name=style_key,
                content_type=ContentTypeKey.CSS,
                # This represents the master version of the LayerStyle and will not change
                # unless the backend configuration is updated
                geometry_type=layer_style_configuration.get('geometry_type'),
                html_class=style_key
            )
        )
    )

    # iterate over the configured style attribtues and update or create new instances and cartocss
    for style_attribute_config in layer_style_configuration.get('style_attributes') or []:

        style_attribute, created, updated = StyleAttribute.objects.update_or_create(
            key=style_attribute_config.get('key') if style_attribute_config.get('key') else style_key + "__default",
            defaults=dict(
                name=style_attribute_config.get('name') if style_attribute_config.get('name') else 'Default',
                attribute=style_attribute_config.get('attribute'),
                style_type=style_attribute_config.get('style_type'),
                opacity=style_attribute_config.get('opacity') or 1,
                style_value_contexts=style_attribute_config.get('style_value_contexts')
            )
        )
        layer_style.style_attributes.add(style_attribute)
        layer_style.save()

    return layer_style

dash_array_regex = re.compile(r'(\d+,)*\d+')


def map_value(value):
    """
        Carto represents null as 'null', so we have to map it from our object None to 'null'
        Also quote string values that aren't colors
    :param value:
    :return:
    """
    if value is None:
        return "'null'"
    if isinstance(value, basestring) and \
            not value.startswith('#') and \
            not dash_array_regex.match(value):
        return '"%s"' % value
    return value


def map_selector_value(value):
    """
        Similar to `map_value`, but used in [key=value] selectors. Maps None to 'null', and all
        strings should be quoted. This allows selectors like [updated="2015-11-24T21:41:29+00:00"]
    """
    if value is None:
        return "null"  # See https://github.com/mapbox/carto/issues/75
    if isinstance(value, basestring):
        return '"%s"' % value
    return value


def build_style_string(style, separator=' '):
    """
        Creates key value pairs as a string for the given Style with the given separator
        between the paris
    :param style:
    :param separator: Default ' '
    :return:
    """

    style_string = separator.join(
        map_dict(
            lambda key, value: '{key}: {value};'.format(key=dasherize(key), value=map_value(value)),
            compact_dict(style)))

    return style_string


def create_cartocss_template(layer_style, style_attribute):
    """
        Creates a complete cartocss template for the given layer_style and given attribute.
    :return:
    """
    # logger.info("layer_style!!! %s" % layer_style)
    # logger.info("style_value_contexts!!! %s" % style_attribute.style_value_contexts)

    if not style_attribute:
        raise Exception("No attribute present in layer_style %s.style_attributes: %s" % (layer_style.get('model_class'), style_attribute))

    # Styles that are defaults of the LayerStyle or the StyleAttribute
    # Generates the string version of the cartocss for the configured attribute symbology of a given layer.
    # Line widths are modified based on pre-configured zoom level factors from the dict below
    # See below for example syntax for the carto css produced

    # Renders each StyleValueContext By zoom level. For example:
    # [zoom >= 10] {
        # [land_use_definition__id=1] {
        #   polygon-fill: #FF0000;
        #   polygon-opacity: .5;
        #   line-color: #000000;
        # }
        # [land_use_definition__id=2] {
        #   polygon-fill: #00FF00;
        #   polygon-opacity: .5;
        #   line-color: #000000;
        # }
    # ....

    if (layer_style.geometry_type == GeometryTypeKey.POINT):
        # zoom level 22 is the maximum zoom level
        zoom_style_value_contexts = [
            dict(value=22, factor=1)
        ]
    else:
        zoom_style_value_contexts = [
            dict(value=13, factor=0.5),
            dict(value=13, factor=1),
            dict(value=16, factor=2)]

    single_symbol = False if len(style_attribute.style_value_contexts) > 1 else True

    zoomed_styles = make_rules_for_zoom_levels(
        zoom_style_value_contexts, style_attribute, single_symbol)

    # the properly formed string format of the cartocss
    carto_css = '''\
.{html_class}
{{buffer-size: 50;}}
{zoom_styles_string}
'''.format(
        html_class=layer_style.id,
        zoom_styles_string='\n'.join(zoomed_styles))
    return carto_css


def make_selector(style_attribute, style_value_context, single_symbol):
    """Returns a basic [Carto]CSS selector for the given attribute/context combination."""

    if single_symbol:
        return ''

    symbol = style_value_context['symbol']

    value = map_selector_value(style_value_context['value'])

    return '''[{attribute}{symbol}{value}]'''.format(
        attribute=style_attribute.attribute,
        symbol=symbol if style_value_context['value'] is not None else '=',
        value=value)


def make_rules_for_zoom_levels(zoom_style_value_contexts, style_attribute, single_symbol):
    """Generates an iterable of strings, one for each value in zoom_style_value_contexts.

    Yields strings in the format '[zoom>=4] { some-styles... }'
    """
    for i, zoom_level in enumerate(zoom_style_value_contexts):
        yield '''[zoom{symbol}{zoom_level}] {{{styles}}}'''.format(
            symbol='<' if i == 0 else '>=',
            zoom_level=zoom_level['value'],
            styles='\n'.join(make_rule_for_zoom_level(
                zoom_level, style_attribute, style_attribute.style_value_contexts, single_symbol)))


def make_rule_for_zoom_level(zoom_level, style_attribute, style_value_contexts, single_symbol):
    """Makes a new style rule specific to a given zoom level.

    We know that we're in the style definition of another rule, so we
    know that if we're in a single-symbol rule, we don't have to open
    another style context.

    Returns strings either in the form [selector] '{ styles...}' or
    just '{ styles... }'
    """
    for style_value_context in style_value_contexts:
        if not single_symbol:
            yield '''{selector} {{{styles}}}'''.format(
                selector=make_selector(style_attribute, style_value_context, single_symbol),
                styles=make_styles_for_zoom_level(zoom_level, style_value_context))
        else:
            yield '''{styles}'''.format(
                styles=make_styles_for_zoom_level(zoom_level, style_value_context))


def make_styles_for_zoom_level(zoom_level, style_value_context):
    return build_style_string(
        map_to_dict(lambda (style, value):
                    (style, round(float(zoom_level['factor']) * float(value or 0), 2))
                    if style == "line-width" else (style, value), style_value_context['style'].iteritems()))
