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


Footprint.LayerStyle = Footprint.Medium.extend({
    geometry_type: SC.Record.attr(String),
    style_attributes: SC.Record.toMany('Footprint.StyleAttribute', {nested:YES}),

    layer: function() {
        return this.get('parentRecord');
    }.property('parentRecord').cacheable(),
});


Footprint.LayerStyle.mixin({
    apiRecordType: function() {
        return Footprint.Medium;
    },
});

/***
 * The style_attributes of a Footprint.LayerStyle
 * These contain an attribute representing the attribute of a Footprint.Feature subclass,
 * along with a list of Footprint.StyleValueContexts, which each represent
 * one styled quantile (i.e. a fill-color, outline-color, etc for attribute value <,>,=,<=, or >= a certain value)
 */
Footprint.StyleAttribute = Footprint.Record.extend({
    name: SC.Record.attr(String),
    key: SC.Record.attr(String),
    attribute: SC.Record.attr(String),
    opacity: SC.Record.attr(Number),
    //the type of style for the given attribute ie. single, categorical, quantitative
    style_type: SC.Record.attr(String),
    // Indicates if the instance is visible by default (such as a layer's visibility on a map)
    style_value_contexts: SC.Record.toMany('Footprint.StyleValueContext', {nested:YES}),

    visible: SC.Record.attr(Boolean, {defaultValue: NO}),

    applicationVisible: null,

    isDefault: function() {
        var key = this.get('key');
        if (!key || key.endsWith('__default'))
            return true;
        return false;
    }.property('key').cacheable(),

    visibleObserver: function() {
        this.setIfChanged('applicationVisible', this.get('visible'));
    }.observes('.visible'),

    _nestedProperties: function() {
        return ['style_value_contexts'];
    }
});

/***
 * A fill, outline, etc representing a certain attribute value, either <,>,=,<=, or >= the value
 */
Footprint.StyleValueContext = Footprint.Record.extend({
    // The value of the context. This might be an integer to represent an exact match,
    // or it can be an integer or a float to represent a > or < value
    value: SC.Record.attr(String),
    // =, <. >, <=, or >=. The equality or comparison symbol
    // For inequalities, the limit of the range is derived from other StyleValueContexts
    // For example, if this record is value: 50, symbol: '>' and a sibling is value:70, symbol: '<',
    // the effective range of this style is > 50 and <= 70
    symbol: SC.Record.attr(String),
    /***
     * Holds all style settings for the value or range indicated by value and symbol
     */
    style: SC.Record.toOne('Footprint.Style', {nested:YES}),

    relatedRecordType: null,
    relatedRecordTypeBinding: SC.Binding.oneWay('*parentRecord.relatedRecordType').defaultValue(null),

    /***
     * For attribute that represent the id of a related record, this
     * returns the instance of that record for the id
     */
    relatedRecord: function() {
        var relatedRecordType = this.get('relatedRecordType');
        var value = this.get('value');
        if (relatedRecordType && value != null) {
            return this.get('store').find(relatedRecordType, this.get('value'));
        }
    }.property('relatedRecordType', 'value').cacheable(),

    /***
     * The name shown is a combination of the value and the (in)equality symbol
     * It also includes the related record instance toString if this is a related attribute
     */
    name: function () {
        var relatedRecord = this.get('relatedRecord');
        if (!this.get('value')) {
            return 'null (Matches features that have a null value)';
        }
        return '%@ %@%@'.fmt(this.get('symbol'), this.get('value'), relatedRecord ? ' %@'.fmt(relatedRecord.toString()) : '')
    }.property('value', 'symbol', 'relatedRecord').cacheable(),

    _nestedProperties: function() {
        return ['fill', 'outline']
    },

    /***
     * Creates needed child records.
     * @private
     */
    _createSetup: function(sourceRecord) {
        sc_super();
        this.set('fill', this.get('store').createRecord(Footprint.Style, {
            // Default fill to white
           color: "rgba(1,1,1,1)"
        }, Footprint.Record.generateId()));
        this.set('outline', this.get('store').createRecord(Footprint.Style, {
            // Default outline to black
            color: "rgba(0,0,0,1)"
        }, Footprint.Record.generateId()));
    }
});

/***
 * Manages cartocss properties from the backend and converts them to css for the front end
 */
Footprint.Style = Footprint.Record.extend({
    'polygon-fill': SC.Record.attr(String),
    'polygon-opacity': SC.Record.attr(Number),
    'line-color': SC.Record.attr(String),
    'line-opacity': SC.Record.attr(Number),
    'line-width': SC.Record.attr(Number),
    'marker-fill': SC.Record.attr(String),
    'marker-width': SC.Record.attr(Number),
    'marker-line-color': SC.Record.attr(String),
    'marker-line-width': SC.Record.attr(Number),

    /***
     * Outputs a dict of css
     * @returns {*}
     */
    css: function() {
        return mapToObject(
            ['background-color', 'border-color', 'border-width', 'box-sizing'],
            function(attr)  { return [attr, this.get(attr)] },
            this);
    }.property('background-color', 'border-color', 'border-width').cacheable(),

    /***
     * Return layout properties as an object to use with SC.View.adjust
     * We need to set the layout rather than set styles for divs tied to views.
     * If we were to set the css it will be overwritten by the layout
     */
    cssAsLayout: function() {
        return {
            border: this.get('border-width')
        };
    }.property('border-width').cacheable(),

    nonLayoutCss: function() {
        return removeKeys(this.get('css'), ['border-width']);
    }.property('css').cacheable(),

    /***
     * We want to always apply this css style to keep the div from growing as we add a border
     */
    'box-sizing': 'border-box',

    /***
     * Merge polygon-fill with polygon-opacity to create background-color
     * @param dct
     * @returns {*}
     */
    'background-color': function(propKey, value) {
        return this.colorProperty(propKey, value, ['polygon-fill', 'marker-fill'], 'polygon-opacity');
    }.property('polygon-fill', 'polygon-opacity').cacheable(),

    'border-color': function(propKey, value) {
        return this.colorProperty(propKey, value, ['line-color', 'marker-line-color'], ['line-opacity']);
    }.property('line-color', 'line-opacity', 'marker-line-color').cacheable(),

    'border-width': function(propKey, value) {
        return this.widthProperty('border-width', value, ['line-width', 'marker-line-width']) || 3 ;
    }.property('line-width', 'marker-width').cacheable(),


    /***
     * gets/set  css/cartocsss properties
     * @param cssAttribute:
     * @param value:
     * @param cartoColorAttributes: Singular or array. If array will use the first
     * attribute with an existing value. Failing that the first attribute
     * @param cartoOpacityAttributes: Singular or array. If array will use the first
     * attribute with an existing value. Failing that the first attribute
     * @returns {*}
     */
    colorProperty: function(cssAttribute, value, cartoColorAttributes, cartoOpacityAttributes) {
        var cartoColorAttribute = cartoColorAttributes.forEach ?
        firstOrNull(cartoColorAttributes.filter(function(attr) { return this.get(attr); }, this)) || cartoColorAttributes[0] :
            cartoColorAttributes;
        var cartoOpacityAttribute = cartoOpacityAttributes.forEach ?
        firstOrNull(cartoOpacityAttributes.filter(function(attr) { return this.get(attr); }, this)) || cartoOpacityAttributes[0] :
            cartoOpacityAttributes;

        var color;
        if (value !== undefined) {
            // Set the polygon-fill and polygon-opacity from value
            color = SC.Color.from(value);
            this.set(cartoColorAttribute, color.toHex());
            this.set(cartoOpacityAttribute, color.get('a'));
            return color.get('cssText')
        }
        else {
            // If no fill return transparent
            if (!this.get(cartoColorAttribute))
                return SC.Color.create({a:0}).get('cssText');
            color = SC.Color.from(this.get(cartoColorAttribute) || "#000");
        }
        if (this.get(cartoOpacityAttribute) != null) // 0 is ok
            color.set('a', this.get(cartoOpacityAttribute));
        return color.get('cssText');
    },

    widthProperty: function(cssAttribute, value, cartoAttributes) {
        if (value !== undefined) {
            // Find the cartoAttribute that's already defined and update it
            // Failing that set the first one
            var done = false;
            cartoAttributes.forEach(function(cartoAttribute) {
                if (!done && this.get(cartoAttribute)) {
                    this.set(cartoAttribute, value);
                    done = true;
                }
            }, this);
            if (!done)
                this.set(cartoAttributes[0], value)
        }
        var ret = null;
        // Find the first cartoAttribute with a valuprogressOverlayViewe
        cartoAttributes.forEach(function(cartoAttribute) {
            ret = ret || this.get(cartoAttribute)
        }, this);
        return ret || 0;
    }
});
