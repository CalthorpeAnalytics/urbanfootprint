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
 * A selection controller whose contents is a list of selectable values. Zero or one items in the list are selected,
 * depending on the property values of the editController.content indicated by the property at propertyKey. If all
 * of editController's content property values are identical, then that single identical item will be the selection
 * of this controller. If the controller's selection is updated to a new value or no value, all the editController's
 * content property values will be updated accordingly. If not all values are identical then there is no selected item.
 *
 */

sc_require('controllers/controllers');

Footprint.clientLandUseDefinitionController = SC.ArrayController.create(Footprint.SingleSelectionSupport, {
    orderBy: ['land_use_description ASC']
});

/***
 * Used for a secondary land use that is represented only as an id on a record, not as a foreign key
 * @type {Footprint.SingleSelectionSupport}
 */
Footprint.clientLandUseDefinitionSecondaryController = SC.ArrayController.create(Footprint.SingleSelectionSupport, {
    orderBy: ['land_use_description ASC'],
    contentBinding: SC.Binding.oneWay('Footprint.clientLandUseDefinitionController.content')
});
