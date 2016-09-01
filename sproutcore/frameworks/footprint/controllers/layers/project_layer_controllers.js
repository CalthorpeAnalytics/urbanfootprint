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
 * The LayerLibraries of the active Project. This is only used by the DataManager
 */
Footprint.projectLayerLibrariesController = Footprint.PresentationsController.create({
    contentBinding:SC.Binding.oneWay('Footprint.projectActiveController*presentations.layers')
});

/***
 * The project APPLICATION LayerLibrary is referenced here so that we can see if a Layer is
 * member of it as opposed to just the current Scenario. This is used by the DataManager to
 * determine the layer's current application active status
 */
Footprint.projectLayerLibraryApplicationController = Footprint.PresentationController.create({
    presentationsBinding: SC.Binding.oneWay('Footprint.projectLayerLibrariesController.content'),
    // The APPLICATION LayerLibrary contains the Layers that are to be shown in the Layer view
    key: 'layer_library__application',
    keysBinding: SC.Binding.oneWay('.layers').transform(function (value) {
        if (value && value.get('status') & SC.Record.READY)
            return value.mapProperty('db_entity').mapProperty('key');
    })
});

/***
 * A nested version of the LayerLibrary, which we used to access the layers for editing.
 * The nested store to that of the Footprint.dbEntitiesEditController, since the latter
 * is the main controller of DbEntity/Layer editing and has its nestedStore set by the CrudState
 */
Footprint.projectLayerLibraryApplicationEditController = Footprint.EditObjectController.create({
    sourceController: Footprint.projectLayerLibraryApplicationController,
    recordType: Footprint.LayerLibrary,
    storeBinding: SC.Binding.oneWay('Footprint.dbEntitiesEditController.store')
});
