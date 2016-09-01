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


sc_require('views/remove_button_view');
sc_require('views/info_views/built_form/container_using_percent_of_component_item_view');


Footprint.PlacetypeComponentsUsingPrimaryComponentView = SC.View.extend({
    classNames: ['footprint-placetype-component-using-primary-component-view'],
    childViews:'titleView placetypeComponentListView'.w(),
    title: null,
    content:null,
    selection: null,

    titleView: SC.LabelView.extend({
        classNames: ['footprint-bold-title-view'],
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        layout: {height: 20, top: 3},
        textAlign: SC.ALIGN_CENTER
    }),

    placetypeComponentListView:SC.ScrollView.extend({
        layout: { left:10, right:10, top: 23, bottom: 10},

        /**
         * The container of the ComponentPercentMixin
         * Bind to the mainStoreVersion since these sometimes have to dynamically load and
         * SC seems incapable of updating the nested store with the loaded record
        */
        contentBinding: SC.Binding.oneWay('.parentView*content.mainStoreVersion'),

        contentView: SC.SourceListView.extend({
            isEnabledBinding: SC.Binding.oneWay('.content').bool(),
            rowHeight: 34,
            isEditable: YES,
            actOnSelect: NO,
            canEditContent: YES,
            canDeleteContent: YES,
            canReorderContent: YES,

            contentBinding: SC.Binding.oneWay('.parentView.parentView*content.primary_component_percent_set'),
            contentValueKey: 'name',
            selection: null,

            exampleView: Footprint.ContainerUsingPercentOfComponentItemView.extend()
        })
    })
})
