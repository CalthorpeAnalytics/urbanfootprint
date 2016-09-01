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

sc_require('states/records_are_ready_state');

/***
 * The state that manages the projects pane at the top of the application
 * @type {Class}
 */
Footprint.ShowingBuiltFormsState = SC.State.design({
    buildingDidChange: function(context) {
        // Let this propagate through to other listeners
        return NO;
    },
    buildingsDidChange: function(context) {
        this.gotoState('buildingsAreReadyState', context)
    },

    cropDidChange: function(context) {
        // Let this propagate through to other listeners
        return NO;
    },
    cropsDidChange: function(context) {
        this.gotoState('cropsAreReadyState', context)
    },

    buildingTypeDidChange: function(context) {
        // Let this propagate through to other listeners
        return NO;
    },
    buildingTypesDidChange: function(context) {
        this.gotoState('buildingTypesAreReadyState', context)
    },
    cropTypeDidChange: function(context) {
        // Let this propagate through to other listeners
        return NO;
    },
    cropTypesDidChange: function(context) {
        this.gotoState('cropTypesAreReadyState', context)
    },

    placetypeDidChange: function(context) {
        // Let this propagate through to other listeners
        return NO;
    },
    placetypesDidChange: function(context) {
        this.gotoState('placetypesAreReadyState', context)
    },
    landscapeTypeDidChange: function(context) {
        // Let this propagate through to other listeners
        return NO;
    },
    landscapeTypesDidChange: function(context) {
        this.gotoState('landscapeTypesAreReadyState', context)
    },

    /***
     * Normalize the percents of a list of PrimaryComponentPercent instance, or PlacetypeComponentPercent instances.
     * Since the user can set the percents to any value, this action normalizes them to add up to 1
     * @param context
     */
    doNormalizePercents: function(context) {
        var content = context.get('content');
        // Find the total to be the denominator
        var total = $.accumulate(content.toArray(), function(item, previous) {
            return (previous || 0)+parseFloat(item.get('percent'));
        });
        if (total == 0) {
            // If all are 0 make the denominator 1
            total=1;
        }
        // Normalize by dividing each percent by the denominator
        content.forEach(function(item) {
            item.setIfChanged('percent', item.get('percent') / total);
        })
    },

    doManageBuiltForms: function(context) {
        // Default behavior is to view/manage buildings
        var pluralContext = toArrayController(context, {crudType:'view'});
        this.doManageBuildings(pluralContext);
    },

    doManageAgricultureTypes: function(context) {
        // Default behavior is to view/manage buildings
        var pluralContext = toArrayController(context, {crudType:'view'});
        this.doManageCrops(pluralContext);
    },
    doManageCrops: function(context) {
        // Tell the modal_state to show the BuiltForm panes,
        // even though our data might not be ready yet.
        var pluralContext = toArrayController(filterKeys(context, ['crudType', 'content']), this.get('cropContext'));
        this.gotoState('builtFormEditState', pluralContext);
    },
    cropContext: function () {
        return {
            infoPane: 'Footprint.BuiltFormInfoPane',
            nowShowing: 'Footprint.ManageCropView',
            recordType: Footprint.Crop,
            recordsEditController: Footprint.cropsEditController,
            loadingController: Footprint.cropsController
        };
    }.property().cacheable(),

    doManageBuildings: function(context) {
        // Tell the modal_state to show the BuiltForm panes,
        // even though our data might not be ready yet.
        var pluralContext = toArrayController(filterKeys(context, ['crudType', 'content']), this.get('buildingContext'));
        this.gotoState('builtFormEditState', pluralContext);
    },
    buildingContext: function () {
        return {
            infoPane: 'Footprint.BuiltFormInfoPane',
            nowShowing: 'Footprint.ManageBuildingView',
            recordType: Footprint.Building,
            recordsEditController: Footprint.buildingsEditController,
            loadingController: Footprint.buildingsController
        };
    }.property().cacheable(),

    doManageBuildingTypes: function(context) {
        var pluralContext = toArrayController(filterKeys(context, ['crudType', 'content']), this.get('buildingTypeContext'));
        this.gotoState('builtFormEditState', pluralContext);
    },
    buildingTypeContext: function () {
        return {
            infoPane: 'Footprint.BuiltFormInfoPane',
            nowShowing: 'Footprint.ManageBuildingTypeView',
            recordType: Footprint.BuildingType,
            recordsEditController: Footprint.buildingTypesEditController,
            loadingController: Footprint.buildingTypesController,
            dependencyContext: this.get('buildingContext')
        };
    }.property().cacheable(),


    doManageCropTypes: function(context) {
        var pluralContext = toArrayController(filterKeys(context, ['crudType', 'content']), this.get('cropTypeContext'));
        this.gotoState('builtFormEditState', pluralContext);
    },
    cropTypeContext: function () {
        return {
            infoPane: 'Footprint.BuiltFormInfoPane',
            nowShowing: 'Footprint.ManageCropTypeView',
            recordType: Footprint.CropType,
            recordsEditController: Footprint.cropTypesEditController,
            loadingController: Footprint.cropTypesController,
            dependencyContext: this.get('cropContext')
        };
    }.property().cacheable(),

    doManagePlacetypes: function(context) {
        var pluralContext = toArrayController(filterKeys(context, ['crudType', 'content']), this.get('placetypeContext'));
        this.gotoState('builtFormEditState', pluralContext);
    },
    placetypeContext: function() {
        return {
            infoPane: 'Footprint.BuiltFormInfoPane',
            nowShowing: 'Footprint.ManagePlacetypeView',
            recordType: Footprint.UrbanPlacetype,
            recordsEditController: Footprint.placetypesEditController,
            loadingController: Footprint.placetypesController,
            dependencyContext: this.get('buildingTypeContext')
        };
    }.property().cacheable(),

    doManageLandscapeTypes: function(context) {
        var pluralContext = toArrayController(filterKeys(context, ['crudType', 'content']), this.get('landscapeTypeContext'));
        this.gotoState('builtFormEditState', pluralContext);
    },
    landscapeTypeContext: function() {
        return {
            infoPane: 'Footprint.BuiltFormInfoPane',
            nowShowing: 'Footprint.ManageLandscapeTypeView',
            recordType: Footprint.LandscapeType,
            recordsEditController: Footprint.landscapeTypesEditController,
            loadingController: Footprint.landscapeTypesController,
            dependencyContext: this.get('cropTypeContext')
        };
    }.property().cacheable(),

    initialSubstate: 'readyState',
    readyState: SC.State,

    builtFormEditState: SC.State.extend({
        initialSubstate: 'loadingState',

        /***
         * Loads the context's loadingController using a remote query. The loadingController is the non-nested source
         * for the recordsEditController, although the latter won't populate until given a nestedStore.
         */
        loadingState: Footprint.LoadingState.extend({
            didLoadEvent: 'didLoadBuiltForms',
            didFailEvent: 'didFailToLoadBuiltForms',

            enterState: function(context) {
                // Show the modal while the records are loading so that the user knows something is happening.
                Footprint.statechart.sendAction(
                    'doShowModal',
                    context
                );

                this.set('loadingController', context.get('loadingController')) ;
                sc_super();
            },

            recordArray: function() {
                if (this.getPath('loadingController.status') === SC.Record.READY_CLEAN)
                    return this.getPath('loadingController.content');
                return Footprint.store.find(SC.Query.create({
                    recordType: this._context.get('recordType'),
                    location: SC.Query.REMOTE
                }));
            },

            didLoadBuiltForms: function(context) {
                if (this.getPath('_context.dependencyContext'))
                    // Load the dependency controller. For instance,
                    // PlacetypeComponents need to load the list of PrimaryComponents for the former's percent mix pulldown list
                    this.gotoState('dependencyLoadingState', this._context);
                else
                    // Otherwise proceed straight to builtFormsAreReadyState
                    this.gotoState('builtFormsAreReadyState', this._context);
            },
            didFailToLoadBuiltForms: function() {
                this.gotoState('errorState');
            }
        }),

        /***
         * Called after loadingState to load a dependency if one exists. After this complete the state goes to builtFormsAreReadyState
         */
        dependencyLoadingState: Footprint.LoadingState.extend({
            didLoadEvent: 'didLoadDependencyBuiltForms',
            didFailEvent: 'didFailToLoadDependencyBuiltForms',

            enterState: function(context) {
                // Call super, changing the context to that of the dependencyContext so that we load the data into the
                // correct Controller. Include the current context so that we can pass it on to the next state as the
                // context.
                arguments.callee.base.apply(this, [
                    toArrayController(
                        context.get('dependencyContext'),
                        {passThroughContext: context}
                    )
                ]);
            },

            recordArray: function() {
                if (this.getPath('loadingController.status') === SC.Record.READY_CLEAN)
                    return this.getPath('loadingController.content');
                return Footprint.store.find(SC.Query.create({
                    recordType: this._context.get('recordType'),
                    location: SC.Query.REMOTE
                }));
            },

            didLoadDependencyBuiltForms: function(context) {
                // Dependency is loaded, move on, passing our original context.
                this.gotoState('builtFormsAreReadyState', this._context.get('passThroughContext'));
            },
            didFailToLoadDependencyBuiltForms: function() {
                // Failure sense us back to the top level
                this.gotoState(this.getPath('parentState.parentState.fullName'));
            }
        }),

        builtFormsAreReadyState: Footprint.RecordsAreReadyState.extend({
            recordsDidUpdateEvent: 'builtFormsDidChange',
            recordsDidFailToUpdateEvent: 'builtFormsDidFailToUpdate',
            updateAction: 'doBuiltFormUpdate',
            undoAction: 'doBuiltFormUndo',

            // Our base record type for matching postSave events
            baseRecordType: Footprint.BuiltForm,
            // We create records as subclasses, so find them in the store as such
            findByBaseRecordType: NO,

            doManageBuildings: function(context) {
                return this._doConfirmManagerChange(toArrayController(context, {
                    'postConfirmAction':'doManageBuildings'}));
            },

            doManageBuildingTypes: function(context) {
                return this._doConfirmManagerChange(toArrayController(context, {
                    'postConfirmAction':'doManageBuildingTypes'}));
            },

            doManagePlacetypes: function(context) {
                return this._doConfirmManagerChange(toArrayController(context, {
                    'postConfirmAction':'doManagePlacetypes'}));
            },

            doManageCrops: function(context) {
                return this._doConfirmManagerChange(toArrayController(context, {
                    'postConfirmAction':'doManageCrops'}));
            },

            doManageCropTypes: function(context) {
                return this._doConfirmManagerChange(toArrayController(context, {
                    'postConfirmAction':'doManageCropTypes'}));
            },

            doManageLandscapeTypes: function(context) {
                return this._doConfirmManagerChange(toArrayController(context, {
                    'postConfirmAction':'doManageLandscapeTypes'}));
            },

            doRevert: function(context) {
                return this._doConfirmManagerChange(toArrayController(context, {
                    'postConfirmAction':'doRevert'}));
            },

            _doConfirmManagerChange: function(context) {
                // If changing from a different BuiltForm record type and outstanding changes exist,
                // warn the user that their changes will be lost.
                if (context.get('confirm') || !this._context.getPath('recordsEditController.store.hasChanges')) {
                    if (this._context.getPath('recordsEditController.store.hasChanges'))
                        // Clear the previous changes
                        this._context.getPath('recordsEditController.store').discardChanges();

                    // User confirmed cancel or no changes. Don't warn just bubble up action to parent state
                    return NO;
                }
                if (this._context.getPath('recordsEditController.store.hasChanges')) {
                    // We'll return to this action with confirm==YES if the user confirms the cancel
                    Footprint.statechart.sendAction('doPromptCancel', context);
                }
            },

            /***
             * Handles picking component selection to add Buildings to the BuildingType percent components or
             * to add BuildingTypes to the PlaceType percent components, depending on which recordType is in
             * active editing
             * @param context
             */
            doPickComponentPercent: function(context) {
                var containerBuiltForm = this._context.getPath('recordsEditController.selection.firstObject');
                if (!containerBuiltForm) {
                    // Something's wrong. We shouldn't be here
                    return;
                }
                // Our context is the SourceListView from which the user selected an item
                var builtFormComponentToAdd = context.getPath('selection.firstObject');

                var store = this._context.getPath('recordsEditController.store');
                if (this._context.get('recordType').kindOf(Footprint.PlacetypeComponent)) {
                    // Create a new PrimaryComponentPercent using the builtFormToAdd (a PrimaryComponent)
                    var newRecord = store.createRecord(
                        Footprint.PrimaryComponentPercent, {
                            component_class: builtFormComponentToAdd.constructor.toString().split('.').slice(-1)[0],
                            container_class: this._context.get('recordType').toString().split('.').slice(-1)[0],
                            placetype_component: containerBuiltForm.get('id'),
                            primary_component: builtFormComponentToAdd.get('id'),
                            percent: 0
                        },
                        Footprint.Record.generateId());

                    containerBuiltForm.get('component_percents').pushObject(newRecord);
                }
                else if (this._context.get('recordType').kindOf(Footprint.Placetype)) {
                    // Create a new PrimaryComponentPercent using the builtFormToAdd (a PlacetypeComponent)
                    var newRecord = store.createRecord(
                        Footprint.PlacetypeComponentPercent, {
                            component_class: builtFormComponentToAdd.constructor.toString().split('.').slice(-1)[0],
                            container_class: this._context.get('recordType').toString().split('.').slice(-1)[0],
                            placetype: containerBuiltForm.get('id'),
                            placetype_component: builtFormComponentToAdd.get('id'),
                            percent: 0
                        },
                        Footprint.Record.generateId());

                    containerBuiltForm.get('component_percents').pushObject(newRecord);
                }
                else if (this._context.get('recordType') == Footprint.Building) {
                    // Create a new BuildingUsePercent using the builtFormToAdd (a Building)
                    var newRecord = store.createRecord(
                        Footprint.BuildingUsePercent, {
                            building_attribute_set: containerBuiltForm.getPath('building_attribute_set.id'),
                            building_use_definition: builtFormComponentToAdd.get('id'),
                            square_feet_per_unit: 1000,
                            efficiency: 1,
                            percent: 0
                        },
                        Footprint.Record.generateId());
                    containerBuiltForm.getPath('building_attribute_set.building_use_percents').pushObject(newRecord);
                }
                return YES;
            },

            /***
             * Removes a *ComponentPercent instance from the component percent list. This is the opposite of doPickSelection
             * @param context
             */
            doRemoveRecord: function(context) {
                var containerBuiltForm = this._context.getPath('recordsEditController.selection.firstObject');
                // Our context is the SourceListView from which the user selected an item
                var builtFormToRemove = context.get('content');
                if (this._context.get('recordType').kindOf(Footprint.PlacetypeComponent)) {
                    // Remove the PrimaryComponentPercent
                    containerBuiltForm.get('primary_component_percents').removeObject(builtFormToRemove);
                }
                else if (this._context.get('recordType').kindOf(Footprint.Placetype)) {
                    // Remove the PlacetypeComponentPercent
                    containerBuiltForm.get('placetype_component_percents').removeObject(builtFormToRemove);
                }
                else if (this._context.get('recordType') == Footprint.Building) {
                    // Remove the PlacetypeComponentPercent
                    containerBuiltForm.getPath('building_attribute_set.building_use_percents').removeObject(builtFormToRemove);
                }
            },

            /***
             * Event sent when a BuildingUsePercent property changes to inform dependent records of the change.
             * For example, when a child instance percent changes, the parent needs to resum the values accordingly
             */
            buildingUsePercentPropertyDidChange: function(context) {
                var buildingUsePercent = context.get('content');

                // Find the parent BuildingUseDefinition
                var parentBuildingUseDefinition = buildingUsePercent.getPath('building_use_definition.category');
                // Get the ChildArray container
                var buildingUsePercents = buildingUsePercent.get('buildingUsePercents');
                // Find or create the parent BuildingUsePercent
                var parentBuildingUsePercent = buildingUsePercent.getPath('parentBuildingUsePercent');
                if (!parentBuildingUsePercent) {
                    // Create the parent if it doesn't exist
                    parentBuildingUsePercent = buildingUsePercents.createNestedRecord(
                        Footprint.BuildingUsePercent,
                        {
                            building_use_definition: parentBuildingUseDefinition.get('id'),
                            building_attribute_set: buildingUsePercents.getPath('parentRecord.id'),
                            efficiency: 0,
                            square_feet_per_unit: 0
                        });
                }
                // Set the parentBuildingUsePercent.percent to the sum of the children
                parentBuildingUsePercent.setIfChanged('percent',
                    parseFloat(buildingUsePercent.get('buildingUsePercents').filter(function(buildingUsePercent) {
                        // Filter for children
                        return buildingUsePercent.getPath('building_use_definition.category')==parentBuildingUseDefinition;
                    }).reduce(function(percentTotal, buildingUsePercent) {
                        // Sum percents
                        return buildingUsePercent.get('percent') + percentTotal;
                    }, 0).toFixed(2))
                );

                // Set the parentBuildingUsePercent.total_far to the sum of each children's percent*totalFar
                var totalFar = buildingUsePercents.getPath('parentRecord.total_far');
                parentBuildingUsePercent.setIfChanged('floor_area_ratio',
                    parseFloat(buildingUsePercent.get('buildingUsePercents').filter(function(buildingUsePercent) {
                        // Filter for children
                        return buildingUsePercent.getPath('building_use_definition.category')==parentBuildingUseDefinition;
                    }).reduce(function(percentTotal, buildingUsePercent) {
                        // Sum percents
                        return buildingUsePercent.get('percent')*totalFar + percentTotal;
                    }, 0).toFixed(2))
                );
            },

            postSavePublishingFinished: function(context) {
                // Create the base type version for the BuiltFormSet collections
                var records = context.get('records');
                var representativeRecord = records[0];
                var store = representativeRecord.get('store');
                var attributes = representativeRecord.attributes();

                // Assume shared built_form_sets for now
                representativeRecord.get('built_form_sets').forEach(function(builtFormSet) {
                    // Locally update any BuiltFormSet that should contain this BuiltForm
                    var builtFormSetStatus = builtFormSet.get('status');
                    records.forEach(function(record) {
                        var storeKey = store.loadRecord(
                            Footprint.BuiltForm,
                            attributes,
                            record.get('id')
                        );
                        var baseRecord = store.materializeRecord(storeKey);

                        if (baseRecord.get('status') & SC.Record.DESTROYED) {
                            builtFormSet.get('built_forms').removeObject(baseRecord);
                        } else {
                            if (!builtFormSet.get('built_forms').contains(baseRecord)) {
                                builtFormSet.get('built_forms').pushObject(baseRecord);
                            }
                        }
                    });
                    // Restore the status.
                    F.store.writeStatus(builtFormSet.get('storeKey'), builtFormSetStatus);
                });

                // Reload the component_percents
                this.containerComponentPercentRefresh(representativeRecord);

                var dbEntityKeys = F.layersForegroundController.filter(
                    function(layer) { return layer.getPath('layer_style.defined_attributes').contains('built_form__id') }
                ).mapProperty('db_entity').mapProperty('key');
                Footprint.mapLayerGroupsController.refreshLayers(dbEntityKeys);

                if (representativeRecord.isUrban) {
                    var flatBuiltForm = F.store.find(F.FlatBuiltForm, baseRecord.get('id'));
                    // If the flat built form is already loaded, reload
                    if (flatBuiltForm) {
                        this.commitConflictingNestedStores([flatBuiltForm]);
                        flatBuiltForm.refresh();
                    }
                    else
                        this.gotoState('loadFlatBuiltFormState');
                }
            },

            containerComponentPercentRefresh: function(record) {
                if (record.hasContainerComponentPercents) {
                    record.get('container_component_percents').forEach(function(containerComponentPercent) {
                        var container = containerComponentPercent.getPath('subclassedContainer');
                        if (container) {
                            container.refresh();
                            // Recursecontainer
                            this.containerComponentPercentRefresh(container);
                        }
                    }, this)
                }
            },
            postSavePublishingFailed: function(context) {

            },

            enterState: function(context) {

                // Used to tell the BuiltFormInfoPane what the current recordType is.
                Footprint.builtFormEditRecordTypeController.set('content', context.get('recordType'));

                // Update the baseRecordType to force more strict matching of post save events
                this.set('baseRecordType', context.get('recordType'));
                //this._store = Footprint.store.get('autonomousStore');
                // Load the nestedStore version of the loadingController's content
                this._content = context.getPath('recordsEditController.content');
                this._context = SC.ArrayController.create({
                    content:context.getPath('recordsEditController.content'),
                    recordType:context.get('recordType'),
                    recordsEditController:context.get('recordsEditController')
                });
                sc_super();

                var crudContext = toArrayController(context, {
                    content:context.getPath('recordsEditController.selection.firstObject'),
                    // Optional. For recordTypes that depend on a controller of a different BuiltForm recordType
                    dependencyContext: context.get('dependencyContext'),
                    // Cycle the nested store to deal with nestedStore + nestedRecord bug
                    cycleNestedStore: YES
                });

                // Call doCloneRecord, doCreateRecord, etc.
                Footprint.statechart.sendAction(
                    'do%@Record'.fmt((context.get('crudType') || 'view').capitalize()),
                    crudContext);
            },
            exitState: function() {
                this._store = null;
                this.set('baseRecordType', Footprint.BuiltForm);
                sc_super();
            }
        })
    }),

    doVisualize: function() {
        this.gotoState(this.loadFlatBuiltFormState);
    },

    /***
     * Used to load the FlatBuiltForm data of the selected BuiltForm
     */
    loadFlatBuiltFormState: SC.State.extend({

        initialSubstate: 'initialLoadState',

        initialLoadState: SC.State.extend({
            enterState: function(context){
                Footprint.statechart.sendEvent('builtFormDidChange', SC.Object.create({
                        content : Footprint.urbanBuiltFormCategoriesTreeController.getPath('selection.firstObject')
                    })
                )
            }
        }),

        // LoadingState when the Footprint.builtFormActiveController is not ready
        loadingFlatBuiltFormState: Footprint.LoadingState.extend({

            doClose: function() {
                this.gotoState(this.getPath('parentState.parentState'));
            },

            enterState: function() {
                sc_super();
                this._createdInfoPane = Footprint.VisualizePane.create();
                this._createdInfoPane.append();
            },
            exitState: function() {
                this._createdInfoPane.remove();
                this._createdInfoPane = null;
            },

            recordType:Footprint.FlatBuiltForm,
            didLoadEvent: 'didLoadFlatBuiltForm',
            loadingController: Footprint.flatBuiltFormsController,
            recordArray:function() {
                return Footprint.store.find(
                    SC.Query.create({
                        recordType: this.get('recordType'),
                        location:SC.Query.REMOTE,
                        parameters:{
                            built_form_id: this._context.getPath('content.id')
                        }
                    })
                );
            },
            didLoadFlatBuiltForm:function() {
            }
        }),

        builtFormDidChange: function(context) {
            this.gotoState('loadingFlatBuiltFormState', context);
        }
    })
});
