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


/* globals Footprint */

sc_require('views/info_views/toggle_button_info_view');

Footprint.NoApprovalView = SC.View.extend({
    childViews: ['titleView'],
    classNames: ['footprint-bold-built-form-summary-title'],
    titleView: SC.LabelView.extend({
        layout: {top: 35, height: 200, width: 300},
        escapeHTML: NO,
        value: 'The current Active Layer is not configured for editing and cannot be merged to the SCAG regional dataset.'
    })
});

Footprint.ApprovalView = Footprint.View.extend({

    childViews: ['selectActiveView', 'titleView', 'querySelectView', 'approveButtonView', 'rejectButtonView',
        'selectedRowsLabelView', 'selectedRowsCountView','selectAllToggleButtonView', 'saveButtonWithStatusView',
        'sourceTableFeatureTable'],

    parentOneWayBindings: [
        'content', 'formattedContent', 'columns', 'status', 'recordType', 'layerSelection', 'isEnabled'],

    selection: null,
    selectionBinding: '.parentView.selection',

    selectActiveView: SC.SegmentedView.extend({
        classNames: ['footprint-segmented-button-view', '.ace.sc-regular-size.sc-segment-view', 'sc-button-label'],
        layout: {top: 4, height: 24, width: 160, left: 80},
        itemValueKey: 'value',
        itemTitleKey: 'title',
        itemActionKey: 'action',
        itemToolTipKey: 'toolTip',
        selectSegmentWhenTriggeringAction: YES,
        activeLayerBehavior: null,
        activeLayerBehaviorBinding: SC.Binding.oneWay('.parentView.activeLayerBehavior'),
        //only show the table if it is an editable feature selected

        items: [
            SC.Object.create({value: 'Footprint.ApprovalView', toolTip: 'Approval', title: 'Approval', action:'reenterApprovalFromMerge'}),
            SC.Object.create({value: 'Footprint.MergeView', toolTip: 'Merge', title: 'Merge', action: 'activateMergeModule'})
        ],
        value: 'Footprint.ApprovalView',
        //if the value is changed by the user set the controller which will then update the view
        valueObserver: function() {
            if (this.get('value')) {
                Footprint.approvalQueriesController.set('activeView', this.get('value'));
            }
        }.observes('value')
    }),

    titleView: SC.LabelView.extend({
        classNames: ['footprint-editable-9font-title-view'],
        value: 'Query Options:',
        layout: {left: 20, height: 12, width: 90, top: 38}
    }),
        /***
     * Selects from a list of predefined LayerSelections that represent various approval-related queries
     */
    querySelectView: Footprint.FootprintSelectView.extend({
        layout: {left: 20, width:300, top: 52, height: 24},
        contentController: Footprint.approvalQueriesController,
        itemTitleKey: 'name',
        selectionObserver: function () {
            //overrides the default selectionObserver in order to execute the approval query logic
            if (this.get('selection')) {
                var selection = this.getPath('selection.firstObject');
                var menuValue = this.getPath('menu.selectedItem.title');
                var contentConroller = this.get('contentController');
                var itemTitleKey = this.get('itemTitleKey');
                //sometimes when selecting from this button this value is null
                if (menuValue) {
                    contentConroller.selectObject(this.get('items').find(function(obj) {
                        return obj.get(itemTitleKey)==menuValue;
                    }));
                    Footprint.statechart.sendAction('doExecuteApprovalQuery', this.get('contentController'));
                }
            }
        }.observes('*menu.selectedItem.title')
    }),

    approveButtonView: SC.ButtonView.design({
        classNames: ['footprint-query-info-clear-button-view'],
        layout: {top: 110, height: 24, left: 180, width: 90},
        title: 'Approve',
        icon: sc_static('footprint:images/check_16.png'),
        isVisibleBinding: SC.Binding.oneWay('Footprint.userController.firstObject.isManager'),
        // Updates the selected features' approval_status to 'approved'.
        action: function() {
            var content = this.get('content'),
                contentValueKey = this.get('contentValueKey');
            if (content) {
                content.forEach(function(val) {
                    val.set(contentValueKey, 'approved');
                });
            }
        },

        contentValueKey: 'approval_status',
        contentBinding: 'Footprint.featuresEditController.selectedRows',
        toolTip: 'Approve Changes in Table(s)',
        isEnabledBinding: SC.Binding.and('.parentView.isEnabled', '*content.firstObject')
    }),

    rejectButtonView: SC.ButtonView.design({
        classNames: ['footprint-query-info-clear-button-view'],
        layout: {top: 110, height: 24, left: 60, width: 90},
        title: 'Reject',
        isVisibleBinding: SC.Binding.oneWay('Footprint.userController.firstObject.isManager'),
        icon: sc_static('footprint:images/clear_16.png'),
        // Updates the selected features' approval_status to 'rejected'.
        action: function() {
            var content = this.get('content'),
                contentValueKey = this.get('contentValueKey');
            if (content) {
                content.forEach(function(val) {
                    val.set(contentValueKey, 'rejected');
                });
            }
        },

        contentValueKey: 'approval_status',
        contentBinding: 'Footprint.featuresEditController.selectedRows',
        toolTip: 'Reject Edit(s)',
        isEnabledBinding: SC.Binding.and('.parentView.isEnabled', '*content.firstObject')
    }),

    selectedRowsLabelView: SC.LabelView.extend({
        classNames: ['footprint-11font-title-view'],
        layout: { top: 90, height: 16, left: 40, width: 290},
        escapeHTML: NO,
        isVisibleBinding: SC.Binding.oneWay('Footprint.userController.firstObject.isManager'),
        value: 'Highlight rows to Approve or Reject Pending edits.'
    }),

    selectedRowsCountView: SC.LabelView.extend({
        classNames: ['footprint-active-built-form-name-view', 'toolbar'],
        selectedRows: null,
        selectedRowsBinding: SC.Binding.oneWay('Footprint.featureTableController.selection'),
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        statusRows: null,
        statusBinding: SC.Binding.oneWay('.parentView.status'),

        value: function() {
            var selectedRows = this.get('selectedRows');
            if (selectedRows) {
                return '%@ %@'.fmt(selectedRows.length(),
                selectedRows.length() > 1 || selectedRows.length() == 0 ? 'Rows Selected': 'Row Selected');
            }
            return '0 Rows Selected';
        }.property('selectedRows').cacheable(),
        hint: 'No Layer Selected',
        textAlign: SC.ALIGN_CENTER,
        layout: {top: 140, height: 16, left: 100, width: 120}
    }),

    selectAllToggleButtonView: Footprint.SelectAllToggleButtonInfoView.extend({
        layout: {top: 170, left: 280,  height: 20, width: 80},
        classNames:'footprint-approval-select-all-view'.w(),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        // The controller is bound here so that we can access its selectAll property
        contentBinding: SC.Binding.from('Footprint.featureTableController'),
        // A property on the controller or content that toggles the selectAll state
        contentValueKey: 'selectAll',
        action: 'selectAllFeatures',

        selectAllFeatures: function() {
            var toggleStatus = this.getPath('content.selectAll');
            if (toggleStatus) {
                Footprint.featureTableController.selectObjects(this.get('content'));
            }
            else {
                Footprint.featureTableController.selectObject(this.getPath('content.firstObject'));
            }
        }
    }),

    saveButtonWithStatusView: Footprint.SaveButtonWithStatusView.extend({
        layout: {bottom: 10, left: 20, height: 27, width: 210},
        contentBinding: SC.Binding.oneWay('Footprint.featuresEditController.content'),
        statusBinding: SC.Binding.oneWay('Footprint.featuresEditController.featuresStatus'),
        monitorProgressOfFirstItem: YES,
        action: 'doFeaturesUpdate',
        isVisibleBinding: SC.Binding.oneWay('Footprint.userController.firstObject.isManager'),
        buttonTitle: 'Save',
        updatingTitle: 'Saving...',
        additionalContext: {
            maintainApprovalStatus: YES
        },
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
    }),

    sourceTableFeatureTable: Footprint.FeatureTableInfoView.extend({
        tableViewLayout:  {left: 0.01, right: 0.02, top: 30, bottom: 0},
        layout: {left: 350},
        itemDescriptionBinding: SC.Binding.oneWay('Footprint.approvalQueriesController*selection.firstObject.description'),
        layerSelectionFeatureLengthBinding: SC.Binding.oneWay('*layerSelection.features_count'),
        parentOneWayBindings: [
            'content', 'formattedContent', 'columns', 'status', 'recordType', 'layerSelection'],
        selectionBinding: SC.Binding.from('Footprint.featureTableController.selection'),
    })
});



Footprint.MergeView = Footprint.View.extend({
    childViews: ['selectActiveView', 'mergeLayerView', 'mergeInfoView', 'mergeButtonView', 'updatingStatusView',
        'sourceTableFeatureTable'],

    parentOneWayBindings: [
        'content', 'formattedContent', 'columns', 'status', 'recordType', 'layerSelection', 'isEnabled', 'activeLayer'],

    recordsAreUpdating: null,
    recordsAreUpdatingBinding: SC.Binding.oneWay('Footprint.mergeUpdaterToolEditController.recordsAreUpdating'),

    isOverlayVisible: function () {
        var recordsAreUpdating = this.get('recordsAreUpdating');
        if (recordsAreUpdating) {
            return recordsAreUpdating;
        }
        return NO;
    }.property('recordsAreUpdating').cacheable(),

    selectActiveView: SC.SegmentedView.extend({
        classNames: ['footprint-segmented-button-view', '.ace.sc-regular-size.sc-segment-view', 'sc-button-label'],
        layout: {top: 4, height: 24, width: 160, left: 80},
        itemValueKey: 'value',
        itemTitleKey: 'title',
        itemActionKey: 'action',
        itemToolTipKey: 'toolTip',
        selectSegmentWhenTriggeringAction: YES,
        activeLayerBehavior: null,
        activeLayerBehaviorBinding: SC.Binding.oneWay('.parentView.activeLayerBehavior'),
        //only show the table if it is an editable feature selected

        items: [
            SC.Object.create({value: 'Footprint.ApprovalView', toolTip: 'Approval', title: 'Approval', action: 'activateApprovalModule'}),
            SC.Object.create({value: 'Footprint.MergeView', toolTip: 'Merge', title: 'Merge', action: 'activateMergeModule'})
        ],
        value: 'Footprint.MergeView',

        //if the value is changed by the user set the controller which will then update the view
        valueObserver: function() {
            if (this.get('value')) {
                Footprint.approvalQueriesController.set('activeView', this.get('value'));
            }
        }.observes('value')
    }),

    mergeLayerView: SC.View.extend({
        classNames: ['footprint-current-query-view'],
        childViews: ['titleView', 'activeLayerLabelView'],
        layout: {left: 20, width: 310, top: 40, height: 40},
        activeLayer: null,
        activeLayerBinding: SC.Binding.oneWay('.parentView.activeLayer'),
        titleView: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            value: 'Layer to Merge:',
            layout: {height: 12, left: 5}
        }),

        activeLayerLabelView: SC.LabelView.extend({
            classNames: ['footprint-active-built-form-name-view', 'toolbar'],
            valueBinding: '*parentView.activeLayer.name',
            hint: 'No Layer Selected',
            textAlign: SC.ALIGN_CENTER,
            layout: {top: 18, height: 16, left: 15, right: 15}
        })
    }),

    mergeInfoView: SC.LabelView.extend({
        classNameBindings: ['isEditable'],
        layout: {top: 90, left: 56, width: 250, height: 50},
        isEditable: NO,
        escapeHTML: NO,
        activeLayer: null,
        activeLayerBinding: SC.Binding.oneWay('Footprint.layerActiveController.content'),
        activeLayerStatus: null,
        activeLayerStatusBinding: SC.Binding.oneWay('*activeLayer.status'),
        value: function() {
            if (this.get('activeLayer')) {
                return 'All Approved records will be merged into the County Version of the %@.'.fmt(this.getPath('activeLayer.name'));
            }
            else return 'All Approved records will be merged into the County Version of the active layer.';
        }.property('activeLayer', 'activeLayerStatus')
    }),

    mergeButtonView: SC.ButtonView.design({
        classNames: ['footprint-query-info-clear-button-view', 'theme-button', 'theme-button-green'],
        layout: {top: 150, height: 20, left: 130, width: 60},
        // Don't enable merge unless there is at least one item to merge
        isEnabledBinding: SC.Binding.and('.parentView.isEnabled', 'Footprint.featuresActiveController.length'),
        title: 'Merge',
        action: 'doMergeLayer',
        isVisibleBinding: SC.Binding.oneWay('Footprint.userController.firstObject.isManager'),
        // This contains the single Footprint.MergeUpdaterTool instance
        contentBinding: 'Footprint.mergeUpdaterToolEditController.content',
        activeLayer: null,
        activeLayerBinding: '*parentView.activeLayer.dbEntityKey',
        targetConfigEntity: null,
        targetConfigEntityBinding: SC.Binding.oneWay('Footprint.regionActiveController.content'),
        toolTip: 'Merge Active Layer into Master Version'
    }),

    updatingStatusView: Footprint.UpdatingOverlayView.extend({
        layout: {top: 150, height: 27, left:200, width: 110},
        isOverlayVisibleBinding: SC.Binding.oneWay('.parentView.isOverlayVisible'),
        previousStatus: NO,
        title: 'Merging..',

        justUpdatedObserver: function() {
            if (this.didChangeFor('justUpdatedObserver', 'isOverlayVisible')) {
                if (this.get('isOverlayVisible') === YES && this.get('previousStatus') === NO) {
                    this.set('previousStatus', YES);
                    this.set('justUpdated', NO);
                }
                else if (this.get('isOverlayVisible') === NO && this.get('previousStatus') === YES) {
                    // Indicate just saved if we are still showing the last saved content
                    this.set('justUpdated', YES);
                    this.set('previousStatus', NO);
                    this.set('Footprint.mergeUpdaterToolEditController.recordsAreUpdating', NO);
                }
            }
        }.observes('.isOverlayVisible')
    }),

    sourceTableFeatureTable: Footprint.FeatureTableInfoView.extend({
        tableViewLayout:  {left: 0.01, right: 0.02, top: 30, bottom: 0},
        layout: {left: 350},
        itemDescription: 'Approved Edits - To be Merged',
        layerSelectionFeatureLengthBinding: SC.Binding.oneWay('*layerSelection.features_count'),
        parentOneWayBindings: [
            'content', 'formattedContent', 'columns', 'status', 'recordType', 'layerSelection'],
        selectionBinding: SC.Binding.from('Footprint.featureTableController.selection'),
    })
});
