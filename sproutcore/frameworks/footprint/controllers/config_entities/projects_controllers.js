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


sc_require('models/config_entity_models');
sc_require('controllers/config_entities/regions_controllers');
sc_require('controllers/active_controller');
sc_require('controllers/controllers');
sc_require('resources/config_entity_delegator');

/*
 * projectsController binds to a flat list of the Projects in the current context
 * @type {*}
 */
Footprint.projectsController = Footprint.ArrayController.create(Footprint.RecordControllerChangeSupport, {
    contentBinding:SC.Binding.oneWay('Footprint.regionActiveController.children'),
    selectedItemDidChangeEvent:'projectDidChange',
    contentDidChangeEvent:'projectsDidChange',

    // Extract from the url
    urlProjectKeyBinding: SC.Binding.oneWay('Footprint.developerModeController.project'),

    // Get the project from the url.
    urlProject: function() {
        var urlProjectKey = this.get('urlProjectKey');
        if (!urlProjectKey || !this.get('content')) {
            return null;
        }
        var projects = this.get('content').filter(function(project) {
            return project.get('key') == urlProjectKey;
        });
        if (projects && projects.length) {
            return projects[0];
        }
        return null;
    }.property('urlProjectKey', 'content'),

    // Create a selection object based on the url, if any is specified. If no project
    // is specified in the url, then it is business as usual.
    selection: function(key, value) {
        if (value !== undefined) {
            // if there is a key in the url, then the user isn't
            // allowed to actually switch projects, and this is a no-op.
            if (!this.get('urlProject')) {
                // Someone is setting the selection, we'll use that forced value instead.
                this._forcedSelection = value;
            }
        }

        if (this._forcedSelection) {
            return this._forcedSelection;
        }

        // finally, fall back to using the project from the url.
        var selectionSet = SC.SelectionSet.create();
        selectionSet.addObject(this.get('urlProject'));
        return selectionSet;
    }.property('urlProject', 'content').cacheable(),
});

/***
 * projectSelectionController keeps track of the active Project
 * @type {*}
 */
Footprint.projectActiveController = Footprint.ActiveController.create(Footprint.ConfigEntityDelegator, {
    parentConfigEntityDelegator: Footprint.regionActiveController,
    listController:Footprint.projectsController
});

/***
 * A separate controller from the regionActiveController so that a region can be added or edited without necessarily being the region in context for the rest of the application
 * @type {*}
 */
Footprint.projectEditController = SC.ObjectController.create({
    // Used to create new instances
    recordType: Footprint.Project,
    // The bound object controller, which interacts with its content record directly, rather than via a nested store
    objectControllerBinding:SC.Binding.oneWay('Footprint.projectActiveController')
});
