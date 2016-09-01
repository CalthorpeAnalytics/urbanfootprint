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

sc_require('controllers/features/feature_controllers');
sc_require('models/intersection_model');
sc_require('controllers/db_entities/primary_geography_db_entity_mixin');
sc_require('controllers/associated_items_controller');
sc_require('sc_extensions/resources/array_status');

/***
 * The name of this file is thus db_entity_controllers
 */

Footprint.dbEntitiesController = Footprint.ArrayController.create({
    dbEntities: null,
    dbEntitiesBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.db_entities'),
    dbEntitiesStatus: null,
    dbEntitiesStatusBinding: SC.Binding.oneWay('*dbEntities.status'),
    /***
     * Filters out DbEntities that we don't need in this context, such as Result DbEntities
     */
    content: function() {
        if (!this.getPath('dbEntities') ||  !((this.get('status') & SC.Record.READY)))
            return null;
        // Just filter out result DbEntities
        return this.get('dbEntities').filter(function(dbEntity) {
            return !dbEntity.get('source_db_entity_key');
        });
    }.property('dbEntities', 'dbEntitiesStatus'),
    status: null,
    statusBinding: SC.Binding.oneWay('*dbEntities.status'),

    /***
     * Bind the active DbEntity to the active Layer, since the user changing the layer must change this selection
     */
    selectionBinding: SC.Binding.oneWay('Footprint.layerTreeController.selection').transform(function(selection) {
        var selectionSet = SC.SelectionSet.create();
        selectionSet.addObjects(selection.mapProperty('db_entity'));
        return selectionSet;
    })
});

/***
 * Nested store version of the Layers for editing. The selection is bound oneWay to the main controller, so that
 * when the main controller selection changes, this one updates its corresponding record
 * The nestedStore property is set by CrudState
 */
Footprint.dbEntitiesEditController = Footprint.EditArrayController.create(SC.RecordsStatus, Footprint.RecordControllerChangeSupport, {
    allowsEmptySelection:YES,
    recordType: 'Footprint.DbEntity',
    sourceController: Footprint.dbEntitiesController,

    // Bind this to the tree controller, they must always have the same selection
    selectionBinding: SC.Binding.from('Footprint.dbEntitiesEditTreeController.selection'),
    selectedItemDidChangeEvent:'dbEntityEditDidChange',
    contentDidChangeEvent:'dbEntitiesDidChange',
    isEditable:YES,
    orderBy: ['name ASC', 'id ASC'] // id just here to fix an SC bug
});

/***
 * The controller used for editing a DbEntity in the Data Manager
 */
Footprint.dbEntityEditController = Footprint.EditSelectedItemController.create({
    sourceControllerBinding: SC.Binding.oneWay('Footprint.dbEntitiesEditController')
});


/***
 * @type {*}
 */
Footprint.dbEntityActiveController = Footprint.ActiveController.create({
    listController: Footprint.dbEntitiesController
});

Footprint.dbEntitiesEditTreeController = Footprint.TreeController.create({

    keyObjects: null,
    keyObjectsBinding: SC.Binding.oneWay('*content.keyObjects'),

    scenario: null,
    scenarioBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),

    content: Footprint.TreeContent.create({
        recordType: Footprint.DbEntity,
        /**
         * The nodes of the tree, currently all tags in the system
         * TODO these tags should be limited to those used by DbEntities
         */
        keyObjectsBinding: SC.Binding.oneWay('Footprint.dbEntityAllCategoriesEditController.content'),
        // The toOne or toMany property of the leaf to access the keyObject(s). Here they are Footprint.Category instances
        keyProperty:'categories',

        defaultLayerLibraryBinding: SC.Binding.oneWay('Footprint.layerLibraryDefaultEditController*content.layers'),

        dbEntitiesBinding: SC.Binding.oneWay('Footprint.dbEntitiesEditController.content'),

        // Track changes to membership
        dbEntitiesObserver: function() {
            this.invokeOnce(this._dbEntitiesObserver);
        }.observes('*dbEntities.[]', '*dbEntities.@each.status'),

        _dbEntitiesObserver: function() {
            this.propertyDidChange('leaves')
        },

        // The leaves of the tree: We are only showing dbEntities that have a corresponding layer in the LayerLibrary.
        leaves: function() {
            var entities = this.get('dbEntities');
            var layers = this.getPath('defaultLayerLibrary');
            if (!layers) {
                return [];
            }

            var layer_db_entity_ids = layers.map(function(layer) {
                return layer.getPath('db_entity.id');
            });
            return entities;

            // Now only include db_entities that have layers.
            return entities.filter(function(dbEntity) {
                return layer_db_entity_ids.indexOf(dbEntity.get('id')) != -1;
            });
        }.property('dbEntitiesBinding', 'defaultLayerLibrary').cacheable(),

        // Bind to the control since we filter the leaves to an array
        leavesStatusBinding: SC.Binding.oneWay('Footprint.dbEntitiesEditController.status'),

        // The property of te keyObject to use for a name. Here it is the 'tag' property of Tag
        keyNameProperty:'value',
        // Our default category for layers whose db_entity doesn't have any tags that match are tag se
        // If our leaf is a provisional DbEntity put it in a specially ke
        undefinedKeyObject:function() {
            return function(leaf) {
                return leaf.get('status') === SC.Record.READY_NEW ?
                    SC.Object.create({key: 'DbEntityClassification', value: 'New', is_new: YES}) :
                    SC.Object.create({key: 'DbEntityClassification', value: 'Unknown'});
            };
        }.property().cacheable(),

        // Sort leaves by name
        sortProperties: ['name'],
        // Sort keys by value and prioritize the new undefined KeyObject
        sortKeyProperties:['is_new', 'value'],
        keyReverseSortDict: {is_new: YES},
        keyObjectsObserver: function() {
            return this.getPath('keyObjects.length');
        }.observes('.keyObjects'),
    }),

    allowsEmptySelection: NO,

    leavesStatus: null,
    leavesStatusBinding: SC.Binding.oneWay('*leaves.status'),
    contentDidChange: function() {
        // Clear the selection when the leaves change. firstSelectableObject will set it to something after.
        if (this.didChangeFor('keyObjects', 'leaves', 'leavesStatus')) {
            this.deselectObjects(this.getPath('selection'));
        }
    }.observes('.keyObjects', '.leaves', '.leavesStatus')
});


/***
 * Offers a list of ConfigEntity scopes for a DbEntity to belong to. It is bound two-way to the DbEntity currently being edited
 * @type {Footprint.SingleSelectionSupport}
 */
Footprint.dbEntityScopesController = SC.ArrayController.create(Footprint.SingleSelectionSupport, {
    allowsEmptySelection: NO,
    scenario: null,
    scenarioBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),
    dbEntity: null,
    dbEntityBinding: 'Footprint.layerEditController*db_entity',
    dbEntityStatus: null,
    dbEntityStatusBinding: SC.Binding.oneWay('*dbEntity.status'),
    // New Layers can create a DbEntity scoped to the Scenario or Project
    // This property serves as a liaison between scope and singleSelection to convert between
    // ConfigEntity and subclassed ConfigEntity, respectively
    // For non-new layers this is readonly--we use the schema to show the scope
    // TODO this is out of date and needs to go be updated
    scopeConfigEntity: function(propKey, value) {
        if (this.getPath('dbEntity.status') === SC.Record.READY_NEW) {
            if (typeof(value) !== 'undefined' && (this.getPath('dbEntity.status') & SC.Record.READY)) {
                // No conversion needed here. scope can accept a subclass instance
                this.setPath('dbEntity.config_entity', value);
            }
            // Return the content matching the scope's id
            return this.get('content').find(function(configEntity) {
                return configEntity.get('id')==this.getPath('dbEntity.config_entity.id');
            }, this);
        }
        else {
            // Find the ConfigEntity matching the schema
            if (this.getPath('dbEntity.status') & SC.Record.READY) {
                return this.get('content').filterProperty('schema', this.getPath('dbEntity.schema'))[0];
            }
        }
    }.property('dbEntity', 'dbEntityStatus').cacheable(),

    singleSelectionBinding: '.scopeConfigEntity',
    // Sets up scopeConfigEntity when the DbEntity becomes ready
    dbEntityObserver: function() {
        if ((this.getPath('dbEntity.status') & SC.Record.READY) &&
            !this.getPath('dbEntity.config_entity')) {
            this.set('scopeConfigEntity', this.get('singleSelection'));
        }
    }.observes('.dbEntity', '*dbEntity.status'), // don't use dbEntityStatusProperty--it lags

    project: null,
    projectBinding: SC.Binding.oneWay('*scenario.project'),
    content: function() {
        return [this.get('scenario'), this.get('project')].compact();
    }.property('scenario', 'project').cacheable()
});


/***
 * The Primary Geography DbEntities of the current Scenario. There must be one or more, typically a DbEntity
 * at the Project scope and one or more at a Region scope
 */
Footprint.primaryDbEntitiesEditController = SC.ArrayController.create(Footprint.PrimaryGeographyDbEntitiesMixin, {
    activeDbEntityBinding: SC.Binding.oneWay('Footprint.dbEntityEditController.content'),
    contentBinding: SC.Binding.oneWay('*dbEntities')
});

/***
 * All of the DbEntity Tags in the system. Set the view to filteredContent to filter by the
 * @type {Footprint.ArrayContentSupport}
 */
Footprint.dbEntityAllTagsController = Footprint.ArrayController.create(Footprint.ArrayContentSupport, {
});
/***
 * Nested version of AllTags controller so we have the same store as the DbEntity being edited.
 * These aren't actually edited
 */
Footprint.dbEntityAllTagsEditController = Footprint.EditArrayController.create({
    sourceController: Footprint.dbEntityAllTagsController,
    storeBinding: SC.Binding.oneWay('Footprint.dbEntitiesEditController.store'),
    recordType: Footprint.DbEntityTag
});

/***
 * The DbEntity Tags of the current DbEntity
 * @type {Footprint.ArrayContentSupport}
 */
Footprint.dbEntityTagsEditController = Footprint.ArrayController.create({
    contentBinding: SC.Binding.oneWay('Footprint.dbEntityEditController*content.tags')
});
/***
 * All available DbEntity tags minus those filtered out by the searchString and those that are already
 * in Footprint.dbEntityTagsEditController
 * @type {Footprint.ArrayContentSupport}
 */
Footprint.dbEntityFilteredEditTagsController = Footprint.AssociatedItemsController.create({
    searchProperties: ['tag'],
    associatedItemsBinding: SC.Binding.oneWay('Footprint.dbEntityTagsEditController.content'),
    allItemsBinding: SC.Binding.oneWay('Footprint.dbEntityAllTagsEditController.content')
});

/***
 * All of the DbEntity Categories in the system. Set the view to filteredContent to filter by the
 * @type {Footprint.ArrayContentSupport}
 */
Footprint.dbEntityAllCategoriesController = Footprint.ArrayController.create(Footprint.ArrayContentSupport, {
    orderBy: 'value DESC'
});

/***
 * Nested version of AllCategories controller so we have the same store as the DbEntity being edited.
 * These aren't actually edited
 */
Footprint.dbEntityAllCategoriesEditController = Footprint.EditArrayController.create({
    sourceController: Footprint.dbEntityAllCategoriesController,
    storeBinding: SC.Binding.oneWay('Footprint.dbEntitiesEditController.store'),
    /***
     * Limit the results for now to the Categories with key DbEntityClassification
     */
    conditions: 'key=\'DbEntityClassification\' AND deleted!=YES',
    recordType: Footprint.DbEntityCategory
});

/***
 * The DbEntity Categories of the current DbEntity
 * @type {Footprint.ArrayContentSupport}
 */
Footprint.dbEntityCategoriesEditController = Footprint.ArrayController.create({
    contentBinding: SC.Binding.oneWay('Footprint.dbEntityEditController*content.categories'),
    store: null,
    storeBinding: SC.Binding.oneWay('*content.store')
});

/***
 * All available DbEntity categories minus those filtered out by the searchString and those that are already
 * in Footprint.dbEntityCategoriesEditController
 * @type {Footprint.ArrayContentSupport}
 */
Footprint.dbEntityFilteredEditCategoriesController = Footprint.AssociatedItemsController.create({
    searchProperties: ['value'],
    associatedItemsBinding: SC.Binding.oneWay('Footprint.dbEntityCategoriesEditController.content'),
    allItemsBinding: SC.Binding.oneWay('Footprint.dbEntityAllCategoriesEditController.content'),
    selectionIsAssociatedItems: YES,
    store: null,
    storeBinding: SC.Binding.oneWay('*content.store')

});

/***
 * The Feature field schema of the DbEntity being viewed or edited in the Data Manager
 */
Footprint.dbEntityFeatureSchemaEditController = Footprint.FeatureFieldsController.create({
    dbEntityBinding: SC.Binding.oneWay('Footprint.dbEntityEditController.content'),
    templateFeatureBinding: SC.Binding.oneWay('Footprint.templateFeatureActiveController.content'),
    statusBinding: SC.Binding.oneWay('Footprint.templateFeatureActiveController.status'),
    contentAsSchema: YES,
    store: null,
    storeBinding: SC.Binding.oneWay('*content.store')
});

/***
 * FeatureBehaviors for the current DbEntities must be loaded before we know if Layers are background imagery.
 * In the future behaviors will be used to identity much more functionality
 */
Footprint.featureBehaviorsController = Footprint.ArrayController.create(SC.ArrayStatus, {
});

/***
 * The DbEntities of the currently joined DbEntities in the Footprint.layerSelectionEditController
 * @type {SC.ArrayStatus}
 */
Footprint.joinedDbEntitiesController = Footprint.ArrayController.create(SC.ArrayStatus, {
    joins: null,
    joinsBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController.joins'),

    // This is just used to prevent out-of-sync problems when the scenario changes
    layerSelectionScenario: null,
    layerSelectionScenarioBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController*layer.db_entity.config_entity'),

    scenario: null,
    scenarioBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),

    /***
     * The content is the DbEntity represented by each of the joins, which are DbEntity keys
     * scoped to the active ConfigEntity
     */
    content: function() {
        var scenario = this.get('scenario');
        if (!this.get('scenario') || !this.get('joins'))
            return null;
        var dbEntities = scenario.get('db_entities');

        return this.get('joins').map(function(key) {
            return dbEntities.filterProperty('key', key).get('firstObject');
        }, this).compact();
    }.property('scenario', 'joins', 'layerSelectionScenario').cacheable(),

    contentObserver: function() {
        if (this.get('content') && this.didChangeFor('contentCheck', 'content')) {
            Footprint.statechart.sendEvent('joinDbEntitiesDidChange');
        }
    }.observes('content')
});
/***
 * We currently just expect on joined DbEntity, so this holds it
 */
Footprint.joinedDbEntityActiveController = SC.ObjectController.create({
    contentBinding: SC.Binding.oneWay('Footprint.joinedDbEntitiesController.firstObject'),
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.joinedDbEntitiesController.status')
});

/***
 * Keeps track of the active DbEntity of the query string of the filter or aggregate,
 * which is always the last clause of the query string
 * @type {SC.ArrayStatus}
 */
Footprint.activeQueryDbEntitiesController = Footprint.ArrayController.create(SC.ArrayStatus, {

});
Footprint.activeQueryDbEntityActiveController = SC.ObjectController.create({
    contentBinding: SC.Binding.oneWay('Footprint.activeQueryDbEntitiesController.firstObject'),
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.activeQueryDbEntitiesController.status')
});
