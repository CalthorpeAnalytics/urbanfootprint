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


sc_require('views/info_views/layer/layer_style_value_slider_info_view');
sc_require('views/info_views/color_preview_view');
sc_require('views/info_views/editable_field_button_view');

Footprint.LayerStylePickerView = SC.View.extend({
    childViews: ['styleSelectorSegmentedView', 'stylePreviewView', 'rgbSliderView', 'lineStyleView'],
    classNames: ['footprint-style-picker-view'],

    // The Footprint.Style to view/edit
    style: null,

    init: function() {
        this._color = SC.Color.create();
        return sc_super();
    },

    destroy: function() {
        this._color.destroy();
        return sc_super();
    },

    /**
     * The color css style currently being edited by the slider and css value controller
     */
    colorProperty: 'background-color',

    /***
     * The css color of the color style being edited
     * This or the color wrapper property is bound to
     * the color picker controls and is updated by those controls
     */
    styleColorCss: function(propKey, value) {
        var style = this.getPath('style');
        if (!style)
            return;
        if (value !== undefined) {
            style.setIfChanged(this.get('colorProperty'), value);
        }
        return style.getPath(this.get('colorProperty'));
    }.property('style', 'colorProperty').cacheable(),

    _color: null,

    /***
     * An SC.Color version of the styleColorCss for the currentColorProperty.
     * This getter/setter keeps them synced
     */
    color: function() {
        // Keep the color.cssText synced to the styleColorCss
        if ((this._color.get('cssText') || '').toUpperCase() !== (this.get('styleColorCss') || '').toUpperCase()) {
            this.setPathIfChanged('_color.cssText', this.get('styleColorCss'))
        }
        return this._color;
    }.property('styleColorCss').cacheable(),

    /***
     * Since only the color.cssText changes, not the color itself, use this observer
     */
    cssTextObserver: function() {
        var value = this.getPath('color.cssText');
        // When the color.cssText value changes, update the styleColorCss to match`the _color
        if ((value || '').toUpperCase() !== (this.get('styleColorCss') || '').toUpperCase()) {
            this.set('styleColorCss', this._color.get('cssText'));
        }
    }.observes('*color.cssText'),

    /***
     * Allows the user to choose between editing the border and fill (when available)
     */
    styleSelectorSegmentedView: SC.SegmentedView.extend({
        layout: {left: 8, width: 90, top: 5, height: 12},
        classNames: ['footprint-segmented-button-view', '.ace.sc-regular-size.sc-segment-view', 'sc-button-label'],
        controlSize: SC.SMALL_CONTROL_SIZE,
        itemValueKey: 'value',
        itemTitleKey: 'title',
        itemActionKey: 'action',
        itemToolTipKey: 'toolTip',
        selectSegmentWhenTriggeringAction: YES,

        items: [
            SC.Object.create({title: 'Fill', value: 'background-color', toolTip: 'Edit the fill style'}),
            SC.Object.create({title: 'Border', value: 'border-color', toolTip: 'Edit the border style'})
        ],
        valueBinding: SC.Binding.from('.parentView.colorProperty')
    }),

    /***
     * Shows the fill and border color and provides shortcuts to adjust them incrementally
     */
    stylePreviewView: SC.View.extend(Footprint.StyleRenderMixin, {
        classNames: ['style-preview'],
        // backgroundColor is a special property of view
        // we might be able to remove this since we're upding styles in render/update
        displayProperties: ['style', 'css'],
        layout: { border: 1, left: 5, top: 24, width: 100, height: 62 },

        // Tells StyleRenderMixin to style the main div instead of creating a child div
        renderStyleInChildElement: NO,

        /**
         * The active Footprint.Style
         */
        style: null,
        styleBinding: SC.Binding.oneWay('.parentView.style'),

        /***
         * The Active color of the style (the fill or outline)
         */
        color: null,
        colorBinding: SC.Binding.from('.parentView.color'),

        /***
         * The css of the style. This is only used as a displayProperty
         */
        css: null,
        cssBinding: SC.Binding.oneWay('*style.css'),

        // Unused for now. Maybe fix and use elsewhere
        brighterColorPreviewView: Footprint.ColorPreviewView.extend({
            layout: { border: 2, left: 10, top: 10, width: 20, height: 20 },
            colorBinding: SC.Binding.oneWay('.parentView.color'),
            factor: 1.25,
            isEnabledBinding: SC.Binding.and('.validColor', '.parentView.isEnabled')
        }),

        // Unused for now. Maybe fix and use elsewhere
        darkerColorPreviewView: Footprint.ColorPreviewView.extend({
            layout: { border: 2, right: 10, bottom: 10, width: 20, height: 20 },
            colorBinding: SC.Binding.oneWay('.parentView.color'),
            factor:.75,
            isEnabledBinding: SC.Binding.and('.validColor', '.parentView.isEnabled')
        }),

        render: function(context) {
            this.renderStyle(context);
            sc_super();
        },

        update: function($context) {
            this.updateStyle($context);
        }
    }),

    rgbSliderView: SC.View.design({
        childViews: ['redSliderInfoView', 'greenSliderInfoView', 'blueSliderInfoView', 'opacityInfoView', 'cssTextView'],
        layout: { top: 20, right: 5, left:110, height:120 },

        validColor: null,
        validColorBinding: SC.Binding.oneWay('.parentView*color.isError').not(),
        isEnabledBinding: SC.Binding.and('.validColor', '.parentView.isEnabled'),
        contentBinding: SC.Binding.oneWay('.parentView.color'),

        redSliderInfoView: Footprint.LayerStyleValueSliderInfoView.extend({
            layout: {top:0, height: 20},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'r',
            title: 'R',
            maximum: 255
        }),

        greenSliderInfoView: Footprint.LayerStyleValueSliderInfoView.extend({
            layout: {top:22, height: 20},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'g',
            title: 'G',
            maximum: 255
        }),

        blueSliderInfoView: Footprint.LayerStyleValueSliderInfoView.extend({
            layout: {top:44, height: 20},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'b',
            title: 'B',
            maximum: 255
        }),

        /***
         * Alpha is naturally between 0 and 1. If Alpha is 0 and any RGB becomes non-zero,
         * we turn alpha to 1. If the user is editing an RGB they obviously don't want alpha at 0,
         * but they might not notice it is set to 0
         */
        opacityInfoView: SC.View.extend({
            childViews: ['titleView', 'inputFieldView'],
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            content: null,
            contentBinding: SC.Binding.from('.parentView.content'),
            layout: {width: 65, height:34, top: 70, left: 0},

            titleView: SC.LabelView.design({
                classNames: ['footprint-editable-9font-title-view'],
                layout: { top: 20, left: 5},
                localize: true,
                value: 'Opacity'
            }),
            inputFieldView: Footprint.EditableFieldButtonView.design({
                classNames: ['slider-value'],
                layout: {height: 20},
                isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
                valueBinding: SC.Binding.from('.parentView*content.a'),
                valueStep: .1,
                minimum: 0,
                maximum: 1,
                validator: function() {
                    return SC.Validator.Number.create({places:1});
                }.property().cacheable()
            })
        }),
        /***
         * The CSS text version of the color. This can be edited and updates the color
         */
        cssTextView: SC.View.extend({
            childViews: ['titleView', 'inputFieldView'],
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            color: null,
            colorBinding: SC.Binding.from('.parentView.content'),
            layout: { top: 70, right: 5, width: 135, height: 34 },

            titleView: SC.LabelView.design({
                classNames: ['footprint-editable-9font-title-view'],
                layout: { top: 20, left: 5},
                localize: true,
                value: 'Color (Hex)'
            }),
            inputFieldView: SC.TextFieldView.design({
                classNames: ['layer-color-text'],
                controlSize: SC.SMALL_CONTROL_SIZE,
                classNameBindings: ['hasAlpha'],
                isEditable: NO,
                isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
                /***
                 * True if the alpha value is not 1. This let's us adjust the text size to fit the alpha format
                 */
                hasAlpha: null,
                hasAlphaBinding: SC.Binding.oneWay('.parentView*color.a').notEqual(1),
                layout: {height: 20 },
                valueBinding: SC.Binding.from('.parentView*color.cssText')
            })
        })
    }),

    lineStyleView: SC.View.extend({
        childViews: ['titleView', 'inputFieldView'],
        layout: {width: 65, height:34, top: 90, left: 20},
        style: null,
        styleBinding: SC.Binding.oneWay('.parentView.style'),

        titleView: SC.LabelView.design({
            classNames: ['footprint-editable-9font-title-view'],
            layout: { top: 20, left: 5},
            localize: true,
            value: 'Line-Width'
        }),
        inputFieldView: Footprint.EditableFieldButtonView.design({
            classNames: ['slider-value'],
            layout: {height: 20},
            valueBinding: SC.Binding.from('.parentView*style.border-width'),
            valueStep: 1,
            minimum: 0,
            maximum: 20,
            validator: function() {
                return SC.Validator.Number.create({places:0});
            }.property().cacheable()
        })
    })
});
