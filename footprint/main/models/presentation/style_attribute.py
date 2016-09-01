# coding=utf-8

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
from django.db import models
from picklefield import PickledObjectField
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager


__author__ = 'calthorpe_analytics'
logger = logging.getLogger(__name__)


class StyleAttribute(models.Model):

    objects = GeoInheritanceManager()
    name = models.CharField(max_length=200, null=True, blank=True)
    key = models.CharField(max_length=200, null=True, blank=True)
    attribute = models.CharField(max_length=200, null=True, blank=True)
    style_type = models.CharField(max_length=40, null=True, blank=True)
    opacity = models.FloatField(default=1)
    style_value_contexts = PickledObjectField(default=lambda: [])

    visible = models.BooleanField(default=False)

    class Meta(object):
        app_label = 'main'


class StyleValueContext(dict):
    """
        The styling for the certain value of an attribute
        This contains that value as well as an (in)equality operator and a reference to the Style instance
    """

    def __init__(self, value, symbol='=', style=None):
        # The attribute value or min/max value that this instance represents
        self['value'] = value
        # =, <. >, <=, or >=. The equality or comparison symbol
        # For inequalities, the limit of the range is derived from other StyleValueContexts
        # For example, if this record is value: 50, symbol: '>' and a sibling is value:70, symbol: '<',
        # the effective range of this style is > 50 and <= 70
        self['symbol'] = symbol
        # Holds a Style instance containing style settings for the value or range indicated by value and symbol
        self['style'] = Style(**(style or {}))

    def __getattr__(self, attr):
        return self[attr] if attr in self else super(StyleValueContext, self).__getattr__(self, attr)


class Style(dict):
    """
        Various style attributes matching cartocss attributes
    """

    def __init__(self,
                 polygon_fill=None, polygon_opacity=None,
                 line_color=None, line_width=None, line_opacity=None,
                 marker_fill=None, marker_width=None, marker_line_color=None,
                 marker_line_width=None, **kwargs):
        self['polygon-fill'] = polygon_fill
        self['polygon-opacity'] = polygon_opacity
        self['line-color'] = line_color
        self['line-width'] = line_width
        self['line-opacity'] = line_opacity

        self['marker-fill'] = marker_fill
        self['marker-width'] = marker_width
        self['marker-line-color'] = marker_line_color
        self['marker-line-width'] = marker_line_width
        # Support arbitrary other styles
        for key, value in kwargs.items():
            self[key] = value

    def __getattr__(self, attr):
        return self[attr] if attr in self else super(Style, self).__getattr__(self, attr)


class ZoomLevelStyleValueContext(StyleValueContext):
    """
       Holds the style for a certain zoom level.
       Merges with the StyleValueContext to compute zoom level calibrated line widths for each zoom level
    """

    def __init__(self, value, factor):
        self['value'] = value
        self['factor'] = factor
