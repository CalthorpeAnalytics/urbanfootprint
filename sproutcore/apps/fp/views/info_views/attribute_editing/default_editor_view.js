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


Footprint.DefaultEditorView = SC.View.extend({
    classNames: ['footprint-default-editor-view'],
    childViews: ['labelView'],

    labelView: SC.LabelView.extend({
        value: 'The selected layer is \n' +
            'not configured for editing',
        layout: {top: 50, left: 20, right: 40, height: 50},
        backgroundColor: '#FFFFFF',
        textAlign: SC.ALIGN_CENTER
    })
});

Footprint.MasterScenarioEditorView = SC.View.extend({
    classNames: ['footprint-default-editor-view'],
    childViews: ['labelView'],

    labelView: SC.LabelView.extend({
        value: 'Layers in Master Scenarios \n Cannot be directly edited',
        layout: {top: 50, left: 20, right: 40, height: 50},
        backgroundColor: '#FFFFFF',
        textAlign: SC.ALIGN_CENTER
    })
});
