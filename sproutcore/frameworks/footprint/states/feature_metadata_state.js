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
 * Loads Feature MetaData of DbEntities as requested
 * @type {Class}
 */
Footprint.FeatureMetadataState = SC.State.design({

    dbEntitiesDidBecomeReady: function () {
        this.gotoState(this.readyToLoadFeatureMetadataState)
    },
    dbEntitiesDidBecomeNotReady: function () {
        this.gotoState(this.notReadyState)
    },

    initialSubstate: 'notReadyState',

    notReadyState: SC.State,

    readyToLoadFeatureMetadataState: SC.State.extend({

        initialSubstate: 'readyState',
        readyState: SC.State,

        /***
         * Load the TemplateFeature when editing the DbEntity.
         * The edit DbEntity is always updated then the active one updates but not the other way around
         */
        dbEntityEditDidChange: function () {
            if (!Footprint.dbEntityEditController.get('no_feature_class_configuration'))
                this.gotoState('loadingTemplateFeatureDependenciesState');
            else {
                // Clear the FeatureTemplate controller
                Footprint.templateFeaturesController.set('content', null);
            }
        },

        /***
         * Called when the LayerSelection joins change in order to load the TemplateFeatures
         * of the joined DbEntities. Currently we just expect one DbEntity at a time
         */
        joinDbEntitiesDidChange: function () {
            this.invokeNext(function () {
                if (Footprint.joinedDbEntityActiveController.get('content') && !Footprint.joinedDbEntityActiveController.get('no_feature_class_configuration')) {
                    // Goto the loadingTemplateFeatureDependenciesState using the joinTemplateFeatureContext.
                    // This context makes sure that the data is not loaded into the default controllers
                    this.gotoState(
                        'loadingTemplateFeatureDependenciesState',
                        this.getPath('joinTemplateFeatureContext'));
                }
                else {
                    // Clear the FeatureTemplate controller
                    Footprint.joinedTemplateFeaturesController.set('content', null);
                }
            }, this);
        }, /***

         /***
         * Loads the FeatureAttribute of that attribute that was typed in a query string.
         * Currently this just tries to load a Footprint.FeatureCategoryAttribute but it
         * will be expanded to detect the appropriate type and optionally load
         * a Footprint.FeatureQuantitativeAttribute instead
         * @param context
         */
        doLoadQueryFeatureAttribute: function (context) {
            this.gotoState('loadingQueryFeatureAttributeState', context);
        },
        /***
         * Clears that controller because a valid DbEntity and attribute no longer exist
         * @param context
         */
        doClearQueryFeatureAttribute: function (context) {
            Footprint.queryFeatureAttributesController.set('content', null);
        },
        queryFeatureAttributeDidLoad: function (loadingController) {
        },


        /***
         * The default context for loading TemplateFeatures. This is used whenever a DbEntity
         * is selected in the main app or in the data manager
         */
        defaultTemplateFeatureContext: {
            dbEntityController: Footprint.dbEntityEditController,
            templateFeaturesController: Footprint.templateFeaturesController,
            primaryDbEntitiesController: Footprint.primaryDbEntitiesEditController,
            primaryDbEntityTemplateFeaturesController: Footprint.primaryDbEntityTemplateFeaturesController,
            fileDatasetController: Footprint.fileDatasetEditController
        },
        /***
         * This context is used for loading the TemplateFeatures of join tables
         * We don't currently need the primary DbEntities TemplateFeatures so we leave it out
         */
        joinTemplateFeatureContext: {
            // Load from this controller which contains the joined DbEntities
            dbEntityController: Footprint.joinedDbEntitiesController,
            // Fill this controller
            templateFeaturesController: Footprint.joinedTemplateFeaturesController
        },

        /***
         * This context is used for loading the TemplateFeatures
         * of the the active query DbEntity, which is currently the last db_entity in the filter
         * or aggregate query_string
         * We don't currently need the primary DbEntities TemplateFeatures so we leave it out
         */
        activeQueryTemplateFeatureContext: {
            // Load from this controller which contains the joined DbEntities
            dbEntityController: Footprint.activeQueryDbEntitiesController,
            // Fill this controller
            templateFeaturesController: Footprint.activeQueryTemplateFeaturesController
        },

        /***
         * Concurrently loads the TemplateFeature for the selected DbEntity as well as those of the
         * primary DbEntities that it associates to
         */
        loadingTemplateFeatureDependenciesState: SC.State.plugin('Footprint.LoadingConcurrentDependenciesState', {

            // The source of the primary DbEntities
            primaryDbEntitiesController: null,
            // The DbEntity for which we want to load TemplateFeature
            dbEntityController: null,
            // This controller is loaded with the TemplateFeatures of the Primary DbEntities
            primaryDbEntityTemplateFeaturesController: null,
            // This controller is loaded with the template feature of the selected DbEntity (could be multiple in the future)
            templateFeaturesController: null,
            // The Footprint.FileDataset controller. Only relevant when processing uploads
            fileDatasetController: null,

            enterState: function (context) {
                // Initialize all the source and loading controllers
                context = context || this.getPath('parentState.defaultTemplateFeatureContext');
                ['primaryDbEntitiesController', 'dbEntityController', 'primaryDbEntityTemplateFeaturesController',
                    'templateFeaturesController', 'fileDatasetController'].forEach(function (attr) {
                    this.set(attr, context[attr]);
                }, this);
                sc_super();
            },

            didLoadConcurrentDependencies: function (context) {
                this.invokeNext(function () {
                    this.get('statechart').sendEvent('featureTemplateDependenciesDidLoad', context);
                });
            },

            /***
             * Loads the FeatureTemplate of all PrimaryGeographies at or above the Scenario that aren't already loaded
             */
            loadPrimaryGeographyTemplateFeaturesState: SC.State.plugin('Footprint.LoadingTemplateFeatureState', {
                // Since this potential returns multiple queries, we want to check
                // the status of each query to indicate completeness of loading
                checkRecordStatuses: YES,
                combineMultipleQueryResults: YES,
                loadingController: function () {
                    return this.getPath('parentState.primaryDbEntityTemplateFeaturesController');
                }.property(),

                /***
                 * Set the context as the primaryDbEntitiesController so
                 * that we load multiple template Features
                 * @param context
                 */
                enterState: function (context) {
                    var primaryDbEntitiesController = this.getPath('parentState.primaryDbEntitiesController');
                    // The only time we'd have an empty controller is for new DbEntities that haven't
                    // set their geography scope in their FeatureClassConfiguration, so we don't
                    // know what the primary geography DbEntity is
                    if (primaryDbEntitiesController && primaryDbEntitiesController.getPath('content.length'))
                        sc_super([primaryDbEntitiesController])
                    // Otherwise don't participate in the concurrent load
                },

                /***
                 * Only call parent exitState if we called parent enterState
                 * @param context
                 */
                exitState: function (context) {
                    if (this._context)
                        sc_super()
                }
            }),

            /***
             * Load the template Feature of the current DbEntity if it isn't already in the Store
             * This will never have any content to load if loadingProvisionalTemplateFeaturesState does
             */
            loadingTemplateFeatureState: SC.State.plugin('Footprint.LoadingTemplateFeatureState', {
                loadingController: function () {
                    return this.getPath('parentState.templateFeaturesController');
                }.property(),

                /***
                 * Set the context as the dbEntityEditController
                 * @param context
                 */
                enterState: function (context) {
                    // Only set content if it's an existing DbEntity. Otherwise do nothing and
                    // wait for the other state to set Footprint.templateFeaturesController
                    var dbEntityController = this.getPath('parentState.dbEntityController');
                    // TODO just load the first DbEntity's TemplateFeature for now
                    // we can handle more later
                    var dbEntity = dbEntityController.getPath('content.isEnumerable') ?
                        dbEntityController.getPath('content.firstObject') :
                        dbEntityController.getPath('content');
                    if (dbEntity.get('id') > 0) {
                        sc_super([SC.Object.create({content: dbEntity})]);
                    }
                    // Otherwise don't participate in the concurrent load
                },

                /***
                 * Only call parent exitState if we called parent enterState
                 * @param context
                 */
                exitState: function (context) {
                    if (this._context)
                        sc_super()
                }
            }),

            /***
             * Load the TemplateFeatures of the newly uploaded file or Argis entry
             * The TemplateFeatures return with the schema of the Feature Table.
             * This will never have any content to load if loadingTemplateFeaturesState does
             */
            loadingProvisionalTemplateFeaturesState: SC.State.plugin('Footprint.LoadingTemplateFeatureState', {
                loadingController: Footprint.templateFeaturesController,

                /***
                 * Set the context as the FileDatasetController
                 * @param context
                 */
                enterState: function (context) {
                    // Only set content if it's a new DbEntity. Otherwise do nothing and
                    // wait for the other state to set Footprint.templateFeaturesController
                    var dbEntityController = this.getPath('parentState.dbEntityController');
                    var fileDatasetController = this.getPath('parentState.fileDatasetController');
                    if (dbEntityController.getPath('content.id') <= 0) {
                        sc_super([SC.Object.create({content: fileDatasetController.get('content')})]);
                    }
                    // Otherwise don't participate in the concurrent load
                },

                /***
                 * Only call parent exitState if we called parent enterState
                 * @param context
                 */
                exitState: function (context) {
                    if (this._context)
                        sc_super()
                },

                /***
                 * Queries for TemplateFeatures that are already in the store.
                 * @param records
                 * @returns {{conditions: string, records: *}}
                 */
                localQueryDict: function (records) {
                    return {
                        conditions: '{records} CONTAINS file_source',
                        records: records
                    };
                },

                /***
                 * The parameters to fetch one TemplateFeature
                 * for unsaved DbEntities. We use a Footprint.FileDatset id representing the
                 * dataset of the new DbEntity
                 * @param record
                 * @returns
                 */
                remoteQueryDict: function (record) {
                    return {file_dataset__id: record.get('id')};
                },

                /***
                 * Returns the records whose TemplateFeatures aren't yet loaded
                 * @param records
                 * @param localTemplateFeatures
                 * @returns {*}
                 */
                nonLocalRecords: function (records, localTemplateFeatures) {
                    return records.filter(function (fileDataset) {
                        return !localTemplateFeatures.mapProperty('file_dataset').contains(fileDataset);
                    });
                }
            })
        }),


        /***
         * Load a FeatureAttribute for the query interface
         */
        loadingQueryFeatureAttributeState: SC.State.plugin('Footprint.LoadingFeatureAttributeState', {
            loadingController: Footprint.queryFeatureAttributesController,
            recordType: Footprint.FeatureCategoryAttribute,
            // Once loaded, configure the StyleAttribute based on its subclass
            didLoadEvent: 'queryFeatureAttributeDidLoad'
        })
    })
})
