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


sc_require('controllers/active_controller');

Footprint.SelectionPropertyController = Footprint.ActiveController.extend({

    /***
     * Bind to the singleSelection property of the the listController. When the selection changes we update
     * our content
     */
    fullContent: null,
    fullContentBinding: SC.Binding.oneWay('.listController*selection.firstObject').defaultValue(null),

    /***
     * Optionally access a property of the fullContent. If omitted the content simply binds
     * to the fullContent
     */
    contentPropertyPath: null,
    _previousContentPropertyPath: null,

    contentPropertyPathObserver: function() {
        if (!this.get('fullContent') || !this.get('contentPropertyPath'))
            return;
        if (this._previousContentPropertyPath) {
            this.removeObserver(
                this.get('fullContent'),
                '*%@'.fmt(this._previousContentPropertyPath),
                this,
                'contentPropertyPathValueDidChange');
        }
        this.addObserver(
            this.get('fullContent'),
            '*%@'.fmt(this.get('contentPropertyPath')),
            this,
            'contentPropertyPathValueDidChange');
        this._previousContentPropertyPath = this.get('contentPropertyPath');
    }.observes('.contentPropertyPath'),

    /***
     * Indicates that fullContent changed whenever the contentPropertyPath value changes
     */
    contentPropertyPathValueDidChange: function() {
        this.propertyDidChange('fullContent');
    },

    /***
     * Get/Set the content. content is either fullContent or a property of fullContent.
     * this.getPath(this.get('contentPropertyPath')) is called to return a property on the content
     */
    content: function() {
        var fullContent = this.get('fullContent');
        if (!fullContent)
            return null;
        return this.get('contentPropertyPath') ?
            fullContent.getPath(this.get('contentPropertyPath')) :
            fullContent;
    }.property('fullContent').cacheable(),
});
