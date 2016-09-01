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


sc_require('views/info_views/built_form/editable_input_field_view');
sc_require('views/info_views/built_form/container_using_percent_of_component_item_view');

Footprint.PlacetypesUsingPlacetypeComponentView = SC.View.extend({

    classNames: ['footprint-placetypes-using-placetype-component-view'],
    childViews:['titleView', 'placetypePercentScrollView'],
    content: null,
    title: null,

    titleView: SC.LabelView.extend({
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        layout: {height: 20, top: 3}
    }),

    placetypePercentScrollView: SC.ScrollView.extend({
        classNames: ['footprint-placetype-percent-scroll-view'],
        layout: { left:10, right:10, top: 23, bottom: 10},
        /**
         * The container of the ComponentPercentMixin
         * Bind to the mainStoreVersion since these sometimes have to dynamically load and
         * SC seems incapable of updating the nested store with the loaded record
        */
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content.mainStoreVersion'),

        contentView: SC.SourceListView.extend({
            isEnabledBinding: SC.Binding.oneWay('.content').bool(),
            rowHeight: 34,
            isEditable: YES,
            actOnSelect: NO,

            contentBinding: SC.Binding.oneWay('.parentView.parentView*content.placetype_component_percent_set'),
            contentValueKey: 'name',
            selection: null,

            exampleView: Footprint.ContainerUsingPercentOfComponentItemView.extend()
        })
    })
})
