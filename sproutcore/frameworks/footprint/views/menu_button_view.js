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


sc_require('views/menu_render_mixin');

Footprint.MenuButtonView = SC.ButtonView.extend({
    classNames:'footprint-menu-button-view'.w(),
    items:null,
    content:null,
    recordType: null,
    activeRecord:null,

    /***
     * Optional. The item that is selected. Optional
     *   @default null
     */
    value:null,
    /**
     * Optional. The key of the item to display in the menu item view
     *  @type string
    */
    itemTitleKey:'title',

    /**
     * The optional key of the item indicating whether or not it is checked
     *   @type string
    */
    itemCheckboxKey:null,

    /**
     * The created MenuPane
     *  @private
    */
    menu:null,

    /**
     * Creates or reveals the menu
     */
    action: function () {
        var menu = this.get('menu');
        if (!menu) {
            menu = SC.MenuPane.create(Footprint.MenuRenderMixin, {
                anchor: this,
                recordType: this.get('recordType'),
                content: null,
                // Bind to the activeRecord, which is sometimes different than the anchor's content
                // For instance, for the layer_section_view the content is the Scenario but the activeRecord is the layer
                contentBinding:SC.Binding.oneWay('.anchor.activeRecord'),
                items: this.get('items'),
                itemTitleKey:this.get('itemTitleKey'),
                itemCheckboxKey:this.get('itemCheckboxKey'),
                itemValueKey:this.get('itemValueKey')
            });
            menu.bind('selectedItem', this, 'value');
            this.set('menu', menu);
        }
        menu.popup(this);
    }
});
