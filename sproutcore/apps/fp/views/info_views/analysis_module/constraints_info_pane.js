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

sc_require('views/info_views/built_form/urban_built_forms/manage_building_view');

Footprint.ConstraintsInfoPane = SC.PalettePane.extend({
    classNames: ['footprint-add-building-pane'],
    layout: { right: 300, centerY: 50, width: 450, height: 300 },
    nowShowing:function() {
        return this.getPath('context.nowShowing') || 'Footprint.EnvironmentalConstraintsManagementView';
    }.property('context').cacheable(),

    contentView: SC.ContainerView.design({
        classNames: ['footprint-add-built-form-container-view'],
        childViews: ['toggleButtonsView'],

        recordType: null,
        // The recordType is stored in the contentView of this view (the nowShowing view)
        recordTypeBinding: SC.Binding.oneWay('*contentView.recordType'),
        // Likewise for the current selectedItem
        selectedItemBinding: SC.Binding.oneWay('*contentView.selectedItem'),

        nowShowingBinding: SC.Binding.oneWay('.parentView.nowShowing'),

        toggleButtonsView: SC.SegmentedView.extend({
            layout: {top: 5, centerY:0, height:22},
            crudType: 'view',
            selectSegmentWhenTriggeringAction: YES,
            itemTitleKey: 'title',
            itemActionKey: 'action',
            itemValueKey: 'title',
            items: [
                {title: 'Environmental',  action: '', recordType:''},
                {title: 'Redevelopment', action: '', recordType:''}
            ],
            value: null
        })
    })
});
