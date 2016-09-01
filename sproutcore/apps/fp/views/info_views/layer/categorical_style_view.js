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


sc_require('views/loading_overlay_view');
sc_require('views/info_views/layer/layer_style_picker_view');

Footprint.CategoricalStyleView = SC.View.extend({
    childViews: ['topBarView', 'overlayView', 'symbologyScrollView', 'stylePickerView'],
    content: null,
    contentBinding: SC.Binding.from('Footprint.styleValueContextsEditController.arrangedObjects'),
    selection: null,
    selectionBinding: SC.Binding.from('Footprint.styleValueContextsEditController.selection'),
    status: null,
    statusBinding: SC.Binding.oneWay('*content.status'),

    isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),

    topBarView: SC.View.extend({
        layout: {height: 20, left: 10, right: 10},
        childViews: ['styledView', 'valueView', 'addAllValuesButton', 'addButtonView'],
        backgroundColor: 'lightgrey',

        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),

        selection: null,
        selectionBinding: SC.Binding.from('.parentView.selection'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),


        styledView: SC.LabelView.extend({
            classNames: ['footprint-10font-title-view'],
            layout: {left: 5, width: 30, height: 16, top: 5},
            value: 'Style'
        }),

        valueView: SC.LabelView.extend({
            classNames: ['footprint-10font-title-view'],
            layout: {left: 60, height: 16, top: 5, width: 40},
            value: 'Value'
        }),

        addAllValuesButton: SC.ButtonView.extend({
            classNames: ['footprint-add-button-view'],
            layout: {right: 85, width: 95, height: 18, top: 2},
            controlSize: SC.SMALL_CONTROL_SIZE,
            action: 'loadFeatureAttributes',
            symbologyType: 'categorical',
            recordType: Footprint.FeatureCategoryAttribute,
            loadingController: Footprint.FeatureCategoryController,
            toolTip: 'Add all unique values of the selected table attribute',
            canAddValues: function() {
                if(!this.get('attribute') || this.get('attribute') =='None') {
                    return NO;
                }
                return YES;
            }.property('attribute').cacheable(),
            db_entity: null,
            db_entityBinding: SC.Binding.oneWay('Footprint.styleableAttributesEditController.dbEntity'),
            attribute: null,
            attributeBinding: SC.Binding.oneWay('Footprint.styleableAttributesEditController*selection.firstObject.attribute'),
            isEnabledBinding: SC.Binding.and('.parentView.isEnabled',
                                             '.canAddValues'),
            title: 'Add All Values'
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
        isVisibleBinding: SC.Binding.oneWay('Footprint.FeatureCategoryController.isProcessing'),
        showLabel: YES,
        title: 'Finding All Unique Values...'
    }),

    symbologyScrollView: SC.ScrollView.extend({
        layout: {top: 20, right: 10, bottom: 140, left: 10},
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        selection: null,
        selectionBinding: SC.Binding.from('.parentView.selection'),

        contentView: SC.SourceListView.extend({
            classNames: ['footprint-layer-source-list'],
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.parentView.content'),
            selection: null,
            selectionBinding: SC.Binding.from('.parentView.parentView.selection'),
            status: null,
            statusBinding: SC.Binding.oneWay('*content.status'),
            rowHeight: 20,
            actOnSelect: NO,
            displayProperties: ['content'],

            exampleView: SC.View.extend(SC.Control, {
                childViews: ['styleView', 'valueView', 'removeButtonView'],
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

                valueView: SC.LabelView.extend({
                    classNames: ['footprint-11font-title-view'],
                    layout: {left: 40, height: 16, top: 2, right: 16},
                    valueBinding: SC.Binding.oneWay('.parentView*content.value')
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
