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
// Project:   DataManagerUI
// ==========================================================================
/*globals DataManagerUI */
sc_require('views/data_manager_existing_db_entities_view');
sc_require('views/data_manager_detail_view');

/*
  This container (SC.Page instance) contains all of the pre-configured views that this framework
  provides.

  The reason we use an SC.Page, is so that the views, which are singletons, don't need to be
  initialized as the application code is initially loaded. Initializing a view (by calling create
  on it) takes some cost that we don't want to pay on initial load. SC.Page will handle this for
  us automatically when the property is first accessed via `DataManagerUI.views.get('viewName')`.

  Likewise, SC.Page will replace the original un-instantiated property with the new singleton, which
  slightly reduces the memory load of the system. Having the pre-configured view in a separate file
  would mean that the un-necessary class would still exist in memory after the singleton is created
  from it.
*/
DataManagerUI.views.mixin({

    panel: Footprint.PanelPane.extend({
        layout: { width: 400, height: 550, centerX:0, centerY: 0, border: 1 },
        layerId: 'dmui-panel',
        classNames: ['dmui-panel'],
        // Allow interaction with the main app to look at legends, etc
        isModal: NO,

        // TODO should this be nested content for editing the DbEntities. I think so
        content: null,
        contentBinding: SC.Binding.oneWay('Footprint.dbEntitiesEditTreeController.arrangedObjects'),
        status: null,
        statusBinding: SC.Binding.oneWay('Footprint.dbEntitiesEditTreeController.status'),
        selection: null,
        selectionBinding: SC.Binding.from('Footprint.dbEntitiesEditTreeController.selection'),
        scenario: null,
        scenarioBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.nestedStoreVersion'),
        featureAttributes: null,


        contentView: SC.View.extend({
            // TODO: Show infoView when we have status to put there.
            childViews: ['panelTitle',
                         /* 'infoView', */
                        'overlayView',
                         'mainView',
                         'footerView'],
            childViewLayout: SC.View.VERTICAL_STACK,
            childViewLayoutOptions: {
                resizeToFit: false,
                spacing: 4,
                paddingBefore: 4,
                paddingAfter: 4,
            },
            layout: { left: 0, right: 0, top: 0, bottom: 0 },

            layerId: 'dmui-panel-content-view',
            classNames: ['dmui-panel-content-view'],

            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            status: null,
            statusBinding: SC.Binding.oneWay('.parentView.status'),
            selection: null,
            selectionBinding: SC.Binding.from('.parentView.selection'),
            scenario: null,
            scenarioBinding: SC.Binding.oneWay('.parentView.scenario'),
            featureAttributes: null,
            featureAttributesBinding: SC.Binding.oneWay('.parentView.featureAttributes'),

            panelTitle: SC.LabelView.extend({
                layout: { height: 32, left: 8, right: 110 },
                classNames: ['dmui-panel-title'],
                layerId: 'dmui-title',
                localize: true,
                value: 'DMUI.LayerListTitle',
            }),

            /***
             * Spins when the LayerLibrary is updating.
             * We assume the project or scenario layer libraries are impacted, so we only watch those.
             * In reality, if a Global or Region level layer visibility is changed, we'd have to monoritor
             * those libraries to get this spinner to show
             */
            overlayView: Footprint.LoadingSpinnerView.extend({
                layout: { height: 32, right: 8 },

                scenarioLayerLibrary: null,
                scenarioLayerLibraryBinding: SC.Binding.oneWay('Footprint.scenarioLayerLibraryApplicationEditController.content'),
                scenarioLayerLibraryStatus: null,
                scenarioLayerLibraryStatusBinding: SC.Binding.oneWay('Footprint.scenarioLayerLibraryApplicationEditController.status'),
                statusBinding: SC.Binding.oneWay('Footprint.scenarioHierarchyLayerLibrariesEditController.calculatedStatus'),
            }),


            /***
             * Gives info, warnings, errors, etc. The content of this will have to be dynamic
             */
            infoView: SC.View.extend({
                layout: {height: 50, left: 8, right: 8, border: 1},
                childViews: ['infoIconView', 'infoMessageView'],
                classNames: ['dmui-info-view', 'dmui-box'],
                layerId: 'dmui-info-view',

                // TODO bind these
                recordIsIncomplete: NO,
                recordHasCompleted: NO,

                infoIconView: SC.ImageView.extend({
                    image: 'dmui-help-button',
                    layout: {left: 0, width: 36},
                }),
                infoMessageView: Footprint.LabelView.extend({
                    layout: {left: 40, right: 0},
                    isVisibleBinding: SC.Binding.oneWay('.value'),
                    value: function () {
                        if (this.get('recordIsIncomplete'))
                            return 'DMUI.InfoMustCompleteMessage';
                        else if (this.get('recordHasCompleted'))
                            return 'DMUI.InfoSuccessMessage';
                        return null;
                    }.property('recordIsIncomplete', 'recordHasCompleted').cacheable(),
                    // Only recordIsIncomplete state has a parameter
                    valueParameters: function () {
                        return this.get('recordIsIncomplete') ? [Footprint.layersEditController.get('name')] : [];
                    },
                }),
            }),

            mainView: DataManagerUI.views.ExistingDbEntitiesView.extend({
                layout: {left: 8, right: 8 },
                fillRatio: 1,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                selectionBinding: SC.Binding.from('.parentView.selection'),
                scenarioBinding: SC.Binding.oneWay('.parentView.scenario'),
            }),

            footerView: SC.View.extend({
                childViews: ['closeButton'],
                layout: { left: 8, right: 8, border: 1, height: 26 },

                closeButton: SC.ButtonView.extend({
                    layout: { width: 72, right: 0 },
                    title: 'Close',
                    action: 'doPromptCancel',
                })
            }),

        }),
    }),
});
