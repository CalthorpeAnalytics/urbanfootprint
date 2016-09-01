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


/***
 * Provides the stylable attributes of the edit Layer's Feature class.
 * The content of this is simply a list of attribute names
 * The selected attribute results in the setting of the Footprint.styleableAttributesEditController selected item
 * There isn't necessarily a Footprint.StyleAttribute for each attribute that can be created
 * The corresponding Footprint.StyleAttribute is created by the state chart when one is needed
 */
Footprint.styleableAttributesEditController = SC.ArrayController.create({
    allowsEmptySelection: NO,
    layer:null,
    layerBinding: SC.Binding.from('Footprint.layerEditController.content'),
    layerStatus: null,
    layerStatusBinding: SC.Binding.oneWay('*layer.status'),
    dbEntityBinding: SC.Binding.oneWay('*layer.db_entity'),
    store: null,
    storeBinding: SC.Binding.oneWay('*layer.store'),
    content: null,
    contentBinding: SC.Binding.oneWay('*layer.medium.style_attributes'),
    contentStatus: null,
    contentStatusBinding: SC.Binding.oneWay('*content.status'),

    firstSelectableObject: function() {
        var activeStyleKey = this.getPath('layer.active_style_key');
        var styleAttributes = this.getPath('layer.medium.style_attributes') || [];
        var firstAttribute = styleAttributes.find(function(style_attribute) {
            return style_attribute.get('key')==activeStyleKey;
        });

        if (firstAttribute) {
            return firstAttribute;
        }
        // fall back the the current medium's style.
        return this.getPath('layer.medium.style_attributes.firstObject');
    }.property('content', 'contentStatus'),

    activeStyleObserver: function () {
        if (this.get('selection') && this.getPath('selection.firstObject')) {
            this.setPath('layer.active_style_key', this.getPath('selection.firstObject.key'));
        }
    }.observes('.selection', '*selection.firstObject.key')
});


Footprint.styleTypeEditController = SC.ArrayController.create({
    allowsEmptySelection: NO,
    styleAttribute: null,
    styleAttributeBinding: SC.Binding.from('Footprint.styleableAttributesEditController*selection.firstObject'),

    content: [
        SC.Object.create({style_type: 'single'}),
        SC.Object.create({style_type: 'categorical'}),
        SC.Object.create({style_type: 'quantitative'})
    ],

    styleAttributeObserver: function() {
        if (this.get('styleAttribute') && this.getPath('styleAttribute.style_type')) {
            var selectedStyle = this.getPath('styleAttribute.style_type');
            this.selectObject(this.get('content').find(function(obj) {
                return obj.get('style_type')==selectedStyle;
            }));
        }
    }.observes('.styleAttribute'),

    isNotSingle: function() {
        if (this.get('selection') && this.getPath('selection.firstObject')) {
            return this.getPath('selection.firstObject.style_type') == 'categorical' ||
                this.getPath('selection.firstObject.style_type') == 'quantitative';
        }
        return NO;
    }.property('selection').cacheable(),

    styleTypeDidChangeObserver: function() {
        if (this.get('selection') && this.getPath('selection.firstObject.style_type')) {
            var selectedStyleType = this.getPath('selection.firstObject.style_type');
            this.setPath('styleAttribute.style_type', selectedStyleType);
        }
        else {
            this.setPath('styleAttribute.style_type', null);
        }
    }.observes('*selection.firstObject.style_type')
});


Footprint.styleAttributeEditController = SC.ArrayController.create({
    allowsEmptySelection: NO,
    styleAttribute: null,
    styleAttributeBinding: SC.Binding.from('Footprint.styleableAttributesEditController*selection.firstObject'),
    dbEntity: null,
    dbEntityBinding: SC.Binding.oneWay('Footprint.dbEntityFeatureSchemaEditController.dbEntity'),
    fields: null,
    fieldsBinding: SC.Binding.oneWay('Footprint.dbEntityFeatureSchemaEditController.content'),
    status: null,
    statusBinding: SC.Binding.oneWay('*content.status'),
    isNotSingle: null,
    isNotSingleBinding: SC.Binding.oneWay('Footprint.styleTypeEditController.isNotSingle'),

    content: function() {
        if (this.get('isNotSingle')) {
            return this.get('fields');
        }
        return [];
    }.property('isNotSingle', 'fields').cacheable(),

    firstSelectableObject: function() {
        if (this.get('content') && this.get('content').length > 0) {
            //currently styled attribute of the style
            var attribute = this.getPath('styleAttribute.attribute');
            //select from the content the current styled column name
            return this.get('content').find(function(obj) {
                return obj.get('field')==attribute;
            });
        }
    }.property('content', 'styleAttribute', 'status').cacheable(),

    attributeDidChangeObserver: function() {
        if (this.get('selection') && this.getPath('selection.firstObject.field')) {
            var selectedAttribute = this.getPath('selection.firstObject.field');
            var selectedStyle = this.getPath('styleAttribute');
            selectedStyle.setIfChanged('attribute', selectedAttribute);
        }
        else {
            this.setPath('styleAttribute.attribute', null);
        }
    }.observes('*selection.firstObject.field')
});


Footprint.styleValueContextsEditController = SC.ArrayController.create({
    allowsEmptySelection: NO,
    content: null,
    contentBinding: SC.Binding.from('Footprint.styleableAttributesEditController*selection.firstObject.style_value_contexts'),
    status: null,
    statusBinding: SC.Binding.oneWay('*content.status'),
    dbEntity: null,
    dbEntityBinding: SC.Binding.oneWay('Footprint.dbEntityFeatureSchemaEditController.dbEntity'),

    contentDidChange: function() {
        this.invokeOnce('doUpdateContent');
    }.observes('.selection','.status'),

    doUpdateContent: function() {
        this.notifyPropertyChange('content');
    }
});


Footprint.FeatureCategoryController = SC.ArrayController.create({
    recordType: Footprint.FeatureCategoryAttribute,
    isProcessing: NO,
    allowsEmptySelection: NO
});

Footprint.FeatureQuantitativeController = SC.ArrayController.create({
    recordType: Footprint.FeatureQuantitativeAttribute,
    isProcessing: NO,
    allowsEmptySelection: NO
});

Footprint.CachedSelectedLayer = SC.ObjectController.create({
    currentSelection: null
});
