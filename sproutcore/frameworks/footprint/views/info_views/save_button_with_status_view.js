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

sc_require('views/save_button_view');
sc_require('views/updating_overlay_view');
sc_require('views/progress_overlay_view');
/***
 * Presents a save button with an updating or complete message when those actions are occuring
 * @type {*|RangeObserver|Class|void}
 */
Footprint.SaveButtonWithStatusView = SC.View.extend({
    classNames:['footprint-save-button-with-status'],
    childViews:['saveButtonView', 'updatingStatusView'],
    // The status of the content being saved
    status: null,
    // The content being saved. Needed to detect updates
    content: null,
    // If true monitor the progress of the first item of content in the progressOverlayView
    // This is used when multiple records are being saved simultaneously and they all
    // share the same progress value
    monitorProgressOfFirstItem: NO,
    action: null,
    additionalContext: null,
    buttonTitle: null,
    updatingTitle: null,
    saveButtonLayout: {top: 2, left: 0, height: 22, width: 60},
    updatingStatusLayout: { top: 0, left: 65, width: 75},

    saveButtonView: Footprint.SaveButtonView.extend({
        classNames: ['theme-button-blue'],
        layout: SC.Binding.oneWay('.parentView.saveButtonLayout'),
        isEditable: YES,
        actionBinding: SC.Binding.oneWay('.parentView.action'),
        additionalContext: null,
        additionalContextBinding: SC.Binding.oneWay('.parentView.additionalContext'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.DIRTY)
    }),

    updatingStatusView: Footprint.UpdatingOverlayStatusView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.updatingStatusLayout'),
        statusBinding: SC.Binding.oneWay('.parentView.status'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        updatingTitleBinding: SC.Binding.oneWay('.parentView.updatingTitle')
    })
});
