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


Footprint.CancelButtonView = SC.ButtonView.design({
    classNames: ['footprint-cancel-button', 'theme-button'],
    layout: { height: 24, width: 80 },

    localize: YES,
    title: 'Cancel',
    action: 'doPromptCancel',
    postConfirmAction: 'doCancel'
});
