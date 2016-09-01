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
 * Utility functions for controller integration testing
 */

/***
 * Sets up the application for controller testing
 * @param config. An object with configuration atrributes:
 *  attribute stateSetup: a no-argument function that initializes any content data and controllers that rely on that content. It also optionally sets the application to a certain state, to avoid going through, the normal statechart flow (e.g. to avoid the login phase by binding the userController and going to the 'loadingApp' state.
 *  attribute datasource: an optional class to use for the Datasource, such as Footprint.Datasource. Defaults to SC.Record.fixtures
 * @return {*}
 */
function setupApplicationForControllerTesting(config) {

    setupForTesting(config);
    SC.RunLoop.begin();
    Footprint.statechart.initStatechart();
    config.stateSetup && config.stateSetup();
    SC.RunLoop.end();
}


/***
 * Clears data from the store after tests complete
 */
function controllerTeardown() {

    // For some reason the Result tab is being set to hidden for passed tests
    $('.passed').css('display', 'block');
    // Make sure the .core-test div has height!
    $('.core-test').height('1000px');
    //SC.RunLoop.begin();
    //Footprint.store.reset();
    //SC.RunLoop.end();
}

function testListController(params) {
    return Footprint.Test.create({
        dependsOn: params.controllers.get('itemsController'),

        timeout:10000, // dependency must be READY_CLEAN by this time
        onComplete: function() {
            // Restart the main thread if we finish on time
            start();
        },

        dependents: [
            Footprint.Test.extend({
                label:'listControllerValidation',
                run: function() {
                    // this is synchronous so don't return a value to monitor
                    listControllerValidation(params);
                }
            })
        ].concat(listTests(params))
    });
}

function testTreeController(params) {

    return Footprint.Test.create({
        dependsOn: params.controllers.get('itemsController'),

        timeout:10000, // dependency must be READY_CLEAN by this time
        onComplete: function() {
            // Restart the main thread if we finish on time
            start();
        },

        dependents: [
            Footprint.Test.extend({
                label:'treeControllerValidation',
                run: function() {
                    // this is synchronous so don't return a value to monitor
                    treeControllerValidation(params);
                }
            }),
        ].concat(listTests(params))

    });
}

function listTests(params) {
    return [
        Footprint.Test.extend({
            label:'cloneRecordTest',
            run: function() {
                // Returns the clonedObject, we monitor it's _status property before continuing to validation
                return cloneRecordTest(params);
            },
            // Await this alternative status property that indicates the clone is complete
            // We could alternatively await 'state' Footprint.EDIT_READY_CREATE
            completeStatusProperty:'_status',
            completeStatus:Footprint.Status.READY_NEW_CLONED
        }),
        Footprint.Test.extend({
            label:'cloneRecordValidation',
            run: function() {
                cloneRecordValidation(params);
            }
        }),
        Footprint.Test.extend({
            label:'saveClonedRecordTest',
            run: function() {
                return saveClonedRecordTest(params);
            }
        }),
        Footprint.Test.extend({
            label:'saveClonedRecordValidation',
            run: function() {
                saveClonedRecordValidation(params);
            }
        }),
        // Simply calls update_current on the EditController, we perform the update in the next test
        // to make sure the object to be edited is loaded, which is asynchronous.
        Footprint.Test.extend({
            label:'startUpdatePropertyTest',
            run: function() {
                return startUpdatePropertyTest(params);
            },
            // When the controller is in update mode we're ready
            completeStatusProperty:'state',
            completeStatus:Footprint.EDIT_READY_UPDATE
        }),
        Footprint.Test.extend({
            label:'updatePropertyTest',
            run: function() {
                var property = 'name';
                return updatePropertyTest(params, property, String);
            }
        }),
        Footprint.Test.extend({
            label:'updatePropertyValidation',
            run: function() {
                var property = 'name';
                updatePropertyValidation(params, property, String);
            }
        })
    ]

}

function listControllerValidation(config) {

    var controllers = config.controllers;
    var listController = controllers.get('itemsController');
    var editController = controllers.get('editController');
    var listControllerPath = '%@.itemsController'.fmt(config.controllersPath);
    var recordType = config.recordType;

    // Verify that instances at the first level of the tree are TreeItem instances
    var items = listController.get('content');
    assertNonZeroLength(items, '%@.content'.fmt(listControllerPath));
    assertKindForList(recordType, items[0],
        '%@.content[0]'.fmt(listControllerPath));
}

// Clone testing

function treeControllerValidation(config) {

    var controllers = config.controllers;
    var treeController = controllers.get('itemsController');
    var editController = controllers.get('editController');
    var treeControllerPath = '%@.itemsController'.fmt(config.controllersPath);
    var recordType = config.recordType;

    // Verify that instances at the first level of the tree are TreeItem instances
    var treeItems = treeController.get('treeItemChildren');
    assertNonZeroLength(treeItems, '%@.arrangedObjects'.fmt(treeControllerPath));
    assertKindForList(Footprint.TreeItem, treeItems, '%@.arrangedObjects'.fmt(treeControllerPath));
    // Verify that instances at the second level of the tree
    assertNonZeroLength(treeItems[0].get('treeItemChildren'),
        '%@.treeItemChildren[0].treeItemChildren'.fmt(treeControllerPath));
    assertKindForList(recordType, treeItems[0].get('treeItemChildren'),
        '%@.treeItemChildren[0].treeItemChildren'.fmt(treeControllerPath));
}

// Clone testing
function cloneRecordTest(config) {
    // Create a new record by cloning the editController.objectController.content
    var editController = config.controllers.get('editController');
    // We shouldn't haven any content to edit yet.
    assertNull(!editController.get('content'));
    // Return this so we can monitor its _status property to become Footprint.Status.READY_NEW_CLONED
    // createNew returns the controller content.
    return editController.createNew()
}
// Call when the return of clone is READY_NEW
function cloneRecordValidation(config) {
    var editController = config.controllers.get('editController');
    var controllerPath = config.controllersPath;
    var editControllerPath = '%@.editController.content'.fmt(controllerPath);
    assertNotNull(editController.get('content'), editControllerPath);
    assertStatus(editController.get('content'), SC.Record.READY_NEW, editControllerPath);
}

function saveClonedRecordTest(config) {
    // Create a new record by cloning the editController.objectController.content
    var editController = config.controllers.get('editController');
    editController.save();
    // Return the controller which delegates its content to the status, so the validation can wait for it to be READY_CLEAN
    return editController;
}

function saveClonedRecordValidation(config) {
    var editController = config.controllers.get('editController');
    var controllerPath = config.controllersPath;
    var editControllerPath = '%@.editController.content'.fmt(controllerPath);
    assertStatus(editController, SC.Record.READY_CLEAN, editControllerPath);
    // Make sure the record has saved to the server an has an id now
    var savedContent = editController.get('content');
    assertNotNull(savedContent.get('id'), '%@.editController.content.id'.fmt(config.controllersPath));
    // Make sure the objectController was updated to the same record
    var content = editController.getPath('objectController.content');
    var editControllerContentPath = '%@.editController.content'.fmt(controllerPath);
    ok(savedContent===content, "%@ was saved but it is not reflected in the objectController.content property".fmt(editControllerContentPath))
}

function startUpdatePropertyTest(config) {
    var editController = config.controllers.get('editController');
    // Reset the controller to begin the editing session
    editController.updateCurrent();
    return editController;
}

function updatePropertyTest(config, property, valueType) {
    var editController = config.controllers.get('editController');
    var content = editController.get('content');
    content.addObserver('status', Footprint.tester, 'obs');
    assertNotNull(content, 'editController.content');

    var oldValue = content.get(property);
    var newValue = _newPropertyValue(content, property, valueType);
    content.set(property, newValue);
    // Make sure the property is not updated in the main store
    var loadedContent = Footprint.store.find(editController.get('recordType'), content.get('id'));
    equals(loadedContent.get(property), oldValue, "Expected content loaded from the main store to still have the original value");
    // Save the change
    editController.save();
    // Return the content so it can be monitored for a READY_CLEAN status
    return content;
}

function updatePropertyValidation(config, property, valueType) {
    var editController = config.controllers.get('editController');
    var content = editController.get('content');
    // Make sure the property is now updated in the main store
    var reloadedContent = Footprint.store.find(editController.get('recordType'), content.get('id'));
    var newValue = _newPropertyValue(content, property, valueType);
    equals(reloadedContent.get(property), newValue, "Expected content reloaded from the main store to have the new value");
}

function _newPropertyValue(content, property, valueType) {
    if (valueType==String)
        return "%@_update".fmt(content.get(property));
    else
        throw "No value generator for valueType %@".fmt(valueType);
}
