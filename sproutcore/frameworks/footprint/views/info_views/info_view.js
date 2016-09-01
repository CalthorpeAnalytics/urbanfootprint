/*
 * UrbanFootprint v1.5
 * Copyright (C) 2016 Calthorpe Analytics
 *
 * This file is part of UrbanFootprint version 1.5
 *
 * UrbanFootprint is distributed under the terms of the GNU General
 * Public License version 3, as published by the Free Software Foundation. This
 * code is distributed WITHOUT ANY WARRANTY, without implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 * Public License v3 for more details; see <http://www.gnu.org/licenses/>.
 */

sc_require('views/label_view');

/**
*
* Base class for a editing. Provides a view for the title and the item itself
* @type {Class}
*/
Footprint.InfoView = Footprint.View.extend(SC.Control, {
    childViews: ['titleView', 'contentView', 'rangeView'],
    classNames: ['footprint-info-view'],

    title: null,
    // Optional parameters to pass to the resolved localized string wildcards
    valueParameters: null,
    rangeValue: null,
    // content, contentValueKey, and value work as they do with any SC.Control mixer
    // You can use content and contentValueKey or simpley value
    content: null,
    contentValueKey: null,
    value: null,

    isEditable:YES,
    titleViewLayout: {left: 0.01, height: 24, width: 0.3},

    titleView: Footprint.LabelView.extend({
        classNames: ['footprint-infoview-title-view'],
        isEnabledBinding:SC.Binding.oneWay('.parentView.isEnabled'),
        layoutBinding: SC.Binding.oneWay('.parentView.titleViewLayout'),
        toolTipBinding: SC.Binding.oneWay('.parentView.toolTip'),
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        valueParameters: SC.Binding.oneWay('.parentView.valueParameters'),
        localize: YES
    }),
    // Override this
    contentView: null,

    rangeView: SC.LabelView.extend({
        classNames: ['footprint-infoview-range-view'],
        layout: {left: .65, width: .3},
        isTextSelectable:YES,
        valueBinding: SC.Binding.oneWay('.parentView.rangeValue'),
        isVisibleBinding:SC.Binding.oneWay('.value').bool()
    }),

    toString: function() {
        return "%@:\n%@".fmt(sc_super(), this.toStringAttributes(this._toStringAttributes()));
    },

    _toStringAttributes: function() {
        return ['title', 'content']
    },

    recordTypeToInfoView: function() {
        return mapToSCObject(Footprint.InfoView.featureInfoViews(Footprint.InfoView), function(infoView) {
            return infoView.prototype.recordType ? [infoView.prototype.recordType, infoView] : null;
        })
    }.property().cacheable()
});

Footprint.InfoView.mixin({
    featureInfoViews: function(clazz) {
        return $.shallowFlatten(clazz.subclasses.map(function (subclass) {
            return [subclass].concat(Footprint.InfoView.featureInfoViews(subclass));
        }, this).compact());
    }
});
