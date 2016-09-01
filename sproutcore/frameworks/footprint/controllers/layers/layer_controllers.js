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


sc_require('controllers/attributes_controller');
sc_require('models/presentation_models');
sc_require('models/layer_models');
sc_require('controllers/config_entities/scenario_controllers');
sc_require('controllers/presentation_controllers');
sc_require('controllers/controllers');
sc_require('controllers/tree_observer');

/***
 * The LayerLibraries of the active Scenario
 */
Footprint.layerLibrariesController = Footprint.PresentationsController.create({
    contentBinding:SC.Binding.oneWay('Footprint.scenarioActiveController*presentations.layers')
});

/**
 * The APPLICATION LayerLibrary of the active Scenario. These are the layers that
 * appear on the main view that the user(s) have chosen to be active
 */
Footprint.scenarioLayerLibraryApplicationController = Footprint.PresentationController.create({
    presentationsBinding:SC.Binding.oneWay('Footprint.layerLibrariesController.content'),
    // The APPLICATION LayerLibrary contains the Layers that are to be shown in the Layer view
    key: 'layer_library__application',
    // TODO what is this for?
    keysBinding:SC.Binding.oneWay('.layers').transform(function(value) {
        if (value && value.get('status') & SC.Record.READY)
            return value.mapProperty('db_entity').mapProperty('key');
    }),

});

/***
 * A nested version of the LayerLibrary, which we used to access the layers for editing.
 * The nested store is set by the ShowingLayersState
 * The nested store to that of the Footprint.dbEntitiesEditController, since the latter
 * is the main controller of DbEntity/Layer editing and has its nestedStore set by the CrudState
 */
Footprint.scenarioLayerLibraryApplicationEditController = Footprint.EditObjectController.create({
    sourceController: Footprint.scenarioLayerLibraryApplicationController,
    recordType: Footprint.LayerLibrary,
    storeBinding: SC.Binding.oneWay('Footprint.dbEntitiesEditController.store'),

    // When the Scenario changes, we make sure all LayerLibraries in the hierarchy are loaded.
    // This sets Footprint.scenarioHierarchyLayerLibrariesEditController so we can bind to its status
    // This has to be the EditController so we can track BUSY records when updating
    contentDidChange: function() {
        // If the LayerLibrary or status didn't change, do nothing
        if (!this.didChangeFor('layerLibraryDidChangeTracker', 'content', 'status'))
            return;

        // Wait until the Scenario LayerLibrary is loaded and then load its ancestors
        if (this.get('status') & SC.Record.READY) {
            Footprint.statechart.sendAction(
                'layerLibraryDidChange',
                SC.Object.create({
                    content: this.get('content'),
                    status: this.get('status')
                })
            );
        }
    }.observes('.content', '.status')
});

/**
 * The DEFAULT LayerLibrary of the active Scenario. These are all layers available at the
 * current Scenario scope that can be manipulated in the data manager, where a user can
 * activate Layers to copy them into the APPLICATION LayerLibrary for the Project or Scenario
 */
Footprint.layerLibraryDefaultController = Footprint.PresentationController.create({
    presentationsBinding:SC.Binding.oneWay('Footprint.layerLibrariesController.content'),
    // The DEFAULT LayerLibrary contains the Layers that are to be shown in the Layer view
    key: 'layer_library__default',
    // TODO what is this for?
    keysBinding:SC.Binding.oneWay('.layers').transform(function(value) {
        if (value && value.get('status') & SC.Record.READY)
            return value.mapProperty('db_entity').mapProperty('key');
    }),
});

/***
 * A nested version of the LayerLibrary, which we used to access the layers for editing.
 * The nested store is set by the ShowingLayersState
 * The nested store to that of the Footprint.dbEntitiesEditController, since the latter
 * is the main controller of DbEntity/Layer editing and has its nestedStore set by the CrudState
 */
Footprint.layerLibraryDefaultEditController = Footprint.EditObjectController.create({
    sourceController: Footprint.layerLibraryDefaultController,
    recordType: Footprint.LayerLibrary,
    storeBinding: SC.Binding.oneWay('Footprint.dbEntitiesEditController.store'),
});

/****
 * The flat version of the active layers. This controller sends the events layersDidChange
 * and layerDidChange when the whole set or active layer is updated
 * @type {RecordControllerChangeSupport}
 */
Footprint.layersController = Footprint.ArrayController.create(Footprint.RecordControllerChangeSupport, {
    contentBinding: SC.Binding.oneWay('Footprint.scenarioLayerLibraryApplicationController.layers'),
    selectionBinding: SC.Binding.oneWay('Footprint.layerTreeController.selection'),
    previousSelection: null,
    selectedItemDidChangeEvent:'layerDidChange',
    contentDidChangeEvent:'layersDidChange',
    //when the content gets updated, ensure that that selection doesn't update to the first object but utilizes the
    //cached selection from prior to the content changing
    firstSelectableObject: function() {
        var cachedSelection = Footprint.layerTreeController.getPath('selection.firstObject');
        if (cachedSelection) {
            return cachedSelection;
        } else if (this.get('content')) {
            return this.getPath('content.firstObject');
        }
    }.property(),
});

/***
 * Nested store version of the Layers for editing. The selection is bound oneWay to the main controller, so that
 * when the main controller selection changes, this one updates its corresponding record
 * The nested store to that of the Footprint.dbEntitiesEditController, since the latter
 * is the main controller of DbEntity/Layer editing and has its nestedStore set by the CrudState
 */
Footprint.layersEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:YES,
    sourceController: Footprint.layersController,
    recordType: 'Footprint.Layer',
    selectionBinding: SC.Binding.oneWay('Footprint.layerTreeController.selection'),
    orderBy: ['name ASC', 'id ASC'], // id just here to fix an SC bug
});

Footprint.layerEditController = SC.ObjectController.create({
    contentBinding: SC.Binding.oneWay('Footprint.layersEditController*selection.firstObject'),
    layerIsSaving: NO,
});

Footprint.layerTreeController = SC.TreeController.create(SC.CollectionViewDelegate, Footprint.LayerStyleSelectionSupport, {
    treeItemIsGrouped: YES,
    allowsMultipleSelection: NO,
    allowsEmptySelection: NO,

    // Delegate the status to the leaves property of the content to get a status
    // The status is used by Footprint.SelectController to know they can assign their content to the selected item
    // or else first item of the leaves list
    statusBinding:SC.Binding.oneWay('*leaves.status'),
    /***
     * Returns the record type
     */
    recordType: function() {
        return this.getPath('leaves.firstObject.constructor');
    }.property('leaves').cacheable(),

    content: SC.Object.create({
        treeItemIsExpanded: NO,
        leaves: null,
        leavesBinding: SC.Binding.from('Footprint.scenarioLayerLibraryApplicationController.layers'),
        leavesStatus: null,
        leavesStatusBinding: SC.Binding.oneWay('*leaves.status'),
        dbEntitiesStatus: null,
        dbEntitiesStatusBinding: SC.Binding.oneWay('Footprint.dbEntitiesController.status'),
        featureBehaviorsStatus: null,
        featureBehaviorsStatusBinding: SC.Binding.oneWay('Footprint.featureBehaviorsController.status'),

        allCategoriesStatus: null,
        allCategoriesStatusBinding: SC.Binding.oneWay('Footprint.dbEntityAllCategoriesController.status'),

        categoriesBinding: SC.Binding.oneWay('Footprint.dbEntityAllCategoriesController.arrangedObjects'),

        /**
         * Creates a single SC.TreeItemContent for a single StyleAttribute, for the style legend.
         */
        _createStyleTreeItemContent: function(is_basemap, attribute) {
            var styleValueContexts = attribute.get('style_value_contexts');
            var styles = [];
            var defaultValue = '';
            if (styleValueContexts &&
                (styleValueContexts.get('length') > 0) &&
                !is_basemap) {
                if (styleValueContexts.get('length') > 1) {
                    defaultValue = 'Null';
                }
                styles = styleValueContexts.map(function (styleValueContext) {
                    return SC.Object.create({
                        style: Footprint.store.createRecord(
                            Footprint.Style,
                            $.extend({}, styleValueContext.getPath('style.attributes'))),
                        title: styleValueContext.get('value') || defaultValue,
                        isSelected: NO,
                        symbol: styleValueContext.get('symbol'),
                        isStyle: YES
                    });
                }, this);
            }
            return SC.Object.create(SC.TreeItemContent, $.extend({}, attribute, {
                treeItemIsExpanded: YES,
                title: attribute.get('style_type') == 'single' ? 'Single Symbol' : attribute.get('attribute'),
                isAttribute: YES,
                style: null,
                treeItemChildren: styles
            }));
        },

        /**
         * Maps an array of StyleAttributes into an array of SC.TreeItemContents
         */
        _getActiveStyleAttributeItems: function(is_basemap, active_styles) {
            var treeItems = active_styles.map(this._createStyleTreeItemContent.bind(this, is_basemap));
            return treeItems;
        },

        /**
         * Create a single SC.TreeItemContent for a single layer.
         */
        _createLayerTreeItemContent: function(layer) {
            var is_basemap = layer.get('isBaseMap'),
                active_style_key = layer.get('active_style_key'),
                active_styles = (layer.getPath('medium.style_attributes') || []).filter(function(style_attribute) {
                    return style_attribute.get('key') === active_style_key;
                });

            var styleAttributes = this._getActiveStyleAttributeItems(is_basemap, active_styles);

            var layerName = layer.get('name');
            return SC.Object.create(SC.TreeItemContent, $.extend({}, layer, {
                title: layerName,
                isLayer: YES,
                hasCheckBox: YES,
                layerVisible: function (propKey, value) {
                    if (typeof(value) !== 'undefined') {
                        layer.set('applicationVisible', value);
                        return value;
                    } else if (layer.get('applicationVisible')) {
                        return layer.get('applicationVisible');
                    }
                    return false;
                }.property('applicationVisible').cacheable(),
                treeItemIsExpanded: NO,
                treeItemChildren: styleAttributes.length > 0 ? styleAttributes : null
            }));
        },

        /**
         * Turns a list of layers into a list of TreeItemContents.
         */
        _getLayerTreeItems: function(layers) {
            var treeItems = layers.map(this._createLayerTreeItemContent, this).sort(function(a, b) {
                if (a.get('name') < b.get('name')) return -1;
                if (a.get('name') > b.get('name')) return 1;
                return 0;
            });
            return treeItems;
        },

        /**
         * Creates a single SC.TreeItemContent for a Category.
         * Returns null if the Category has no layers, so that we don't show the Category
         */
        _createCategoryTreeItemContent: function(category) {
            // Find leaves whose category value matches that of this category
            var layers = this.get('leaves').filter(function(layer) {
                return category.get('value') === layer.categoryValue('DbEntityClassification');
            });
            // If no layers than return null. We'll filter out this category
            if (!layers.get('length'))
                return null;

            return SC.Object.create({
                treeItemChildren: this._getLayerTreeItems(layers),
                // TODO: UF-491 - Get this from the db.
                name: category.get('value').replace(/_/g, ' ').capitalize(),
                treeItemIsExpanded:YES
            });
        },
        /**
         * Turns the current list of categories into an array of TreeItemContents.
         */
        _getCategoryTreeItems: function() {
            var categories = this.get('categories');
            if (!categories) {
                return categories;
            }
            // Map each Category to a TreeItem. Use compact to filter out null TreeItems that result when the
            // category lacks any layers
            var treeItems = categories.toArray().reverse().map(this._createCategoryTreeItemContent, this).compact();
            return treeItems;
        },

        treeItemChildren: function () {
            if (this.get('leaves') &&
                (this.get('leavesStatus') & SC.Record.READY) &&
                (this.get('dbEntitiesStatus') & SC.Record.READY) &&
                this.get('categories') &&
                this.get('featureBehaviorsStatus') & SC.Record.READY) {

                var categories = this._getCategoryTreeItems();
                return categories;
            } else {
                return [];
            }
        }.property('leaves', 'leavesStatus', 'dbEntitiesStatus', 'categories', 'featureBehaviorsStatus').cacheable(),
    }),

    contentDidChange: function() {
        // Clear the selection when the leaves change. firstSelectableObject will set it to something after.
        if (this.didChangeFor('leaves', 'leavesStatus')) {
            this.deselectObjects(this.getPath('selection'));
        }
    }.observes('.leaves', '.leavesStatus'),

    // Update the treeItemChildren if the leaves change
    leavesDidChange: function() {
        this.get('content').propertyDidChange('treeItemChildren');
    }.observes('*leaves.[]'),

    cachedSelectedLayer: null,
    cachedSelectedLayerBinding: SC.Binding.oneWay('Footprint.CachedSelectedLayer.currentSelection'),

    firstSelectableObject: function() {
        var cachedSelectedLayer = this.get('cachedSelectedLayer');
        return (this.get('leavesStatus') & SC.Record.READY) ? this.get('leaves').find(function(item) {
            if (cachedSelectedLayer) {
                return item.getPath('db_entity.key') == cachedSelectedLayer.getPath('db_entity.key');
            } else {
                return item.get('isForeground') && item.getPath('applicationVisible');
            }
        }) : null;
    }.property(),

    cachedSelectedLayerObserver: function() {
        var selection = this.getPath('selection.firstObject');
        //only update if there is a selection
        if (selection) {
            Footprint.CachedSelectedLayer.set('currentSelection', selection);
        }
    }.observes('selection'),

    /***
    * Deals with a bug in SC.TreeItemObserver where the expandedState
    * is set to closed if the treeItemChildren are not immediately
    * present. We assume that the root element is never displayed and
    * thus should always be expanded here when the treeItemChildren
    * exist
    */
    treeItemChildrenObserver: function () {
        if ((this.get('leavesStatus') & SC.Record.READY) && (this.get('dbEntitiesStatus') & SC.Record.READY)) {
            var arrangedObjects = this.get('arrangedObjects');
            if (arrangedObjects) {
                this.set('treeItemIsExpanded', YES);
            }
        }
    }.observes('.leaves', '.leavesStatus', '.dbEntitiesStatus'),

    toString: function() {
        return this.toStringAttributes('content'.w());
    },
});

/***
 * A base controller to filter layers by behavior.
 * Currently this works by setting the propertyKey property
 * to a computedProperty on the Layer model
 */
Footprint.LayerTypeController = SC.ArrayController.extend({
    propertyKey: null,
    layers: null,
    layersBinding: SC.Binding.oneWay('Footprint.layersController.arrangedObjects'),
    layersStatus: null,
    layersStatusBinding: SC.Binding.oneWay('Footprint.layersController.status'),
    featureBehaviorsStatus: null,
    featureBehaviorsStatusBinding: SC.Binding.oneWay('Footprint.featureBehaviorsController.status'),

    // TODO This might not be needed anymore
    layersDidChange: function() {
        this.invokeOnce('doUpdateContent');
    }.observes('*layers.@each.status'),

    doUpdateContent: function() {
        this.notifyPropertyChange('content');
    },

    content: function() {
        if (!(this.get('layersStatus') & SC.Record.READY) ||
            !(this.get('featureBehaviorsStatus') & SC.Record.READY))
            return null;
        return (this.get('layers') || SC.EMPTY_ARRAY).filterProperty(this.get('propertyKey'));
    }.property('propertyKey', 'layersStatus', 'featureBehaviorsStatus', 'layers').cacheable(),
});

/****
 * Base Map layers.
 */
Footprint.layersBackgroundController = Footprint.LayerTypeController.create({
    propertyKey: 'isBaseMap'
});

/****
 * Foreground layers.
*/
Footprint.layersForegroundController = Footprint.LayerTypeController.create({
    propertyKey: 'isForeground'
});

/****
 * Layers that have been selected to be on the map.
 */
Footprint.layersVisibleController = SC.ArrayController.create({
    // Convenience flag for the menu panel.
    layersMenuSectionIsVisible: NO,
    layers: null,
    layersBinding: SC.Binding.oneWay('Footprint.layersController.arrangedObjects'),
    layersStatus: null,
    layersStatusBinding: SC.Binding.oneWay('Footprint.layersController.status'),
    // The controller doesn't specifically need anything from the FeatureBehaviors yet,
    // but dependant controllers do
    featureBehaviorsStatus: null,
    featureBehaviorsStatusBinding: SC.Binding.oneWay('Footprint.featureBehaviorsController.status'),
    // Manually observe membership and invalidate content to work around annoyances.
    layersDidChange: function() {
        this.notifyPropertyChange('content');
    }.observes('*layers.@each.applicationVisible'),

    content: function() {
        if (this.get('layers') &&
           (this.get('layersStatus') & SC.Record.READY) &&
           (this.get('featureBehaviorsStatus') & SC.Record.READY)) {
            var layers = this.get('layers');
            return layers.filterProperty('applicationVisible', YES);
        }
    }.property('layersStatus', 'featureBehaviorsStatus', 'layers').cacheable(),
});

/****
 * The class for the foreground and background list controllers.
 */
Footprint.LayersVisibleListController = SC.ArrayController.extend({
    // A property of the Layer for determining inclusion. Currently just isForeground or isBaseMap
    propertyKey: null,
    layers: null,
    layersBinding: SC.Binding.oneWay('Footprint.layersVisibleController.content'),

    content: function() {
        if (this.get('layers')) {
            return (this.get('layers') || SC.EMPTY_ARRAY).filterProperty(this.get('propertyKey')).sortProperty('sortPriority');
        }
    }.property('layers', 'propertyKey', 'sortPriority').cacheable(),

    // This updates the content's sort property, then alerts the authorities.
    contentDidUpdate: function() {
        var content = this.get('content');
        if (!content) return;
        // Scan ourselves and update sortPriority appropriately.
        var i, len = content.get('length'),
            obj,
            currentPriority = 0;
        for (i = 0; i < len; i++) {
            obj = content.objectAt(i);
            currentPriority += 10;
            obj.setIfChanged('sortPriority', currentPriority);
        }
        this.invokeOnce('_doUpdateMap');
    }.observes('*content.[]'),

    _doUpdateMap: function() {
        Footprint.statechart.sendAction('visibleLayersDidChange');
    },
});

/****
 * Foreground leaves that have been made visible on the map.
 */
Footprint.layersVisibleForegroundController = Footprint.LayersVisibleListController.create({
    propertyKey: 'isForeground'
});

/****
 * Background layers that have been made visible on the map.
 */
Footprint.layersVisibleBaseMapController = Footprint.LayersVisibleListController.create({
    propertyKey: 'isBaseMap'
});

/***
 * Binds to the currently selected PresentationMedium
 * @type {*}
 */
Footprint.layerActiveController = SC.ObjectController.create({
    contentBinding: SC.Binding.oneWay('Footprint.layerTreeController*selection.firstObject'),
    activeScenario: null,
    activeScenarioBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),

    activeScenarioStatus: null,
    activeScenarioStatusBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.status'),

    editSectionIsVisible: null,
    editSectionIsVisibleBinding: SC.Binding.oneWay('Footprint.mainPaneButtonController.editSectionIsVisible'),

    dbEntityStatus: null,
    dbEntityStatusBinding: SC.Binding.oneWay('*content.dbEntityStatus'),

    /***
     * When the status becomes READY_CLEAN, send an event so the LayerSelection can load. This only matters
     * for loading the LayerSelection for the initial layer when a Scenario loads
     */
    statusObserver: function() {
        if (this.didChangeFor('statusCheck', 'status') && this.get('status') === SC.Record.READY_CLEAN)
            Footprint.statechart.sendEvent('layerDidBecomeReady');
    }.observes('.status'),

    /***
     * The default edit section view based on the layer. This could be an analysis tool view, the
     * scenario builder view, or the agriculture builder view
     */
    editorView: function() {
        if (this.getPath('content') &&
                this.getPath('content.dbEntityKey') &&
            (this.get('status') & SC.Record.READY) &&
            (this.get('dbEntityStatus') & SC.Record.READY)
        ) {

            var activeLayerClassKey = this.getPath('content.dbEntityKey').toUpperCase()[0] + this.getPath('content.dbEntityKey').slice(1).camelize();
            var activeLayerBehaviorKey =this.getPath('content.db_entity.feature_behavior.behavior.key');

            if ('behavior__editable_feature' == activeLayerBehaviorKey && activeLayerClassKey) {
                return 'Footprint.%@EditorView'.fmt(activeLayerClassKey);
            }
            if ('behavior__scenario_end_state' == activeLayerBehaviorKey) {
                return 'Footprint.ScenarioBuilderManagementView';
            }
            if ('behavior__agriculture_scenario' == activeLayerBehaviorKey ||
                    'behavior__base_agriculture' == activeLayerBehaviorKey) {
                return 'Footprint.AgricultureBuilderManagementView';
            }
        }
        // No default editor for this layer
        return 'Footprint.DefaultEditorView';

    }.property('content', 'status', 'activeScenario', 'activeScenarioStatus', 'editSectionIsVisible').cacheable(),

    layerBehavior: null,
    layerBehaviorBinding: SC.Binding.oneWay('*content.db_entity.feature_behavior.behavior.key'),
    /***
     * Return true is the given layer is editable
    */
    layerIsEditable: function() {
        if (this.getPath('layerBehavior')) {
             var layer_behavior = this.getPath('layerBehavior');
             if (layer_behavior == 'behavior__editable_feature'
                 || layer_behavior == 'behavior__scenario_end_state'
                 || layer_behavior == 'behavior__agriculture_scenario'
                 || layer_behavior == 'behavior__base_agriculture'
                 || this.get('value') === YES) {
                 return YES;
             }
             else {
                 return NO
             }
         }
         return NO
    }.property('layerBehavior').cacheable(),

    /***
     * Returns true if a Builder view is enabled, false otherwise
     */
    isBuilderView: function() {
        return ['Footprint.ScenarioBuilderManagementView', 'Footprint.AgricultureBuilderManagementView'].contains(
            this.get('editorView')
        );
    }.property('editorView').cacheable()
});

/***
 * Combines the layers and all important dependencies so that we can have reliable status
 */
Footprint.layersAndDependenciesController = SC.ArrayController.create(SC.ArrayStatus, {
    layers: null,
    layersBinding: SC.Binding.oneWay('Footprint.layersController.content'),
    layersStatus: null,
    layersStatusBinding: SC.Binding.oneWay('Footprint.layersController.status'),
    dbEntities: null,
    dbEntitiesBinding: SC.Binding.oneWay('Footprint.dbEntitiesController.content'),
    dbEntitiesStatus: null,
    dbEntitiesStatusBinding: SC.Binding.oneWay('Footprint.dbEntitiesController.status'),
    featureBehaviors: null,
    featureBehaviorsBinding: SC.Binding.oneWay('Footprint.featureBehaviorsController.content'),
    featureBehaviorsStatus: null,
    featureBehaviorsStatusBinding: SC.Binding.oneWay('Footprint.featureBehaviorsController.status'),
    content: function() {
        if ((this.get('dbEntitiesStatus') & SC.Record.READY) &&
            (this.get('layersStatus') & SC.Record.READY) &&
            (this.get('featureBehaviorsStatus') & SC.Record.READY) &&
            this.get('layers')) {
            return this.get('layers').toArray()
                .concat(this.get('dbEntities'))
                .concat(this.get('featureBehaviors'));
        }
        return null;
    }.property('layers', 'layersStatus', 'dbEntities', 'dbEntitiesStatus', 'featureBehaviors', 'featureBehaviorsStatus').cacheable(),
});

/***
 * All current layers that have the editable_feature behavior
 */
Footprint.editableLayersController = Footprint.ArrayController.create({
    activeScenario: null,
    activeScenarioBinding: SC.Binding.oneWay('F.scenarioActiveController.content'),
    activeScenarioStatus: null,
    activeScenarioStatusBinding: SC.Binding.oneWay('*activeScenario.status'),
    layers: null,
    layersBinding: SC.Binding.oneWay('F.layersController.content'),
    layersStatus: null,
    layersStatusBinding: SC.Binding.oneWay('*layers.status'),

    layersDidChange: function() {
        this.invokeOnce('doUpdateContent');
    }.observes('*layers.@each.db_entity.status'),

    doUpdateContent: function() {
        this.notifyPropertyChange('content');
    },

    content: function() {
        var layers = this.get('layers');
        if (!layers) {
            return null;
        } else {
            return layers.filter(function (layer) {
                return layer.getPath('db_entity.feature_behavior.behavior.key') == 'behavior__editable_feature';
            });
        }
    }.property('layers', 'layersStatus', 'activeScenario', 'activeScenarioStatus').cacheable(),
});

/***
 * Warning: Don't make this an ObjectController. It will fire an infinite loop of observers
 * Provide the LayerLibrary for each scope that the user has permission to edit/view
 * We'll start with just the project and scenario and expand later
 * The content is an SC.Object keyed by ConfigEntity key and valued by the Application edit LayerLibrary
 * controller content.
 * TODO we don't need this info from controllers. We could fetch it ourselves if we had a nestedStore set
 */
Footprint.layerLibrariesApplicationEditController = SC.Object.create({
    projectLayerLibrary: null,
    projectLayerLibraryBinding: SC.Binding.oneWay('Footprint.projectLayerLibraryApplicationEditController.content'),
    projectLayerLibraryStatus: null,
    projectLayerLibraryStatusBinding: SC.Binding.oneWay('*projectLayerLibrary.status'),
    scenarioLayerLibrary: null,
    scenarioLayerLibraryBinding: SC.Binding.oneWay('Footprint.scenarioLayerLibraryApplicationEditController.content'),
    scenarioLayerLibraryStatus: null,
    scenarioLayerLibraryStatusBinding: SC.Binding.oneWay('*scenarioLayerLibrary.status'),
    content: function() {
        if ((this.get('projectLayerLibraryStatus') & SC.Record.READY) &&
            (this.get('scenarioLayerLibraryStatus') & SC.Record.READY)) {
            return mapToSCObject(
                [[this.getPath('projectLayerLibrary.config_entity.key'), this.get('projectLayerLibrary')],
                 [this.getPath('scenarioLayerLibrary.config_entity.key'), this.get('scenarioLayerLibrary')]],
                function(tuple) {
                    return tuple;
                }
            );
        }
    }.property('projectLayerLibraryStatus', 'projectLayerLibrary', 'scenarioLayerLibraryStatus', 'scenarioLayerLibrary').cacheable(),
});

/***
 * Stores the LayerLibrary of the active Scenario and every LayerLibrary above that in the hierarchy
 */
Footprint.scenarioHierarchyLayerLibrariesEditController = SC.ArrayController.create(Footprint.CalculatedStatusSupport);
