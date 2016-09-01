
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

from __future__ import absolute_import


from unittest import TestCase

from footprint.main.models.geospatial.geometry_type_keys import GeometryTypeKey
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.style_attribute import StyleAttribute

from . import style_configuration
# from footprint.main.management.commands.footprint_init import FootprintInit
# from footprint.main.models.config.project import Project


class TestStyleConfiguration(TestCase):

    def test_cartocss_blank(self):
        layer_style = LayerStyle()
        style_attribute = StyleAttribute()
        css = style_configuration.create_cartocss_template(layer_style, style_attribute)

        # TODO: handle 'None' class better
        expected_style = '''.None
{buffer-size: 50;}
[zoom<13] {}
[zoom>=13] {}
[zoom>=16] {}
'''
        self.assertEquals(expected_style, css)

    def test_cartocss_blank_point(self):
        layer_style = LayerStyle(geometry_type=GeometryTypeKey.POINT)
        style_attribute = StyleAttribute()
        css = style_configuration.create_cartocss_template(layer_style, style_attribute)

        # TODO: handle 'None' class better
        expected_style = '''.None
{buffer-size: 50;}
[zoom<22] {}
'''
        self.assertEquals(expected_style, css)

    def test_cartocss_single_symbol(self):
        """Single symbols should have just """
        layer_style = LayerStyle(id='parcels')
        style_attribute = StyleAttribute(style_value_contexts=[
            {'value': 'two', 'symbol': '!=', 'style': {'border': '1px solid black'}}],
            attribute='number')
        css = style_configuration.create_cartocss_template(layer_style, style_attribute)

        expected_style = '''.parcels
{buffer-size: 50;}
[zoom<13] {border: 1px solid black;}
[zoom>=13] {border: 1px solid black;}
[zoom>=16] {border: 1px solid black;}
'''
        self.assertEquals(expected_style, css)

    def test_cartocss_multi_symbol(self):
        layer_style = LayerStyle(id='parcels')
        style_attribute = StyleAttribute(style_value_contexts=[
            {'value': 'one', 'symbol': '=', 'style': {'border': '1px solid red'}},
            {'value': 'two', 'symbol': '!=', 'style': {'border': '1px solid black'}}],
            attribute='number')
        css = style_configuration.create_cartocss_template(layer_style, style_attribute)

        expected_style = '''.parcels
{buffer-size: 50;}
[zoom<13] {[number="one"] {border: 1px solid red;}
[number!="two"] {border: 1px solid black;}}
[zoom>=13] {[number="one"] {border: 1px solid red;}
[number!="two"] {border: 1px solid black;}}
[zoom>=16] {[number="one"] {border: 1px solid red;}
[number!="two"] {border: 1px solid black;}}
'''
        self.assertEquals(expected_style, css)

    def test_cartocss_scaled_line_width(self):
        """Line width should be scaled appropriately with the zoom level, to maintain readability."""
        layer_style = LayerStyle(id='parcels')
        style_attribute = StyleAttribute(style_value_contexts=[
            {'value': 'two', 'symbol': '!=', 'style': {'line-width': '7'}}],
            attribute='number')
        css = style_configuration.create_cartocss_template(layer_style, style_attribute)

        expected_style = '''.parcels
{buffer-size: 50;}
[zoom<13] {line-width: 3.5;}
[zoom>=13] {line-width: 7.0;}
[zoom>=16] {line-width: 14.0;}
'''
        self.assertEquals(expected_style, css)

    def test_cartocss_scaled_line_width_multi_symbol(self):
        """Line width should be scaled appropriately with the zoom level, to maintain readability."""
        layer_style = LayerStyle(id='parcels')
        style_attribute = StyleAttribute(style_value_contexts=[
            {'value': 'one', 'symbol': '=', 'style': {'line-width': '5'}},
            {'value': 'two', 'symbol': '!=', 'style': {'line-width': '7'}}],
            attribute='number')
        css = style_configuration.create_cartocss_template(layer_style, style_attribute)

        expected_style = '''.parcels
{buffer-size: 50;}
[zoom<13] {[number="one"] {line-width: 2.5;}
[number!="two"] {line-width: 3.5;}}
[zoom>=13] {[number="one"] {line-width: 5.0;}
[number!="two"] {line-width: 7.0;}}
[zoom>=16] {[number="one"] {line-width: 10.0;}
[number!="two"] {line-width: 14.0;}}
'''
        self.assertEquals(expected_style, css)

    def test_cartocss_escaped_value(self):
        """Make sure strings like dates are escaped correctly."""
        layer_style = LayerStyle(id='parcels')
        style_attribute = StyleAttribute(style_value_contexts=[
            {'value': '2015-11-24-T21:41:29+00:00', 'symbol': '=', 'style': {'border': '1px solid red'}},
            {'value': None, 'symbol': '!=', 'style': {'border': '1px solid black'}}],
            attribute='number')
        css = style_configuration.create_cartocss_template(layer_style, style_attribute)

        expected_style = '''.parcels
{buffer-size: 50;}
[zoom<13] {[number="2015-11-24-T21:41:29+00:00"] {border: 1px solid red;}
[number=null] {border: 1px solid black;}}
[zoom>=13] {[number="2015-11-24-T21:41:29+00:00"] {border: 1px solid red;}
[number=null] {border: 1px solid black;}}
[zoom>=16] {[number="2015-11-24-T21:41:29+00:00"] {border: 1px solid red;}
[number=null] {border: 1px solid black;}}
'''
        self.assertEquals(expected_style, css)
