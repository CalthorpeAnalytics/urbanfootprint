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
 * Previews a brighter or darker version of the parent color.
 * If the button is clicked the parentView.color is set to this color
 * @type {Class|*}
 */
Footprint.ColorPreviewView = SC.ImageButtonView.design({
    classNames: ['footprint-color-sub-preview'],
    displayProperties: ['backgroundColor'],
    /***
     * The color bound to the parentView or similar. This is the base color that is updated
     * to the previewColor value when the view is clicked.
     */
    color: null,

    /***
     * The factor by which to change color for the previewColor.
     * This can be less than 1 to darken the color and greater than 1 to brighten it
     */
    factor: null,

    /***
     * css value of the color. Used for updating properties
     */
    cssText: null,
    cssTextBinding: SC.Binding.oneWay('*color.cssText'),

    /***
     * A color that changes the value of the color property.
     * This is set as the backgroundColor style and updates the color when clicked.
     */
    previewColor: null,
    previewColorBinding: SC.Binding.oneWay('*updatedColor.validCssText'),

    /***
     * Checks for errors
     */
    validColor: null,
    validColorBinding: SC.Binding.oneWay('.color.isError').not(),

    backgroundColor: function() {
        return this.get('isEnabled') ?
            this.get('parentColor') :
            'grey';
    }.property('isEnabled', 'previewColor').cacheable(),

    action: function() {
        this.setPath('color.cssText', this.get('previewColor'));
    },

    /***
     * Creates a copy of the color property updated by a certain factor.
     * The alpha value is hard-coded to 1
     * @param factor
     * @returns {SC.Observable}
     */
    updatedColor: function() {
        var color = this.get('color');
        if (!color) {
            return;
        }
        var ret = color.mult(this.get('factor') || 1);
        ret.set('a', 1);
        return ret;
    }.property('factor', 'color')
});
