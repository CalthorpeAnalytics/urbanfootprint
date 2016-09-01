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


sc_require('views/info_views/save_button_with_status_view');
/***
 * Abstract class from which to build custom Feature Editor Views
 */

Footprint.FeaturesEditorView = SC.View.extend({
    title: null,
    activeLayer: null,
    content: null,
    saveButtonViewLayout: null,
    saveButtonWithStatusView: Footprint.SaveButtonWithStatusView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.saveButtonViewLayout'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        statusBinding: SC.Binding.oneWay('Footprint.featuresEditController.featuresStatus'),
        monitorProgressOfFirstItem: YES,
        action: 'doFeaturesUpdate',
        buttonTitle: 'Save',
        updatingTitle: 'Saving...',
        additionalContext: {
            maintainApprovalStatus: NO
        },
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
    })
});
