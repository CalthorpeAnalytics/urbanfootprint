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

/**
 * View to list an individual editable record. This is the exampleView of Footprint.EditRecordsSelectView
 */
Footprint.EditRecordView = SC.View.extend(SC.Control, {
    layout: { height: 24 },
    childViews: 'nameLabelView copyButtonView deleteButtonView'.w(),
    classNameBindings: ['isNew:new-record', 'isDirty:dirty-record'],
    /***
     * The layout of the nameLabelView
     */
    nameLabelViewLayout: { left: 48, top: 0.3},
    /***
     * The property of the content to use for the record name. Default 'name'
     */
    contentNameProperty: 'name',

    status: null,
    statusBinding: SC.Binding.oneWay('*content.status'),

    isNew: function() {
        return this.get('status') === SC.Record.READY_NEW;
    }.property('status').cacheable(),

    isDirty: function() {
        return this.get('status') === SC.Record.READY_DIRTY;
    }.property('status').cacheable(),

    nameLabelView: SC.LabelView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.nameLabelViewLayout'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.contentNameProperty')
    }),

    copyButtonView: Footprint.AddButtonView.extend({
        layout: { left: 0, width: 12, centerY: 0, height: 11 },
        action: 'doCloneRecord',
        recordType: Footprint.Scenario,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        isVisibleBinding: SC.Binding.oneWay('.content').bool()
    }),

    deleteButtonView: Footprint.DeleteButtonView.extend({
        layout: { left: 24, width: 10, centerY: 0, height: 11},
        action: 'doPromptDeleteRecord',
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        isVisible: function() {
            return this.getPath('content.isDeletable');
        }.property('content').cacheable()
    })
});
