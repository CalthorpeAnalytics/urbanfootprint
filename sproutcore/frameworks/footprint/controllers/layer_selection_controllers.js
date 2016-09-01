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

__author__ = 'calthorpe_analytics'

/***
 * Manages the Footprint.LayerSelections. Right now this just has
 * the single LayerSelection for the current user and layer.
 * @type {SC.SelectionSupport}
 */
Footprint.layerSelectionsController = SC.ArrayController.create(SC.SelectionSupport, Footprint.ArrayContentSupport, {
    // Update the layer property whenever the user layer or user statuses change
    activeLayer:null,
    activeLayerBinding:SC.Binding.oneWay('Footprint.layerActiveController.content'),
    user:null,
    // TODO firstObject simple binding doesn't work
    userBinding:SC.Binding.oneWay('Footprint.userController.firstObject'),
    contentObserver:function() {
        if (this.get('content') && this.get('status') & SC.Record.READY) {
            this.forEach(function(layerSelection) {
                if (layerSelection.get('user') === this.get('user')) {
                    this.selectObject(layerSelection);
                }
            }, this)
        }
    }.observes('.content', '.status').cacheable()
});

/***
* Binds to the LayerSelection instance of the active Layer
* @type {*|void}
*/
Footprint.layerSelectionActiveController = SC.ObjectController.create({
    contentBinding: SC.Binding.oneWay('Footprint.layerSelectionsController.firstObject'),
    layerId: null,
    layerIdBinding: SC.Binding.oneWay('*content.layer.id')
});

Footprint.layerSelectionEditController = SC.ObjectController.create({
    layerId: null,
    layerIdBinding: SC.Binding.oneWay('*content.layer.id')
});
