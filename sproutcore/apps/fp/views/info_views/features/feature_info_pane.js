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


sc_require('views/info_views/query/query_info_view');
sc_require('views/info_views/features/modal_feature_summary_info_view');
sc_require('views/info_views/features/modal_feature_query_info_view');
sc_require('views/info_views/features/feature_edit_info_view');

/***
 * The pane used to edit the settings of a new or existing Feature and the DbEntity to which it is associated (if any). The saving order of this will have to first save a created DbEntity and then the Feature if a DbEntity is being created here
 * @type {*}
 */


Footprint.FeatureInfoPane = Footprint.InfoPane.extend({
    classNames: "footprint-feature-info-view opaque".w(),
    // context passed in upon creation. This may contain 'nowShowing'
    context: null,

    // Indicates that this pane can be closed whenever another modal wants to open.
    // This is a non-modal pane, thus it's possible to open something else in the meantime.
    closeForNewModal: YES,

    recordType: null,
    recordTypeBinding: SC.Binding.oneWay('Footprint.layerActiveController.featureRecordType'),
    content:null,
    contentBinding: SC.Binding.oneWay('Footprint.featuresActiveController.content'),
    selection: null, // TODO always null for now
    summaryContent:null,
    summaryContentBinding: SC.Binding.oneWay('Footprint.featureAggregatesTableController.content'),
    summarySelection: null, // TODO always null for now
    layerSelection: null,
    layerSelectionBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController.content'),

    layout: { top: 0, width: 950, right: 0, height: 550 },

    /***
     * This checks context for nowShowing. You can override this property with a hard-coded nowShowing
     */
    nowShowing: function(key, value) {
        // Getter
        if (value === undefined) {
            return this._nowShowing || this.getPath('context.nowShowing') || 'Footprint.ModalFeatureSummaryInfoView';
        }
        // Setter
        else {
            this._nowShowing = value;
            return value;
        }
    }.property('context').cacheable(),

    contentView: SC.TabView.design({
        selectSegmentWhenTriggeringAction: YES,

        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        selection: null,
        selectionBinding: '.parentView.selection',
        recordType: null,
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),

        summaryContent: null,
        summaryContentBinding: SC.Binding.oneWay('.parentView.summaryContent'),
        summarySelection: null,
        summarySelectionBinding: '.parentView.summarySelection',

        layerSelection: null,
        layerSelectionBinding: SC.Binding.oneWay('.parentView.layerSelection'),

        layout: {top: 10},
        itemTitleKey: 'title',
        itemValueKey: 'value',
        items: [
            {title: 'Summary', value: 'Footprint.ModalFeatureSummaryInfoView'}
            // TODO untested
//            {title: 'Revisions', value: 'Footprint.ModalFeatureRevisionsInfoView'}
        ],
        // Two way binding so that the view can receive the initial value from the parent but also change it
        nowShowingBinding: '.parentView.nowShowing'
    })


});
