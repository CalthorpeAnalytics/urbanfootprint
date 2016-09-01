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

// ==========================================================================
// Project:   Footprint.ArcGisLayersModal
// ==========================================================================
/*globals Footprint */

sc_require('views/label_view');
sc_require('views/info_views/label_select_info_view');

/** @class

  (Document Your View Here)

  @extends SC.View
*/
Footprint.ArcGisLayersModal = Footprint.PanelPane.extend(
/** @scope Footprint.ArcGisLayersModal.prototype */ {

    layout: { width: 400, height: 200, centerX: 0, centerY: 0 },
    layerId: 'footprint-arcgis-layers-modal',

    contentView: SC.View.extend({
        childViewLayout: SC.View.VERTICAL_STACK,
        childViews: ['titleView', 'chooseProjectView', 'layersView', 'commandsView'],
        classNames: ['footprint-arcgis-layers-content-view'],
        layerId: 'footprint-arcgis-layers-content-view',

        titleView: Footprint.LabelView.extend({
            layout: { height: 20 },
            classNames: ['footprint-arcgis-layers-title-view'],
            layerId: 'footprint-arcgis-layers-content-title-view',
            value: 'DMUI.ConnectToFile'
        }),

        chooseProjectView: Footprint.LabelView.extend({
            layout: { height: 20 },
            classNames: ['footprint-arcgis-layers-choose-project-view'],
            layerId: 'footprint-arcgis-layers-choose-project-view',
            value: 'DMUI.ChooseAnArcGISProject'
        }),

        layersView: Footprint.LabelSelectInfoView.extend({
            layout: { height: 40 },
            classNames: ['footprint-arcgis-layers-select-info-view'],
            layerId: 'footprint-arcgis-layers-select-info-view',
            title: 'DMUI.Layers',
            content: null,
            itemTitleKey:'name',
            includeNullItem:YES,
            nullTitle:'Select a layer',
            action: 'doSelectArcGISLayer'
        }),

        commandsView: SC.View.extend({
            layout: { height: 24 },
            classNames: ['footprint-arcgis-commands-view'],
            layerId: 'footprint-arcgis-commands-view',
            childViewLayout: SC.View.HORIZONTAL_STACK,
            childViews: ['cancelView', 'connectView'],

            cancelView: SC.ButtonView.extend({
                layout: { width: 150 },
                classNames: ['footprint-arcgis-commands-cancel-view'],
                layerId: 'footprint-arcgis-commands-cancel-view',
                title: 'Cancel',
                action: 'doCloseArcGisLayers'
            }),

            connectView: SC.ButtonView.extend({
                layout: { width: 150 },
                classNames: ['footprint-arcgis-commands-connect-view'],
                layerId: 'footprint-arcgis-commands-connect-view',
                title: 'Connect',
                action: 'doConnectArcGisLayers'
            })
        })
    })
});
