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



/***
 * The default post-login state, whether for an authenticated session or an anonymous demo session
 * @type {Class}
 */
Footprint.ShowingAppState = SC.State.design({

    /***
     * loadingApp has substates for all of the panels of the application
     */
    substatesAreConcurrent: YES,

    enterState: function() {
        Footprint.mainPage.get('mainPane').append();
    },

    /***
     * Listens for socketIO messages
     */
    socketIOState: SC.State.plugin('Footprint.SocketIOState'),

    /***
     * Tracks file uploads
     */
    fileUploadState: SC.State.plugin('Footprint.FileUploadState'),

    firstLoadingTierState: SC.State.extend({
        substatesAreConcurrent: YES,
        /***
         * The top bar of the application showing project info
         */
        showingProjectsState:SC.State.plugin('Footprint.ShowingProjectsState'),
        /***
         * The scenario panel in the top-left
         */
        showingScenariosState:SC.State.plugin('Footprint.ShowingScenariosState'),

        /***
         * The layers panel in the middle-left
         */
        showingLayersState:SC.State.plugin('Footprint.ShowingLayersState'),

        /***
         * Manages LayerLibrary hierarchy loading
         */
        showingLayerLibrariesState:SC.State.plugin('Footprint.ShowingLayerLibrariesState'),

        /***
         * The toolbar panel in the middle-left
         scenario_in*/
        showingToolsState:SC.State.plugin('Footprint.ShowingToolsState'),

        crudState:SC.State.plugin('Footprint.CrudState'),

        /***
         * The map panel in the bottom-center
         */
        showingMapState:SC.State.plugin('Footprint.ShowingMapState'),

        firstTierAwaitingState: SC.State.extend({
            initialSubstate: 'awaitingState',

            /***
             *
             */
            awaitingState: SC.State.extend({
                /*** Let the layers finish loading before loading less important states ***/
                layersAreReady: function() {
                    this.gotoState('secondTierLoadingState');
                }
            }),
            /***
             * The second tier of "showing" States to load
             */
            secondTierLoadingState: SC.State.extend({
                substatesAreConcurrent: YES,

                /***
                 * The DbEntities are only needed by the Data manager. They will
                 * typically already be loaded by associations, but this ensures they are all loaded
                 */
                showingDbEntitiesState:SC.State.plugin('Footprint.ShowingDbEntitiesState'),
                /***
                 * Works alongside ShowingDbEntitiesState to load Feature metadata of selected DbEntities
                 */
                featureMetaDataState:SC.State.plugin('Footprint.FeatureMetadataState'),

                /***
                 * The built forms panel in the bottom-left
                 */
                showingBuiltFormsState:SC.State.plugin('Footprint.ShowingBuiltFormsState'),
                /***
                 * The policies panel in the bottom-right
                 scenario_in*/
                showingAnalysisModulesState:SC.State.plugin('Footprint.ShowingAnalysisModulesState'),

                showingAnalysisToolsState: SC.State.plugin('Footprint.ShowingAnalysisToolsState'),

                /***
                 * The results panel in the top-right
                 */
                showingResultsState:SC.State.plugin('Footprint.ShowingResultsState')
            })
        })
    }),

    exitState: function() {
        Footprint.getPath('mainPage.mainPane').remove();
    }
});
