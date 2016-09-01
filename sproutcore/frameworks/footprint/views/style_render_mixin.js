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
 * Allows a view to mix dynamic css style values into the render and update method
 * @type {{}}
 */
Footprint.StyleRenderMixin = {
    /***
     * The style to apply to the styled div. This is also searched when updating, so something is required
     */
    styleClass: 'footprint-style',
    /***
     * By default the styled element is a child of the view's main div
     * The child element is created in render rather than a separate view to save time.
     * Set this to NO to style the view's main div
     */
    renderStyleInChildElement: YES,

    /***
     * A Footprint.Style record
     */
    style: null,
    /***
     * A bound to the style record so that display properties will update when they are changed
     */
    fill_color: null,
    fill_colorBinding: SC.Binding.oneWay('*style.background-color'),
    line_color: null,
    line_colorBinding: SC.Binding.oneWay('*style.border-color'),
    line_width: null,
    line_widthBinding: SC.Binding.oneWay('*style.border-width'),

    /***
     * A wrapper around the Footprint.Style that
     * converts between cartoss and css and delivers css to the render/update methods
     *
     */
    cssObject: function() {
        return Footprint.CssObject.create({
            style: this.get('style')
        });
    }.property('style').cacheable(),

    // TODO we need to put these in CssObject
    cartoToCss: function() {
        return {
            'line-cap' : 'line-cap',
            'line-join': 'line-join',
            'outline/line-width': 'outline-width',
            'outline/line-color': 'outline-color',
            'outline/line-opacity': 'outline-opacity',
            'outline/line-dasharray': 'outline-style',
            'outline/line-join': 'outline/line-join',
            'outline/line-cap': 'outline/join-cap',
            'mainline/line-dasharray': 'mainline/line-dasharray',
            'mainline/line-join': 'mainline/line-join',
            'mainline/line-cap': 'mainline/line-cap',
            'marker-width': 'marker-width',
            'marker-fill': 'marker-fill',
            'marker-line-color': 'marker-line-color',
            'marker-line-width': 'marker-line-width'
        }
    }.property().cacheable(),

    /***
     * Call this from the mixer's render method
     * Renders the color swab. By default this is a div with the
     * background-color, background-icon, border-color, border-width, and border-style
     */
    renderStyle: function(context) {
        var renderStyleInChildElement = this.get('renderStyleInChildElement');
        if (renderStyleInChildElement)
            context = context.begin();
        context.addClass(this.getPath('theme.classNames'))
            .addClass(['sc-view', this.get('styleClass'), 'sc-view:before', 'sc-view:after']);
        /***
         * For layout properties we need to set the style for non-view divs
         * For view div use the adjust method with the special layout properties
         */
        var style = this.get('style');
        if (style) {
            /***
             * If we are rendering the style in an unmanaged child element,
             * we need to set layout properties. Otherwise use adjust instead
             * to edit this views layout to match the css layout properties
             */
            if (renderStyleInChildElement)
                context.setStyle(style.get('css'));
            else {
                context.setStyle(style.get('nonLayoutCss'));
                this.adjust(style.get('cssAsLayout'));
            }
        }
        context.update();
        if (renderStyleInChildElement)
            context.end();
    },

    /***
     * Updates the color. This searches for the element by class name and updates the background-color thereof
     * @param $context
     */
    updateStyle: function($context) {
        var style = this.get('style');
        if (!style)
            return;
        var renderStyleInChildElement = this.get('renderStyleInChildElement');
        var $div = this.get('renderStyleInChildElement') ?
            $context.find('.%@'.fmt(this.get('styleClass'))) :
            $context;
        if (renderStyleInChildElement) {
            $div.css(style.get('css'))
        }
        else {
            $div.css(style.get('nonLayoutCss'));
            this.adjust(style.get('cssAsLayout'));
        }
    }
};
