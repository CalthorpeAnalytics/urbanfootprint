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
 * Loads controllers specific to sacog
 * @type {*}
 */
FootprintSacog.LoadingRegionSacogLandUseDefinitionState = Footprint.LoadingState.design({
    recordType:Footprint.ClientLandUseDefinition,
    loadingController: Footprint.clientLandUseDefinitionController,
    didLoadEvent:'landUseDefinitionIsReady',
    didFailEvent:'landUseDefinitionDidFail',
    setLoadingControllerDirectly: YES,

    recordArray: function() {
        return Footprint.store.find(SC.Query.create({
            recordType:this.get('recordType'),
            location:SC.Query.REMOTE,
            parameters:{
                config_entity: Footprint.regionActiveController.get('content')
            }
        }));
    }
});

FootprintSacog.LoadingRegionSacogState = SC.State.design({
   initialSubstate:'loadingRegionSacogLandUseDefinitionState',
   loadingRegionSacogLandUseDefinitionState: FootprintSacog.LoadingRegionSacogLandUseDefinitionState
});
