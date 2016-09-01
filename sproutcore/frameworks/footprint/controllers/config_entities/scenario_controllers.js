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


sc_require('models/scenarios_models');
sc_require('controllers/config_entities/projects_controllers');
sc_require('controllers/active_controller');
sc_require('controllers/tree_controller');
sc_require('controllers/tree_content');
sc_require('controllers/controllers');
sc_require('resources/config_entity_delegator');


/****
 * The flat version of the active scenarios. This controller sends the events scenariosDidChange
 * and scenarioDidChange when the whole set or active scenario is updated
 * @type {RecordControllerChangeSupport}
 */
Footprint.scenariosController = Footprint.ArrayController.create(Footprint.RecordControllerChangeSupport, Footprint.SingleSelectionSupport,{
    project: null,
    projectBinding: SC.Binding.oneWay('Footprint.projectActiveController.content'),
    contentBinding:SC.Binding.oneWay('*project.children'),
    selectionBinding: SC.Binding.oneWay('Footprint.scenarioCategoriesTreeController.selection'),
    selectedItemDidChangeEvent:'scenarioDidChange',
    contentDidChangeEvent:'scenariosDidChange',

    contentLength: null,
    contentLengthBinding: SC.Binding.oneWay('*content.length'),

    /***
     * Try to find a cookie value so we maintain the last used Project when reloading.
     * If we lack a cookie or the cookie's project doesn't exist, return the firstObject
     */
    firstSelectableObject: function() {
        var cookie = this.findCookie(this.get('project'));
        return (cookie && cookie.get('value') && this.findProperty('id', cookie.get('value'))) ||
            sc_super();
    }.property(),

    /***
     * Override because the revision of the content is incremented when nothing really changes.
     * Make absolutely sure the scenarios have change before sending the scenariosDidChange event
     */
    contentDidChange: function() {
        // Only consider a change if the status changes, the parent project changes, or the number of scenarios changes
        if (this.didChangeFor('statusChange', 'status', 'contentLength', 'project') &&
            // TODO this should just be READY_CLEAN, but our status is sometimes dirty
            // We have to check content.status instead of status. When content changes
            // status will still have the previous status.
            [SC.Record.READY_CLEAN, SC.Record.READY_DIRTY].contains(this.getPath('content.status')))

            // Give bindings a change to update before calling
            this.invokeNext(function() {
                Footprint.statechart.sendAction(this.get('contentDidChangeEvent'), this);
            })
    }.observes('.project', '.content', '.contentLength', '.status'),

    /***
     * Store the selected Scenario in a Cookie so that we can make it the selected Scenario when the user reloads
     * @param duration
     */
    setCookie: function(duration, project, scenario) {
        var cookie = this.findCookie(project);
        var scenarioId = scenario.get('id');
        if (cookie) {
            cookie.set('value', scenarioId);
        }
        else {
            cookie = SC.Cookie.create({
                name: 'project.%@.scenario.id'.fmt(project.get('id')),
                value: scenarioId
            });
        }
        if (duration) {
            var d = new Date();
            d.setTime(d.getTime() + duration);
            cookie.expires = d;
        }
        else
            cookie.expires = null;
        cookie.write();
    },

    /***
     * Destroy the cookie for each Project (used when logging out)
     */
    destroyCookies: function() {
        Footprint.projectsController.get('content').forEach(function(project) {
            this.destroyCookie(project);
        }, this);
    },

    /***
     * Destroy the cookied Scenario of the given Project
     * @param project
     */
    destroyCookie: function(project) {
        var cookie = this.findCookie(project);
        if (cookie) {
            cookie.destroy();
        }
    },

    /***
     * Find the cookied scenario of the given project
     * @param project
     * @returns {*}
     */
    findCookie: function(project) {
        return SC.Cookie.find('project.%@.scenario.id'.fmt(project.get('id')));
    }
});

/***
 * Represents the active Scenario. This is reset to the first item of Footprint.scenariosController whenever the latter is reset
 * @type {*}
 */
Footprint.scenarioActiveController = SC.ObjectController.create(Footprint.ConfigEntityDelegator, {

    contentBinding:SC.Binding.oneWay('Footprint.scenariosController*selection.firstObject'),
    parentConfigEntityDelegator: Footprint.projectActiveController,

    // Fetches the category value of the Scenario
    category:function() {
        return this.getPath('content.categories').filter(function(category) {
            return category.key=='category';
        })[0];
    }.property('content').cacheable(),

        /***
     * Cache the current Project so that when we reload we remain there
     */
    contentObserver: function() {
        // Don't cache the id until the Project is ready
        if (this.get('status') & SC.Record.READY) {
            if (this.didChangeFor('scenarioChecker', 'status', 'content'))
                Footprint.scenariosController.setCookie(
                    24*60*60*1000,
                    this.getPath('content.parent_config_entity'),
                    this.get('content'))
        }
    }.observes('.status', '.content')

});

/***
 * Nested store version of the Scenarios for editing. The selection is bound oneWay to the main controller, so that
 * when the main controller selection changes, this one updates its corresponding record
 */
Footprint.scenariosEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:YES,
    sourceController: Footprint.scenariosController,
    isEditable:YES,
    recordType: Footprint.Scenario,
    parentEntityKey: 'parent_config_entity',
    parentRecordBinding:'Footprint.projectActiveController.content',
    store: null,
    orderBy: 'name ASC'
});

/***
 * A subset of the ConfigEntity categories where the category key is 'category'
 * TODO this isn't needed anymore since Footprint.configEntityCategoriesController
 * is already filtered. This controller can probably go away next time we develop
 * a site with scenarios
 * @type {Footprint.ArrayContentSupport}
 */
Footprint.scenarioCategoriesController = Footprint.ArrayController.create(Footprint.ArrayContentSupport, {
    allCategories: null,
    allCategoriesBinding: SC.Binding.oneWay('Footprint.configEntityCategoriesController.content'),
    allCategoriesStatus: null,
    allCategoriesStatusBinding: SC.Binding.oneWay('Footprint.configEntityCategoriesController.status'),
    content: function() {
        return (this.get('allCategoriesStatus') & SC.Record.READY) ?
        Footprint.store.find(SC.Query.local(
            Footprint.Category,
            { conditions: "key = {key}",
              key: 'category' // TODO bad name. Change on server
            }
        )) :
        [];
    }.property('allCategories', 'allCategoriesStatus').cacheable()
});

/***
 *
 * Organizes the Scenarios by one of their Category keys. Currently this hard-coded to 'category' but it should be made a property so that the user can categorize Scenarios otherwise
 * @type {*|void
*/
Footprint.scenarioCategoriesTreeController = Footprint.TreeController.create({

    keyObjects: null,
    keyObjectsBinding: SC.Binding.oneWay('*content.keyObjects'),
    selectionBinding: SC.Binding.from('Footprint.scenariosController.selection'),

    /***
     * Try to find a cookie value so we maintain the last used Project when reloading.
     * If we lack a cookie or the cookie's project doesn't exist, return the firstObject
     * Note that this mimics Footprint.scenarioController. Since they two-way bind the
     * selection this ensures that they both consult the cookie first
     */
    firstSelectableObject: function() {
        var cookie = Footprint.scenariosController.findCookie(Footprint.projectActiveController.get('content'));
        return (cookie && cookie.get('value') && Footprint.scenariosController.findProperty('id', cookie.get('value'))) ||
            sc_super();
    }.property(),

    content: Footprint.TreeContent.create({
        // The unique Category instances assigned to Scenarios that we limited by the special key 'category'
        // We'll only show category values of Scenarios that fall within these categories
        keyObjectsBinding: SC.Binding.oneWay('Footprint.scenarioCategoriesController.content'),
        // The toOne or toMany property of the leaf to access the keyObject(s). Here they are Category instances
        keyProperty:'categories',
        leavesBinding: SC.Binding.oneWay('Footprint.scenariosController.content'),

        // The property of the keyObject that access its name, thus the value of each Category of categories
        keyNameProperty:'value',
        undefinedKeyObject:SC.Object.create({key: 'category', value:'Unknown'}),

        keyObjectsObserver: function() {
            return this.getPath('keyObjects.length')
        }.observes('.keyObjects')
    })
});

/***
 * All Scenarios of the project that are not active
 */
Footprint.nonActiveScenarios = Footprint.ArrayController.create({
    activeScenario: null,
    activeScenarioBinding: SC.Binding.oneWay('F.scenarioActiveController.content'),
    scenarios: null,
    scenariosBinding: SC.Binding.oneWay('F.scenariosController.content'),
    scenariosStatus: null,
    scenariosStatusBinding: SC.Binding.oneWay('*scenarios.status'),
    content: function() {
        return (this.get('scenarios') || []).filter(function(scenario) {
            return this.get('activeScenario') != scenario;
        }, this)
    }.property('activeScenario', 'scenarios', 'scenariosStatus').cacheable()
});
