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
 * Utility functions for integration testing
 */

/***
 * Setup a view for integration testings
 * @param config. An object with configuration atrributes:
 *  attribute contentSetup: a no-argument function that initializes any content data and controllers to bind to the views.
 *  attribute views: a function that returns an array of one or more views to test. These views are simply added to the SC.MainPane that is created in this function and appended to the div of the DOM holding the unit test results. The pane css position is changed from absolute to relative so that the view doesn't cover up to test results. You should thus override the view's position left and top to 0 for testing.
 *  attribute datasource: an optional class to use for the Datasource, such as Footprint.Datasource. Defaults to SC.Record.fixtures
 *  attribute mainPane: optionally supply a mainpane instead of SC.MainPane. This is useful for full application view testing. This would probably be in place of the views options.
 * @return {*} the SC.MainPane pane instance. Access the views with pane.childViews[]
 */
function viewSetup(config) {

    setupForTesting(config);

    SC.RunLoop.begin();

    // Place the views to test in the MainPane
    // Set the global Footprint.testPane to aid in debugging views.
    var pane = Footprint.testPane = (config.mainPane || SC.MainPane).create(config.views ? {
        childViews: config.views()
    } : {});

    // Set the login and user data so calls to the Footprint.DataSource have an apiKey
    setUserContent();

    Footprint.testStatechart = Footprint.Statechart.create({
        trace: YES, // Trace events that aren't handled
        initialState: 'loadingApp'
    });
    Footprint.testStatechart.initStatechart();
    pane.set('defaultResponder', Footprint.testStatechart);

    pane.appendTo($('.core-test')); // this would be '.jasmine_report' for jasmine tests
    $('.core-test').css('height', '1000px');
    pane.$().css('position', 'relative');
    $('.passed').css('display', 'block');

    config.contentSetup();

    try {
        SC.RunLoop.end();
    } catch(e) {
        Footprint.logError(e);
        throw e;
    }

    return pane;
}

function viewTeardown() {

    $('.passed').css('display', 'block');
    // This could be turned on when runnning multiple tests to clear the pane
    //SC.RunLoop.begin();
    //pane.remove();
    //pane = view = null;
    //Footprint.store.reset();
    //SC.RunLoop.end();
}

/**
 * Validates a contentView bound to a TreeController which uses a TreeContent for mixin
 * @param pane: The SC.Pane instance
 * @param data: 'treeController': The controller with the content data of the tree controller.
 *  'treeControllerPath': A label to identify the tree controller.
 *  'contentView': The content view bound to the TreeController.
 *  'contentViewPath': A label for the contentView
 *  'topLevelValidator': An optional function to validate each top level item, the function receives three args: The overall index of the tree item, the item view for the item, and the bound content item.
 *  'bottomLevelValidator': Like topLevelValidator but for the bottom-level (inner) items.
 */
function treeViewValidation(pane, config) {
    if (!config.controllers.get('itemsController'))
        throw "itemsController is undefined"
    return Footprint.Test.create({
        label:'View Test',
        //  start when this controller is READY_CLEAN
        dependsOn: config.controllers.get('itemsController'),
        // The dependsOn controller must be ready within this duration
        onReadyTimeout:10000,
        // The dependent test(s) must all finish within this duration
        dependentTimeout:10000,

        dependents: [
            Footprint.Test.extend({
                label:'treeControllerValidation',
                run: function() {
                    _treeViewValidation(pane, config);
                }
            }),
            Footprint.Test.extend({
                label:'treeControllerValidation',
                run: function() {
                    _treeViewSelectionValidation(pane, config);
                }
            }),
            // Simulate a clone button click to create an edit pane that clones the selected item
            Footprint.Test.extend({
                label:'cloneValidationSetup',
                // The content status delegated by the edit controller should be READY_NEW
                completeStatus: SC.Record.READY_NEW,
                run: function() {
                    var panel = _cloneValidationSetup(pane, config);
                    return panel.get('editController')
                }
            }),
            Footprint.Test.extend({
                label:'cloneValidation',
                run: function() {
                    _cloneValidation(pane, config);
                }
            })
        ],
        onDependentsComplete: function() {
            throw "die so we can interact";
            start();
        }

    });
}

function _treeViewValidation(pane, config) {
    var scGroupItemSelector = '.sc-group-item',
        scListItemSelector = '.sc-list-item-view';

    var treeContent = config.controllers.get('itemsController').get('content');
    var treeControllerPath = config.controllers.get('controllersPath')+ '.itemsController';
    var treeContentPath = treeControllerPath+'.content';

    assertNotNull(config.controllers.get('itemsController'), treeControllerPath);
    assertNotNull(treeContent, treeContentPath);
    assertNotNull(config.contentView, config.contentViewPath);

    // Assert that there are as many top-level view nodes as there are treeItemChildren in the controller
    assertNonZeroLength(treeContent.get('treeItemChildren'), treeContentPath+'.treeItemChildren');
    equals(pane.$(scGroupItemSelector).length,
        treeContent.get('treeItemChildren').length,
        'Expect number matching tree item children count');
    // Make sure the arranged objects length matches our node length + keys length
    // TODO this assumes no items with multiple keys
    equals(config.controllers.get('itemsController').get('arrangedObjects').toArray().length,
        config.controllers.get('itemsController').get('nodes').toArray().length +
        config.controllers.get('itemsController').get('keyObjects').toArray().length,
        'itemsController.arrangedObjects');

    // Assert that top-level node node has the expected number of child nodes. The nodes are actually siblings in the tree view DOM, so use nextUntil to get all up to the next tag node or the end of the siblings.
    var actualTopLevelCounts = pane.$(scGroupItemSelector).map(function(i, selector) {
        return $(selector).nextUntil(scGroupItemSelector).length;
    });
    assertNotNull(treeContent.get('tree'), "Expecting the content object to mix in Footprint.TreeContent and implement its tree property for testing purposes");
    var expectedLowerLevelCounts = $.map(treeContent.get('tree'), function(dict, keyString) {
        // make sure the tree data has no non-zero sub node values
        assertNonZeroLength(dict.values, 'treeContent.tree.%@'.fmt(keyString));
        return dict.values.length;
    });
    assertEqualLength(expectedLowerLevelCounts.length, actualTopLevelCounts.length, treeContent.tree);

    if (expectedLowerLevelCounts.length==actualTopLevelCounts.length) {
        $.dualMap(expectedLowerLevelCounts, actualTopLevelCounts, function(expected, actual, index) {
            equals(expected, actual, 'Expected %@ lower level items, found %@ for index %@'.fmt(expected, actual, index));
        });
    }

    // Flatten the first and second-level items and summon the corresponding view by index
    // Run optional validators on the top-level and bottom-level items
    $.each(
        config.controllers.get('itemsController').get('arrangedObjects').toArray(),
        function(i, contentItem) {
            var itemView = config.contentView.itemViewForContentIndex(i);
            if (itemView.$(scGroupItemSelector).length > 0) {
                if (config.topLevelValidator) {
                    config.topLevelValidator(i, itemView, contentItem)
                }
            }
            else {
                // For SC.ListItemView there is no separate view for the label
                //updateNameAndValidate(pane, itemView, contentItem, i);
                if (config.bottomLevelValidator) {
                    config.bottomLevelValidator(i, itemView, contentItem)
                }
            }
        });
}

/***
 * Select items in the list to make sure our activeObjectController's content updates
 * @param pane
 * @param config
 * @private
 */
function _treeViewSelectionValidation(pane, config) {
    var arrangedObjects = config.controllers.get('itemsController').get('arrangedObjects').toArray()
    var recordType = config.controllers.getPath('editController.recordType');
    var contentItem = arrangedObjects.slice(-1)[0];
    var itemView = config.contentView.itemViewForContentIndex(arrangedObjects.indexOf(contentItem));
    assertNotNull(itemView, "Footprint.panel.contentView.(last item view)");
    // Click the last item and cycle the a run loop
    mouseClick(itemView.$().get(0));
    // Assert that the selection updated
    equals(config.controllers.getPath('itemsController.selection.firstObject'), contentItem, 'itemsController.selection.firstObject');
    // Assert that the objectController content updated
    equals(config.controllers.getPath('editController.objectController.content'), contentItem, 'editController.objectController.content');
}

function _cloneValidationSetup(pane, config) {
    var addButtonView = config.editbarView.addButtonView;
    Footprint.testStatechart.firstCurrentState().add(addButtonView);
    // It seems like a couple run loops need to run to complete all the bindings of the newly created EditPane
    for (i=0; i<2; i++) {
        SC.RunLoop.begin();
        SC.RunLoop.end();
    }
    // Return the debug global panel variable
    return Footprint.panel;
}

function _cloneValidation(pane, config) {
    var panel = Footprint.panel;
    // Assert that all of the properties modeled for read or edit are set
    var viewConfiguration = Footprint.InfoViewConfigurations[panel.get('recordType').toString()];
    viewConfiguration.get('attributes').forEach(function(key) {
        var config = viewConfiguration.get(key);
        // The EditItemView for the property
        var editItemViewName = '%@View'.fmt(key);
        var editItemView = panel.contentView[editItemViewName];
        assertNotNull(editItemView, "Footprint.panel.contentView.%@".fmt(editItemViewName));

        // The expected display title of the view item
        var title = config['title'] || SC.String.titleize(key);
        equals(editItemView.get('title'), title);

        // The configured class of the item view
        var itemViewClass = config['itemViewClass'] || Footprint.EditableModelStringView;
        var itemView = editItemView.get('itemView');
        ok(itemView.kindOf(itemViewClass), "Expected the property %@ itemViewClass %@ to be a kindOf of %@".fmt(
            "Footprint.panel.contentView.%@".fmt(editItemViewName),
            itemView,
            itemViewClass
        ));

        // The properties of the itemView and their expected values relative to the content
        var itemViewProperties = config['properties'] || SC.Object.create({attributes:['value'], value:'editController.%@'.fmt(key)});
        itemViewProperties.get('attributes').forEach(function(propertyName) {
            var propertyPath = itemViewProperties[propertyName];
            // We expect the value in the editItemView to be that of the content
            equals(itemView.getPath(propertyName), panel.getPath(propertyPath), "Footprint.panel.contentView.%@.itemView.%@".fmt(editItemViewName, propertyName));
        });
    }, this);
}

/**
 * Validates a ListView bound to a ListController
 * @param pane: The SC.Pane instance
 * @param data: 'listController': The controller with enumerable content data of the ListController.
 *  'listControllerPath': A label to identify the listController.
 *  'contentView': The ListView bound to the ListController.
 *  'contentViewPath': A label for the contentView
 *  'itemValidator': An optional function to validate each item, the function receives three args: The index of the tem, the item view for the item, and the bound content item.
 */
function listViewValidation(pane, data) {

    var scListItemSelector = '.sc-list-item-view';

    var listContent = data.listController.get('content');
    var listContentPath = data.listControllerPath + '.content'

    assertNotNull(data.listController, data.listControllerPath);
    assertNotNull(listContent, listContentPath);
    assertNotNull(data.contentView, data.contentViewPath);

    // Assert that there are as many nodes as there are content itmes
    assertNonZeroLength(listContent, listContentPath);
    equals(pane.$(scListItemSelector).length,
        listContent.toArray().length,
        'Expect number matching list item children count');

    // Run optional validators on the view items
    $.each(
        listContent.toArray(),
        function(i, contentItem) {
            var itemView = data.contentView.itemViewForContentIndex(i);
            if (data.itemValidator) {
                data.itemValidator(i, itemView, contentItem)
            }
        });
}

/**
 * Validates a SelectView bound to a ListController
 * @param pane: The SC.Pane instance
 * @param data: 'listController': The controller with enumerable content data of the ListController.
 *  'listControllerPath': A label to identify the listController.
 *  'itemActiveController': The controller with the active item of the ListController.
 *  'itemActiveControllerPath': The path of the itemActiveController
 *  'contentView': The SelectView bound to the ListController.
 *  'contentViewPath': A label for the contentView
 */
function selectViewValidation(pane, data) {

    var listContent = data.listController.get('content');
    var listContentPath = data.listControllerPath + '.content'

    assertNotNull(data.listController, data.listControllerPath);
    assertNotNull(listContent, listContentPath);
    assertNotNull(data.contentView, data.contentViewPath);

    // Assert that there are as many nodes as there are content itmes
    assertNonZeroLength(listContent, listContentPath);
    // Since the selectView doesn't actually have a DOM element per item, we just check this obvious equality
    equals(data.contentView.get('items').length(),
        listContent.toArray().length,
        'Expect number matching');

    var itemActiveContent = data.itemActiveController.get('content');
    ok(data.listController.contains(itemActiveContent), "Expect active content to be an item of the list controller");
    var activeIndex = data.listController.indexOf(itemActiveContent);
    // Select the next item by simply changing the selected value. This should update the itemActiveController content via the two-binding
    // TODO I'm not sure how to fire a select event via a mouse click--maybe if the SelectView has an exampleView there will be an actual DOM element to target.
    var nextIndex = (activeIndex+1) % data.listController.length();
    data.contentView.set('value', data.listController.toArray()[nextIndex]);
    // Update the bindings
    SC.RunLoop.begin();
    SC.RunLoop.end();
    var updatedItemActiveContent = data.itemActiveController.get('content');
    ok(updatedItemActiveContent != itemActiveContent, "Expect the %@ to have an updated item".fmt(data.itemActiveControllerPath));
    equals(updatedItemActiveContent, data.listController.toArray()[nextIndex], 'Expect active item to equal the item at index %@ of the list controller'.fmt(nextIndex));
}
