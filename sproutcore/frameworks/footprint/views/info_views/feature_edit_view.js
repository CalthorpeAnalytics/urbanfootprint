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


sc_require('views/info_views/info_view');
sc_require('views/save_button_view');


Footprint.FeatureEditView = Footprint.InfoView.extend({
    classNames: "footprint-feature-edit-view".w(),
    childViews:'commitButtonsView'.w(),
    title: 'Editable Fields',
    content: null,
    recordType: null,
    selection: null,

    commitButtonsView: Footprint.SaveButtonView.extend({
        classNames: ['theme-button-green'],
        layout: {bottom: 45, left: 10, height:40, width:90},
        isEditable: YES,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        // Indicates whether or not the content of the pane is editable and has changed--thus can be saved or cancelled
        isChanged: function() {
            return this.get('status') & SC.Record.READY_DIRTY
        }.property('status'),
        isEnabledBinding: SC.Binding.oneWay('.isChanged')
    })
});
