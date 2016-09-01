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


sc_require('views/info_views/style_value_slider_info_view');
sc_require('views/info_views/color_preview_view');

Footprint.StylePickerView = SC.View.extend({
    childViews: ['styleSelectorSegmentedView', 'stylePreviewView', 'cssTextView', 'rgbSliderView', 'lineStyleView'],
    classNames: ['footprint-style-picker-view'],

    // The Footprint.Style to view/edit
    style: null,

    isEditable: YES,

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
        layout: {left: 0, width: 160, top: 0, height: 16},
        classNames: ['footprint-segmented-button-view', '.ace.sc-regular-size.sc-segment-view', 'sc-button-label'],
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
        layout: { border: 1, left: 5, top: 26, width: 150, height: 90 },

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

    /***
     * The CSS text version of the color. This can be edited and updates the color
     */
    cssTextView: SC.TextFieldView.design({
        classNames: ['color-text'],
        controlSize: SC.SMALL_CONTROL_SIZE,
        classNameBindings: ['hasAlpha'],
        isEditable: YES,
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        /***
         * True if the alpha value is not 1. This let's us adjust the text size to fit the alpha format
         */
        hasAlpha: null,
        hasAlphaBinding: SC.Binding.oneWay('.parentView*color.a').notEqual(1),
        layout: { top: 120, left: 5, width: 150, height: 30 },
        valueBinding: SC.Binding.from('.parentView*color.cssText')
    }),

    rgbSliderView: SC.View.design({
        childViews: ['redSliderInfoView', 'greenSliderInfoView', 'blueSliderInfoView', 'alphaSliderInfoView'],
        layout: { top: 0, right: 5, left:160, height:120 },

        validColor: null,
        validColorBinding: SC.Binding.oneWay('.parentView*color.isError').not(),
        isEnabledBinding: SC.Binding.and('.validColor', '.parentView.isEnabled'),
        contentBinding: SC.Binding.oneWay('.parentView.color'),

        redSliderInfoView: Footprint.StyleValueSliderInfoView.extend({
            layout: {top:0, height: 24},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'r',
            title: 'Red',
            maximum: 255
        }),

        greenSliderInfoView: Footprint.StyleValueSliderInfoView.extend({
            layout: {top:30, height: 24},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'g',
            title: 'Green',
            maximum: 255
        }),

        blueSliderInfoView: Footprint.StyleValueSliderInfoView.extend({
            layout: {top:60, height: 24},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'b',
            title: 'Blue',
            maximum: 255
        }),

        /***
         * Alpha is naturally between 0 and 1. If Alpha is 0 and any RGB becomes non-zero,
         * we turn alpha to 1. If the user is editing an RGB they obviously don't want alpha at 0,
         * but they might not notice it is set to 0
         */
        alphaSliderInfoView: Footprint.StyleValueSliderInfoView.extend({
            layout: {top:90, height: 24},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'a',
            title: 'Opacity',
            step: .01,
            minimum: 0,
            maximum: 1,
            rgbObservers: function() {
                if (this.get('content') && this.get('value') === 0 && ['r','g','b'].find(function(color) {
                        // If defined and non-zero
                        return this.get('content').get(color);
                }, this)) {
                    this.set('value', 1);
                }
            }.observes('*content.r', '*content.g', '*content.b')
        })
    }),

    lineStyleView: SC.View.extend({
        childViews: ['thicknessSliderInfoView'],
        layout: {top: 125, left: 160, right: 5},
        classNames: ['lineStyleView'],

        styleBinding: SC.Binding.oneWay('.parentView.style'),

        colorProperty: null,
        colorPropertyBinding: SC.Binding.oneWay('.parentView.colorProperty'),
        color: null,
        colorBinding: SC.Binding.oneWay('.parentView.color'),

        isBorderSelected: function() {
            return this.get('colorProperty')=='border-color';
        }.property('colorProperty').cacheable(),

        /***
         * Only make this view enabled/visible if the 'border-color' is the color property being edited
         */
        isEnabled: null,
        isEnabledBinding: SC.Binding.and('.parentView.isEnabled', '.isBorderSelected'),

        isVisibleBinding: SC.Binding.oneWay('.isEnabled'),

        thicknessSliderInfoView: Footprint.StyleValueSliderInfoView.extend({
            layout: {top:0, height: 24},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            contentBinding: SC.Binding.oneWay('.parentView.style'),
            color: null,
            colorBinding: SC.Binding.oneWay('.parentView.color'),
            /***
             * Similar to the alpha slider, if any RGB value is set to non-zero
             * assume that the user wants some line width, so set this from 0 to 1
             */
            rgbObservers: function() {
                if (this.get('isEnabled') && this.get('color') && this.get('value') === 0 && ['r', 'g', 'b'].find(function (color) {
                        // If defined and non-zero
                        return this.get('color').get(color);
                    }, this)) {
                    this.set('value', 1);
                }
            }.observes('*color.r', '*color.g', '*color.b'),

            contentValueKey: 'border-width',
            title: 'Width',
            step: 1,
            minimum: 0,
            maximum: 5
        })
    })

});
