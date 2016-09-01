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


Footprint.featureRevisionsController = Footprint.ArrayController.create(Footprint.FeaturesControllerMixin, {
    layerBinding:SC.Binding.oneWay('Footprint.layerSelectionActiveController.layer')
});
Footprint.featureRevisionsEditController = Footprint.ArrayController.create(Footprint.FeaturesControllerMixin, Footprint.EditControllerSupport, {
    allowsEmptySelection:YES,
    sourceController: Footprint.featureRevisionsController,
    layerBinding:SC.Binding.oneWay('Footprint.layerSelectionEditController.layer')
});
