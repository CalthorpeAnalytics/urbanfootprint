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


sc_require('mixins/selected_item');
sc_require('views/section_toolbars/title_view');

Footprint.ToolbarView = SC.View.extend(Footprint.SelectedItem, {
    layout: {height: 17},

    childViews: 'titleView'.w(),
    classNames: "footprint-toolbar-view".w(),
    contentNameProperty:null,

    title: null,
    /**
     * An observable object keyed by view name and valued by the title to display for each configured view.
     * The given value of the labelView will be formatted to specify the controller.name property
     */
    titles: null,

    /**
     * The view which actually shows the main title of the whatever section of the app the TitlebarView is describing
     * The title is formed by combining titles.labelView with the controller.name or "Loading controller.name"
     * if the latter isn't READY
     */
    titleView: Footprint.TitleView.extend({
        contentNamePropertyBinding:SC.Binding.oneWay('.parentView.contentNameProperty'),
        titleBinding: SC.Binding.oneWay('.parentView.title'),
        contentBinding: SC.Binding.oneWay('.parentView.content')
    })
});
