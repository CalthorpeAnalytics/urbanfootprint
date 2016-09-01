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

/**
 * Reverts the changes to the current record.
 */

Footprint.RevertButtonView = SC.ButtonView.design({
    classNames: ['footprint-revet-button', 'theme-button'],
    layout: { height: 24, width: 80 },

    localize: YES,
    title: 'Revert',
    hint: 'Revert the current changes',
    action: 'doPromptCancel', // Same prompt as cancel, but only for the current record
    postConfirmAction: 'doRevert',
    // Indicates whether or not the content of the pane is editable
    isEnabledBinding: SC.Binding.oneWay('.status').equalsStatuses(SC.Record.READY_DIRTY, SC.Record.READY_NEW),
});
