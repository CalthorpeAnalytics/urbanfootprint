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

sc_require('controllers/active_controller');

Footprint.policySetsController = Footprint.SetsController.create({
    listControllerBinding: SC.Binding.oneWay('Footprint.scenariosController'),
    property:'policy_sets'
});

/***
 * The active policy, as dictated by the user's selection
 * @type {*}
 */
Footprint.policySetActiveController = Footprint.ActiveController.create({
    listController:Footprint.policySetsController
});


Footprint.policySetEditController = SC.ObjectController.create({
    // Used to create new instances
    recordType: Footprint.Policy,
    // The bound object controller, which interacts with its content record directly, rather than via a nested store
    objectControllerBinding:'Footprint.policySetActiveController',

    // Coerce single tag selection into the built_forms's tags collection
    // TODO the view control should support multiple selection
    tag: function(propKey, value) {
        if (value !== undefined) {
            this.get('tags').removeObjects(this.get('tags'));
            this.get('tags').pushObject(value);
        }
        else
            return this.get('tags').objectAt(0);
    }.property('*content.tags')
});

Footprint.policySetControllers = Footprint.ControllerConfiguration.create({
    editController:Footprint.policySetEditController,
    itemsController:Footprint.policySetsController,
    recordSetController:Footprint.policySetsController
});
