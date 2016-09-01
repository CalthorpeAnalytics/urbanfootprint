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

sc_require('controllers/layers/layer_controllers');

/***
 * This state exists to load a hierarchy of LayerLibraries so that we can add an remove Layers from the Application
 * LayerLibrary at any ConfigEntity scope
 */
Footprint.ShowingLayerLibrariesState = SC.State.extend({
    initialSubstate: 'layerLibraryReadyState',
    layerLibraryReadyState: SC.State,

    /***
     * Called when the active Scenario changes and its LayerLibrary is loaded.
     * This forces loading of parent Application LayerLibraries so we can properly update
     * Layer membership
     * @param context
     */
    layerLibraryDidChange: function(context) {
        this.gotoState(this.loadingLayerLibraryHierarchyState, context)
    },

     /***
     * When the active Scenario LayerLibrary is loaded, we need to load the parent
     * LayerLibraries so that we can change the membership of project, region, and global
     * layers
     */
    loadingLayerLibraryHierarchyState: SC.State.plugin('Footprint.LoadingState', {

        recordType: Footprint.LayerLibrary,
        loadingController: Footprint.scenarioHierarchyLayerLibrariesEditController,
        // Check the status of LayerLibrary since they are not part of a collection
        checkRecordStatuses: YES,

        /***
         * Returns the Application LayerLibray of the scenario and all parent config_entities
         * Once this loads we set the
         * @param context: Contains the Scenario LayerLibrary at content and its status at status
         * @returns {Array}
         */
        recordArray: function(context) {
            var layerLibrary = context.get('content');
            if (context.getPath('status') & SC.Record.READY) {
                var layerLibraries = [];
                layerLibraries.pushObject(layerLibrary);
                // Gather LayerLibraries all the way up the hierarchy
                var configEntity = layerLibrary.get('config_entity');
                while (configEntity) {
                    // Find the corresponding layerLibrary of the parent ConfigEntity
                    configEntity = configEntity.get('parent_config_entity');
                    // Since LayerLibraries might not be loaded, try to load all of them even
                    // though we only want the Application ones, not the Default ones
                    if (configEntity)
                        layerLibraries.pushObjects(configEntity.getPath('presentations.layers'))
                }
                return layerLibraries;
            }
        }
    })
})
