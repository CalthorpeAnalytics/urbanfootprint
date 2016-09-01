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

sc_require('views/info_views/layer/layer_style_picker_view');
sc_require('views/loading_overlay_view');


Footprint.QuantitativeStyleView = SC.View.extend({
    childViews: ['topBarView', 'overlayView', 'symbologyScrollView', 'stylePickerView'],
    content: null,
    contentBinding: SC.Binding.from('Footprint.styleValueContextsEditController.arrangedObjects'),
    selection: null,
    selectionBinding: SC.Binding.from('Footprint.styleValueContextsEditController.selection'),
    status: null,
    statusBinding: SC.Binding.oneWay('*content.status'),

    topBarView: SC.View.extend({
        layout: {height: 20, left: 10, right: 10},
        childViews: ['styledView', 'valueView', 'addAllValuesButton', 'addButtonView', 'removeButtonView'],
        backgroundColor: 'lightgrey',

        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),

        selection: null,
        selectionBinding: SC.Binding.from('.parentView.selection'),

        styledView: SC.LabelView.extend({
            classNames: ['footprint-10font-title-view'],
            layout: {left: 5, width: 30, height: 16, top: 5},
            value: 'Style'
        }),

        valueView: SC.LabelView.extend({
            classNames: ['footprint-10font-title-view'],
            layout: {left: 80, height: 16, top: 5, width: 40},
            value: 'Value'
        }),

        addAllValuesButton: SC.ButtonView.extend({
            classNames: ['footprint-add-button-view'],
            layout: {right: 85, width: 115, height: 18, top: 2},
            controlSize: SC.SMALL_CONTROL_SIZE,
            action: 'loadFeatureAttributes',
            symbologyType: 'quantitative',
            recordType: Footprint.FeatureQuantitativeAttribute,
            loadingController: Footprint.FeatureQuantitativeController,
            canAddValues: function() {
                if(!this.get('attribute') || this.get('attribute') =='None') {
                    return NO;
                }
                return YES;
            }.property('attribute'),
            isEnabledBinding: SC.Binding.and('.parentView.isEnabled',
                                             '.canAddValues'),
            db_entity: null,
            db_entityBinding: SC.Binding.oneWay('Footprint.styleableAttributesEditController.dbEntity'),
            attribute: null,
            attributeBinding: SC.Binding.oneWay('Footprint.styleableAttributesEditController*selection.firstObject.attribute'),
            title: 'Add Value Ranges'
        }),

        addButtonView: SC.ButtonView.extend({
            layout: {right: 10, width: 29, height: 18, top: 2},
            controlSize: SC.SMALL_CONTROL_SIZE,
            action: 'addStyleValueContext',
            icon: sc_static('images/plus_icon12.png'),
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content')
        })
    }),

    overlayView: Footprint.LoadingOverlayView.extend({
        layout: {top: 20, right: 10, bottom: 140, left: 10, zIndex: 999},
        isVisibleBinding: SC.Binding.oneWay('Footprint.FeatureQuantitativeController.isProcessing'),
        showLabel: YES,
        title: 'Generating Quantiles...'
    }),

    symbologyScrollView: SC.ScrollView.extend({
        layout: {top: 20, right: 10, bottom: 140, left: 10},
        content: null,
        contentBinding: SC.Binding.from('.parentView.content'),
        selection: null,
        selectionBinding: SC.Binding.from('.parentView.selection'),

        contentView: SC.SourceListView.extend({
            classNames: ['footprint-layer-source-list'],
            content: null,
            contentBinding: SC.Binding.from('.parentView.parentView.content'),
            selection: null,
            selectionBinding: SC.Binding.from('.parentView.parentView.selection'),
            status: null,
            statusBinding: SC.Binding.oneWay('*content.status'),
            rowHeight: 20,
            actOnSelect: NO,

            exampleView: SC.View.extend(SC.Control, {
                childViews: ['styleView', 'symbolView', 'valueView', 'removeButtonView'],
                classNames: ['footprint-style-attribute-list-example-view'],

                styleView: SC.View.extend(Footprint.StyleRenderMixin, {
                    styleClass:'footprint-style-medium-color',
                    displayProperties:['style', 'fill_color', 'line_color', 'line_width'],
                    renderStyleInChildElement: NO,
                    status: null,
                    statusBinding: SC.Binding.oneWay('.parentView.status'),
                    styleBinding: SC.Binding.oneWay('.parentView*content.style'),

                    render: function(context) {
                        sc_super();
                        // Style swab
                        this.renderStyle(context);
                    },
                    update: function($context) {
                        // Style swab
                        this.updateStyle($context);
                    }
                }),

                symbolView: SC.LabelView.extend({
                    classNames: ['footprint-11font-title-view'],
                    layout: {left: 40, height: 16, top: 2, width: 30},
                    valueBinding: SC.Binding.from('.parentView*content.symbol')
                }),

                valueView: SC.TextFieldView.extend({
                    classNames: ['footprint-11font-title-view'],
                    layout: {left: 70, top: 2, width: 65, bottom: 2},
                    nestedStoreValue: null,
                    nestedStoreValueBinding: SC.Binding.from('.parentView*content.value'),
                    value: function(propKey, value) {
                        if (typeof(value) !== 'undefined' && !isNaN(value)) {
                            //set the nested store value as a float by default after user enters new value
                            this.set('nestedStoreValue', value == '' ? null : parseFloat(value));
                            return value;
                        }
                        else {
                            // return the nested store value when the user has not updated anything
                            if (this.get('nestedStoreValue')) {
                                return this.get('nestedStoreValue');
                            }
                        }
                    }.property('nestedStoreValue').cacheable()
                }),
                removeButtonView: SC.ImageButtonView.extend({
                    layout: {top: 4, left: 330},
                    image: 'remove-icon',
                    action: 'removeStyleValueContext',
                    content: null,
                    contentBinding: SC.Binding.oneWay('.parentView.content')
                })
            })
        })
    }),

    stylePickerView: Footprint.LayerStylePickerView.extend({
        layout: { right: 20, height: 130, left: 10, bottom: 0},
        styleBinding: SC.Binding.from('.parentView*selection.firstObject.style')
    })
});
