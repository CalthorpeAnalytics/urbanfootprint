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


sc_require('views/section_toolbars/toolbar_view');
sc_require('views/section_toolbars/title_view');
sc_require('views/section_toolbars/edit_title_view');

/**
 * Extends TitlebarView to add an edit button view
 * @type {*}
 */
Footprint.EditingToolbarView = Footprint.ToolbarView.extend({

    childViews: 'titleView'.w(),
    classNames: "footprint-editing-toolbar-view".w(),
    content: null,
    contentNameProperty: null,
    recordType: null,
    activeRecord: null,
    menuItems: null,
    controlSize: null,
    title: null,
    icon: sc_static('images/section_toolbars/pulldown.png'),

    // This contains the title and the pull down
    titleView: Footprint.EditTitleView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.titleViewLayout'),
        titleBinding: SC.Binding.oneWay('.parentView.title'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        contentNamePropertyBinding:SC.Binding.oneWay('.parentView.contentNameProperty'),
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        activeRecordBinding: SC.Binding.oneWay('.parentView.activeRecord'),
        menuItemsBinding: SC.Binding.oneWay('.parentView.menuItems'),
        controlSizeBinding: SC.Binding.oneWay('.parentView.controlSize'),
        iconBinding: SC.Binding.oneWay('.parentView.icon')
    })
});
