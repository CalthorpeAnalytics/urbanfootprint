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


sc_require('views/item_views/list_item_view');
/**
 *
 * Displays a Layer as an item of a list by binding a Footprint.Layer to the content.
 * This also requires
 */
Footprint.LayerItemView = Footprint.ListItemView.extend({

    /***
     * Render specific content based on the content type
     * @param content
     * @param context
     * @param key
     * @param value
     * @param working
     * @returns {*}
     */
    renderForTreeLevel: function (content, context, key, value, working) {
        // The innermost level for Style objects
        var itemClass;
        if (content.get('isStyle')) {
            this.renderStyle(context);
            itemClass = this.get('labelStyleClass');
        } else if (content.get('isLayer')) {
            // The middle level for Layer objects
            if (content.getPath('hasCheckBox')) {
                itemClass = this.get('labelLayerClassToggle');
            } else {
                itemClass = this.get('labelLayerClassNoToggle');
            }
        } else if (content.get('isAttribute')) {
            // The middle level for Layer objects
            if (content.get('hasCheckBox')) {
                itemClass = this.get('labelAttributeClassToggle');
            }
            else {
                itemClass = this.get('labelAttributeClassNoToggle');
            }
        } else {
            // Default for the outermost level, Layer Categories
            sc_super();
        }
        if (itemClass) {
            context.begin()
                .addClass(this.getPath('theme.classNames'))
                .addClass(['sc-view', 'sc-label-view', itemClass])
                .push(content.get(key))
                .end();
        }
        return value;
    }
});
