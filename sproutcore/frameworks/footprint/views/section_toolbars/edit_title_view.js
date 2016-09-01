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


sc_require('views/section_toolbars/edit_button_view');
sc_require('views/section_toolbars/title_view');

Footprint.EditTitleView = Footprint.TitleView.extend({
    classNames: "footprint-edit_title-view".w(),
    childViews: 'labelView editView'.w(),
    layout: {left: 0, width: .9},
    recordType: null,
    activeRecord: null,
    menuItems: null,
    controlSize: null,
    content: null,
    //icon: sc_static('images/section_toolbars/pulldown.png'),
    icon: null,
    title: null,

    editView: Footprint.EditButtonView.extend({
        layout: {left: 2, width: 26},
        layoutBinding: SC.Binding.oneWay('.parentView.editViewLayout'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        recordTypeBinding: SC.Binding.oneWay(parentViewPath(1, '.recordType')),
        activeRecordBinding: SC.Binding.oneWay(parentViewPath(1, '.activeRecord')),
        parentViewMenuItems: null,
        parentViewMenuItemsBinding: SC.Binding.oneWay('.parentView.menuItems'),
        menuItems: function () {
            if (this.getPath('parentViewMenuItems')) {
                return this.get('parentViewMenuItems');
            }
            else {
                return this.get('defaultMenuItems');
            }
        }.property('parentViewMenuItems').cacheable(),

        controlSizeBinding: SC.Binding.oneWay('.parentView.controlSize'),
        // Only show the title if the icon is not set
        title: function() {
            if (!this.get('icon')) {
                return this.getPath('parentView.title');
            }
        }.property('icon'),
        iconBinding: SC.Binding.oneWay('.parentView.icon')
    })
});
