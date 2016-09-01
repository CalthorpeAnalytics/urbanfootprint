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



Footprint.LayerStyleLeftSideView = SC.View.extend({
    layout: { width: 240, bottom: 40},
    childViews:['labelViews', 'styleLayerAttributesListView'],
    selectedLayer: null,
    content: null,
    selection: null,

    labelViews: SC.View.extend({
        childViews: ['layerToStyleView', 'activeLayerLabelView', 'activeStyleLabelView', 'activeLayerNameView',
            'styledAttributesView'],
        layout: { height: 120 },
        selectedLayer: null,
        selectedLayerBinding: SC.Binding.oneWay('.parentView.selectedLayer'),
        selection: null,
        selectionBinding: SC.Binding.from('.parentView.selection'),

        layerToStyleView: SC.LabelView.extend({
            classNames: ['footprint-11font-title-view'],
            layout: {top: 5, height: 16, left: 5},
            value: 'Current Layer:',
            textAlign: SC.ALIGN_LEFT
        }),

        activeLayerLabelView: SC.LabelView.extend({
            classNames: ['footprint-selected-style-layer-title'],
            layout: {top: 21, height: 24, left: 10},
            valueBinding: SC.Binding.oneWay('.parentView*selectedLayer.name'),
            textAlign: SC.ALIGN_LEFT
        }),

        activeStyleLabelView: SC.LabelView.extend({
            classNames: ['footprint-11font-title-view'],
            layout: {bottom: 45, height: 16, left: 5},
            value: 'Active Layer Style:',
            textAlign: SC.ALIGN_LEFT
        }),

        activeLayerNameView: SC.TextFieldView.extend({
            classNames: ['footprint-active-style-title'],
            layout: {bottom: 25, height: 20, left: 10},
            valueBinding: SC.Binding.from('.parentView*selection.firstObject.name'),
            isEnabledBinding: SC.Binding.oneWay('.parentView*selection.firstObject.isDefault').not(),
            textAlign: SC.ALIGN_LEFT
        }),

        styledAttributesView: SC.LabelView.extend({
            classNames: ['footprint-11font-title-view'],
            layout: {bottom: 0, height: 16, left: 5},
            value: 'Saved Layer Styles:',
            textAlign: SC.ALIGN_LEFT
        })
    }),

    styleLayerAttributesListView: SC.View.extend({
        layout: {top: 125, left: 10},
        childViews: ['topBarView', 'attributeScrollView'],
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        selection: null,
        selectionBinding: SC.Binding.from('.parentView.selection'),

        topBarView: SC.View.extend({
            layout: {height: 20},
            childViews: ['styledAttributeView', 'styledTypeView', 'addButtonView'],
            backgroundColor: 'lightgrey',
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),

            styledTypeView: SC.LabelView.extend({
                classNames: ['footprint-10font-title-view'],
                layout: {left: 14, width: 50, height: 14, top: 3},
                value: 'Style Type'
            }),
            styledAttributeView: SC.LabelView.extend({
                classNames: ['footprint-10font-title-view'],
                layout: {left: 82, height: 14, top: 3, right: 35},
                value: 'Styled Attribute'
            }),
            addButtonView: SC.ButtonView.extend({
                layout: {right: 2, width: 29, height: 18, top: 2},
                controlSize: SC.SMALL_CONTROL_SIZE,
                action: 'addStyleAttribute',
                icon: sc_static('images/plus_icon12.png'),
                content: null,
                contentBinding: SC.Binding.oneWay('.parentView.content')
            })
        }),

        attributeScrollView: SC.ScrollView.extend({
            layout: {top: 20},
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            selection: null,
            selectionBinding: SC.Binding.from('.parentView.selection'),

            contentView: SC.SourceListView.extend({
                content: null,
                contentBinding: SC.Binding.oneWay('.parentView.parentView.content'),
                selection: null,
                selectionBinding: SC.Binding.from('.parentView.parentView.selection'),
                status: null,
                statusBinding: SC.Binding.oneWay('*content.status'),
                rowHeight: 30,
                actOnSelect: NO,

                exampleView: SC.View.extend(SC.Control, {
                    childViews: ['styleName', 'styleTypeView', 'attributeView', 'removeButtonView'],
                    classNames: ['footprint-style-attribute-list-example-view'],
                    content: null,
                    contentBinding: SC.Binding.oneWay('.content'),

                    styleName: SC.LabelView.extend({
                        classNames: ['footprint-10font-title-view'],
                        layout: {left: 5, right: 18, height: 14, top: 2},
                        valueBinding: SC.Binding.oneWay('.parentView*content.name')
                    }),

                    styleTypeView: SC.LabelView.extend({
                        classNames: ['footprint-editable-9font-title-view'],
                        layout: {left: 14, width: 80, height: 14, top: 15},
                        valueBinding: SC.Binding.oneWay('.parentView*content.style_type').transform(function (type) {
                            if (isNaN(type)) {
                                return type.capitalize()
                            }
                            return type
                        })
                    }),

                    attributeView: SC.LabelView.extend({
                        layout: {left: 85, height: 14, top: 15, right: 18},
                        classNames: ['footprint-editable-9font-title-view'],
                        styleType: null,
                        styleTypeBinding: SC.Binding.oneWay('.parentView*content.style_type'),
                        attribute: null,
                        attributeBinding: SC.Binding.oneWay('.parentView*content.attribute'),
                        value: function () {
                            if (this.get('attribute') && this.get('styleType') && this.get('styleType') != 'single') {
                                return this.get('attribute')
                            }
                            return 'None'
                        }.property('attribute', 'styleType').cacheable()
                    }),

                    removeButtonView: SC.ImageButtonView.extend({
                        layout: {top: 9, left: 215},
                        image: 'remove-icon',
                        action: 'removeStyleAttribute',
                        content: null,
                        isEnabledBinding: SC.Binding.oneWay('.parentView.content.isDefault').not(),
                        contentBinding: SC.Binding.oneWay('.parentView.content')
                    })
                })
            })
        })
    })
});
