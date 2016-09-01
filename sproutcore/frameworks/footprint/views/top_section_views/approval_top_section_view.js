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


sc_require('views/info_views/toggle_button_info_view');
sc_require('views/view_mixins/footprint_data_bindings_mixin');

/***
 * The pane used to edit the settings of a new or existing Feature and the DbEntity to which it is associated (if any). The saving order of this will have to first save a created DbEntity and then the Feature if a DbEntity is being created here
 * @type {*}
 */

Footprint.ApprovalTopSectionView = SC.View.extend({

    childViews: ['contentView'],

    layerName: null,
    layerNameBinding: SC.Binding.oneWay('Footprint.layerActiveController.name'),

    activeLayer: null,
    activeLayerBinding: SC.Binding.oneWay('Footprint.layerActiveController.content'),

    activeLayerBehavior: null,
    activeLayerBehaviorBinding: SC.Binding.oneWay('*activeLayer.db_entity.feature_behavior.behavior.key'),

    title: function() {
        return 'Select features from %@'.fmt(this.get('layerName'));
    }.property('layerName'),

    content: null,
    contentBinding: SC.Binding.oneWay('Footprint.featureTableController.content'),
    // The formatted content actually shown by the table
    formattedContent: null,
    formattedContentBinding: SC.Binding.oneWay('Footprint.featureTableController.formattedContent'),
    // The columns to use for the result table
    columns: null,
    columnsBinding: SC.Binding.oneWay('Footprint.featureTableController.columns'),
    // Use the active controller here so that the table doesn't refresh when we commit edits
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.featureTableController.status'),

    //two way binding for the selected feature(s)
    selection: null,
    selectionBinding: SC.Binding.from('Footprint.featureTableController.selection'),
    recordType: null,
    recordTypeBinding: SC.Binding.oneWay('Footprint.featureTableController.recordType').notEmpty(null, Footprint.Feature),
    layerSelection: null,
    layerSelectionBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController.content'),
    layerSelectionStatus: null,
    layerSelectionStatusBinding: SC.Binding.oneWay('Footprint.featureTableController.layerSelectionStatus'),

    isEnabled: function() {
        return (!(this.get('status') & SC.Record.BUSY)) && (this.get('layerSelectionStatus') & SC.Record.READY);
    }.property('layerSelectionStatus', 'status').cacheable(),

    contentView: SC.ContainerView.extend(Footprint.DataBindingsMixin, {

        activeViewProperty: null,
        activeViewPropertyBinding: SC.Binding.oneWay('Footprint.approvalQueriesController.activeView'),

        parentOneWayBindings: [ 'content', 'formattedContent', 'columns', 'status', 'recordType', 'layerSelection',
            'isEnabled', 'activeLayerBehavior', 'activeLayer'],

        selection: null,
        selectionBinding: '.parentView.selection',

        nowShowing: function () {
            if (this.getPath('activeViewProperty') && this.get('activeLayerBehavior') == 'behavior__editable_feature') {
                return '%@'.fmt(this.getPath('activeViewProperty'));
            }
            return 'Footprint.NoApprovalView';
        }.property('activeViewProperty', 'activeLayer', 'activeLayerBehavior').cacheable()
    })
});
