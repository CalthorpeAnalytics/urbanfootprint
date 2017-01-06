/*
 * UrbanFootprint v1.5
 * Copyright (C) 2017 Calthorpe Analytics
 *
 * This file is part of UrbanFootprint version 1.5
 *
 * UrbanFootprint is distributed under the terms of the GNU General
 * Public License version 3, as published by the Free Software Foundation. This
 * code is distributed WITHOUT ANY WARRANTY, without implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 * Public License v3 for more details; see <http://www.gnu.org/licenses/>.
 */

/* global logProperty */

sc_require('data_sources/server_api_caller');
sc_require('data_sources/data_source_mixin');

Footprint.DataSource = SC.DataSource.extend(Footprint.DataSourceMixin, {

    init: function() {
        this._storeKeysToRetrieve = [];
        this._storeForRetrieve = null;
        sc_super();
    },

    fetch: function(store, query, retry) {

        if (!query.get('isRemote')) {
            // Return local queries as handled without doing anything. We always assume that the data needed by a local
            // query was already fetched by a remote query.
            store.dataSourceDidFetchQuery(query);
            return YES;
        }
        var recordType = query.recordType;

        // For some reason the generic SC.Record type is sometimes fetched. We obviously can't handle it here
        if (recordType == Footprint.Record) {
            Footprint.logError('Received a Footprint.Record record type. This should never happen');
            return NO;
        }

        // If we are doing a set GET but have no ids, don't query
        if (query.parameters && query.parameters.ids && query.parameters.ids.length == 0) {
            Footprint.logError('Received an ids parameters with no ids. This probably shouldn\'t happen.');
            store.dataSourceDidFetchQuery(query);
            return YES;
        }

        // Use the recordType and parameters to form the API call
        var apiCaller = this.recordTypeToApiCaller(recordType, query.parameters);
        if (apiCaller) {
            // If we have a Feature request without ids to limit the results reasonably
            if (recordType.kindOf(Footprint.Feature)
                && !recordType.kindOf(Footprint.TemplateFeature)
                && !recordType.kindOf(Footprint.FeatureCategoryAttribute)
                && !recordType.kindOf(Footprint.FeatureQuantitativeAttribute)
                && (!(query.parameters.ids || query.parameters.id))) {
                // Features are loaded into an SC.SparseArray, so they don't need to all load at once
                // No _didFetch is wired up. Instead a delegate handles requests for more records
                // as needed, which in turn calls _didFetch

                var sparseArray = SC.SparseArray.create({
                    delegate: Footprint.SparseArrayDelegate.create({
                        dataSource: this,
                        apiCaller: apiCaller,
                    }),
                    rangeWindowSize: Footprint.DataSource.MAX_SPARSE_REQUEST_SIZE,
                    store: store,
                    query: query
                });
                // SparseArray has no status management, so we do it manually
                // Initially the sparseArray is BUSY_LOADING. This will
                // change to a READY_CLEAN or one of the SparseArray alternative READY states afterward
                sparseArray.set('status', SC.Record.BUSY_LOADING);
                logProperty(sparseArray.get('status'), 'Sparse Array busy adding');
                store.dataSourceDidFetchQuery(
                    query,
                    sparseArray
                );
            }
            else {
                apiCaller.load(
                    this,
                    this._didFetch,
                    { query: query, store: store, recordType: recordType, retry: Footprint.DataSource.RETRY_COUNT }
                );
            }
        }
        // For now if no handler exists, it means we have an internal Sproutcore record type
        return YES;
    },


    _didFetch: function(response, params) {
        var store = params.store;
        var query = params.query;
        var recordType = params.recordType;
        // Only used for SparseArray fetches
        var sparseArray = params.array;

        var storeKeys;
        // NOTE: If we get a response that's 200 OK but has a string response body, we're assuming
        // that it's this odd edge case where selecting too many parcels bombs out the server but
        // returns a 200.
        if (SC.$ok(response) && SC.typeOf(response.get('body')) === SC.T_HASH && !response.get('not_found')) {
            if (response.get('body')['objects']) {
                // If the API returned a list there will be an 'objects' property containing all the object
                var self = this;
                var objs = $.map(response.get('body')['objects'], function(obj) {
                    return self._transformTastypieJsonToSproutcore(obj, recordType);
                });
                storeKeys = store.loadRecords(recordType, objs);
                if (sparseArray) {
                    var meta = response.get('body')['meta'];
                    // These three methods must be called to sync the SparseArray to what has loaded
                    sparseArray._providingLength = YES; // Prevent a duplicate call
                    sparseArray.provideLength(meta['total_count']);
                    sparseArray._providingLength = NO;
                    sparseArray.provideObjectsInRange({ start: meta['offset'], length: meta['limit'] }, storeKeys);
                    sparseArray.rangeRequestCompleted(meta['offset']);
                    // SparseArray has no status management, so we do it manually
                    // If the SparseArray status indicates that it is incrementally loading everything
                    // and it's not yet finished
                    if ((sparseArray.get('status') & SC.Record.READY_SPARSE_ARRAY_CONTINUOUS) == SC.Record.READY_SPARSE_ARRAY_CONTINUOUS) {
                        // This status is just to trigger observers that need to respond to incremental change
                        sparseArray.set('status', SC.Record.READY_SPARSE_ARRAY_CONTINUOUS_DID_ADD);
                        logProperty(sparseArray.get('status'), 'Sparse Array continuous loading did add');
                        if (sparseArray.get('isCompletelyLoaded')) {
                            // We're now done
                            sparseArray.set('status', SC.Record.READY_CLEAN);
                            logProperty(sparseArray.get('status'), 'Sparse Array continuous loading did complete');
                            // Tell the statechart that the array completely loaded.
                            // This is used when updating features
                            Footprint.statechart.sendEvent('sparseArrayDidComplete', sparseArray);
                        }
                        else {
                            // Still more to load
                            sparseArray.loadNext();
                        }
                    }
                    else {
                        // If incremental loading is complete or not happening, set the status to READY_CLEAN
                        sparseArray.set('status', SC.Record.READY_CLEAN);
                        logProperty(sparseArray.get('status'), 'Sparse Array Incremental loading complete or not occurring');
                    }
                }
            }
            else {
                // Otherwise return the single result as a list (loadRecord might work here instead)
                var obj = this._transformTastypieJsonToSproutcore(response.get('body'), recordType);
                storeKeys = [store.loadRecord(recordType, obj)];
            }
            // The SC.SparseArray holds the storeKeys if it exists
            store.dataSourceDidFetchQuery(query, sparseArray || storeKeys);
        }
        else {
            // handle special weird error case where nginx returns a 200 OK with an error message in
            // the body.
            if (SC.$ok(response) && SC.typeOf(response.get('body')) !== SC.T_HASH)
                store.dataSourceDidErrorQuery(query, response); //same as below for now - may require special handling later
            // handle error case where we want to retry
            // TODO: This needs to be smarter about infinite-loop retrying certain things (e.g. 500
            // server errors).
            else if (!params.retry)
                this.fetch(store, query, Footprint.DataSource.RETRY_COUNT);
            // handle regular error case
            else
                if (sparseArray) {
                    // SparseArray has no status management, so we do it manually
                    sparseArray.set('status', SC.Record.ERROR);
                    Footprint.logError('Sparse Array error');
                }
            store.dataSourceDidErrorQuery(query, response);
        }

        return YES;
    },

    /***
     * Transform the Tastypie model object to a Sproutcore formatted one, which for now just means using an id for related items instead of a uri
     * @param obj
     * @param recordType: Optional recordType to inform transformation
     * @return {*}
     * @private
     */
    _transformTastypieJsonToSproutcore: function(obj, recordType) {
        return this._transform(this._deurlify, obj, null, null, recordType);
    },

    _transform: function(func, obj, parent, key, recordType) {
        var self = this;
        if (typeof obj === 'object') {
            if (obj instanceof Array) {
                return obj.map(function(value) {
                    return self._transform(func, value, parent, key, recordType);
                });
            }
            else {
                return obj &&
                    // Certain recordTypes have child dictionaries that transformed to SC.Objects.
                    // We don't want to transform the recordType objects themselves, just their keys that are dicts, hence key
                    (key && [].contains(recordType) ?
                        // TODO no such recordTypes exist anymore. Consider removing
                        mapObjectToSCObject(obj, function(childKey, value) {
                            return [childKey, self._transform(func, value, obj, childKey, recordType)];
                        }) :
                        $.mapObjectToObject(obj, function(childKey, value) {
                            // Get the relatedRecordType with which to recurse for related types
                            // If the attribute coming from the API is not modeled by the recordType,
                            // simply pass the parent recordType to the _transform
                            var recordAttribute = recordType.prototype[childKey];
                            var recordTypeOrRelatedRecordType = recordAttribute && recordAttribute.instanceOf &&
                                (recordAttribute.instanceOf(SC.ManyAttribute) ||
                                 recordAttribute.instanceOf(SC.ChildAttribute) || // meaning SingleAttribute
                                 recordAttribute.instanceOf(SC.SingleAttribute)) &&
                                (typeof(recordAttribute.type) == 'string' ?
                                    SC.objectForPropertyPath(recordAttribute.type) :
                                    (recordAttribute.type.kindOf ? recordAttribute.type : null));

                            var result = [
                                childKey,
                                self._transform(func, value, obj, childKey, recordTypeOrRelatedRecordType || recordType)
                            ];
                            // If we have an id result...
                            // If we have a related record cache the resourceUri's API type. We otherwise loose
                            // it when we transform the URL to a simple ID. We occasionally need the type
                            // because SC models only the bae type as the related record type, but the API
                            // needs the subclass type. We may or may not model the subclass type in SC.
                            // This allows us to retrieve the record by its subclass later. SC will then
                            // model it as the subclass if it has the recordType or as the base class if it doesn't
                            // see _didRetrieveRecords
                            if (typeof value === 'string' && value.indexOf('/') === 0) {
                                // If the childKey is resource_uri, we want the recordType which has this
                                // attribute, since the resource_uri represents its id. If we have something
                                // else, we have a non-nested toOne or toMany URI
                                var relatedRecordType = childKey=='resource_uri' ?
                                    recordType:
                                    recordTypeOrRelatedRecordType;
                                // The name from the API
                                var subclassRecordTypeName = 'Footprint.%@'.fmt(value.split('/').reverse()[2].classify());
                                if (recordTypeOrRelatedRecordType &&
                                    relatedRecordType.toString() != subclassRecordTypeName) {
                                    // Cache predicted API type by the key {recordType}_{id}
                                    Footprint.DataSource._serverTypeLookup[
                                        '%@_%@'.fmt(relatedRecordType.toString(), result[1])
                                    ] = subclassRecordTypeName;
                                }
                            }
                            return result;
                        }));
            }
        }
        else {
            return func.apply(this, [obj, parent, key]);
        }
    },
    /**
     Transforms the association fields from Resource URI django-tastypie format to the Sproutcore related id format
     */
    _deurlify: function(value, parent, key) {
        if (typeof value === 'string' && value.indexOf('/') === 0) {
            return this._convertUrlToId(value);
        }
        else
            return value;
    },
    _convertUrlToId: function(value) {
        return parseInt(value.split('/').reverse()[1]);
    },

    /***
     * Transform the Sproutcore model object to a Tastypie formatted one, which for now just means using a resource url for related items instead of an id
     * @param obj
     * @return {*}
     * @private
     */
    _transformSproutcoreJsonToTastypie: function(store, obj, originalObj, recordType) {
        var self = this;
        if (!obj) {
            return obj;
        }
        else if (typeof obj === 'object') {
            if (obj.isEnumerable) {
                return obj.map(function(value) {
                    // Extract the attributes from the record if it is a record
                    var dataHash = value.storeKey ? store.readDataHash(value.storeKey) : value;
                    // Get the parent store data hash so that we only send values that have actually changed
                    // TODO we'ere not using originalDataHash right now
                    var originalDataHash = null;
                    //store.parentStore && value && value.storeKey ?
                    //    data.recordType.processDataHash(store.parentStore.readDataHash(value.storeKey)) :
                    //    null;
                    return self._transformSproutcoreJsonToTastypie(store, dataHash, originalDataHash, recordType);
                });
            }
            else {
                var modifiedObject = obj && removeKeys(
                    removeKeysMatchingObject(obj, SC.Object.create()),
                    $.map(obj, function(v,k) { return k[0]==('_') ? k : null; }).compact());

                return obj && $.mapObjectToObject(modifiedObject, function(key, value) {
                    // Change the 'resource_uri' property from an id to a uri. This probably doesn't matter to the API
                    if (key=='resource_uri') {
                        return [key, self._urlify(value, recordType)];
                    }
                    else {
                        // If we can detect that the primitive value has not changed, leave it out of the transformation
                        // This minimizes the data that is sent to the API in a PATCH operation.
                        // TODO we probably need to limit this to PATCHES. POST and PUT probably won't like missing values
                        // TODO This is causing problems on delete, or on corrupt data, so omitting for now
                        //if (value && !value.storeKey && originalObj && value===originalObj[key])
                        //    return null;

                        // Extract the attributes from the record if it is a record
                        var data = value && value.storeKey ? store.readDataHash(value.storeKey) : value;
                        // Get the parent store data hash so that we only send values that have actually changed
                        // TODO we'ere not using originalDataHash right now
                        var originalData = null;
                        //store.parentStore && value && value.storeKey ?
                        //    data.recordType.processDataHash(store.parentStore.readDataHash(value.storeKey)) :
                        //    null;
                        var childRecordType = self._modelClassOfAttribute(recordType, key);
                        return [key, self._transformSproutcoreJsonToTastypie(store, data, originalData, childRecordType)];
                    }
                });
            }
        }
        else {
            // Change the id to a resource uri if a recordType is defined
            return this._urlify(obj, recordType);
        }
    },



    /**
     Transforms the association fields from and id to Resource URI django-tastypie format
     */
    _urlify: function(value, recordType) {
        if (recordType && recordType.apiRecordType) {
            // We might have to map the resource name to a subclass at this point if that's how the value
            // originally came into the datasource
            // Make sure that the apiRecordType is called to get base classes where needed.
            var originalTypeName = Footprint.DataSource._serverTypeLookup['%@_%@'.fmt(recordType.toString(), value)];
            var apiResourceName = this.toApiResourceName(originalTypeName || recordType.apiRecordType());
            var apiVersion = this.getApiVersion(apiResourceName);
            // Detect negative ids, indicating a new record and transform to 0 for tastypie
            return '/footprint/api/%@/%@/%@/'.fmt(apiVersion, apiResourceName, value < 0 ? 0 : value);
        }
        else
            return value;
    },

    /**
     * Since SC.Store calls once on each storeKey, we accumulate and then invoke once at the end of the run loop
     * @param store
     * @param storeKeys
     */
    retrieveRecords: function(store, storeKeys) {

        var recordTypes = storeKeys.map(function(storeKey) {
            return SC.Store.recordTypeFor(storeKey);
        });

        // Never load these 'abstract' classes
        // Whoever is invoking this should be stopped by instead invoking the subclassed version
        if (recordTypes.contains(Footprint.ConfigEntity))
            return NO;

        storeKeys.forEach(function(storeKey) {
            if (store.materializeRecord(storeKey).get('id') < 0) {
                throw "storeKey %@ has a negative id. This indicates that something is trying to retrieve and unsaved record".fmt(storeKey);
            }
            this._storeKeysToRetrieve.push(storeKey);
        }, this);
        // We assume this is always the same store
        this._storeForRetrieve = store;
        this.invokeOnce('_retrieveRecords');
        return YES;
    },

    /**
     * In some cases, we have predicted in advance the type of object that we need to fetch, even
     * if it doesn't exactly match the recordType that the datastore seems to think it should be.
     */
    _resolveTypeFromPredictions: function(recordType, ids) {

        var resolvedTypeName;
        var recordTypeName = recordType.toString();
        ids.forEach(function(id) {
            var typedRecordKey = '%@_%@'.fmt(recordTypeName, id);
            var localTypeName = Footprint.DataSource._serverTypeLookup[typedRecordKey];
            if (localTypeName) {
                if (resolvedTypeName && localTypeName !== resolvedTypeName) {
                    Footprint.logError('not all records in this collection of ' + recordType.toString() +
                                       ' records resolve the same. Some are ' + resolvedTypeName +
                                       ' and some are ' + localTypeName );
                }
                resolvedTypeName = localTypeName;
            }
        });

        if (resolvedTypeName) {
            return SC.objectForPropertyPath(resolvedTypeName);
        }

        return recordType;
    },

    _retrieveRecords: function() {
        var storeKeys = this._storeKeysToRetrieve;
        var store = this._storeForRetrieve;

        var struct = this.recordTypeNameToStoreKeys(storeKeys, store);
        var recordTypeNameToIds = struct['recordTypeNamesToStoreKeys'],
            storeRecordTypeLookup = struct['storeRecordTypeLookup'];

        // now for each recordType, initiate a request
        var ret = null;
        $.each(recordTypeNameToIds, function(recordTypeName, storeKeys) {
            for (var i=0; i<storeKeys.get('length'); i += Footprint.DataSource.MAX_REQUEST_SIZE) {
                var idsSlice = storeKeys.slice(i, i + Footprint.DataSource.MAX_REQUEST_SIZE).map(
                    function(storeKey) { return store.idFor(storeKey); }
                );

                // If this is the first time we're loading these
                // records, then the datastore thinks they're of some base
                // type as determined by the record that triggered the
                // load. But we may know in advance that the record is of a
                // different type.
                var recordType = storeRecordTypeLookup[recordTypeName];
                recordType = this._resolveTypeFromPredictions(recordType, idsSlice);

                var localRet = this.retrieveRecordsOfType(
                  store, recordType, storeRecordTypeLookup[recordTypeName],
                  idsSlice, Footprint.DataSource.RETRY_COUNT);

                // Set SC.MIXED_STATE if we get different YES/NO across types
                if (ret === NO && localRet) {
                    ret = SC.MIXED_STATE;
                } else if (ret === null) {
                    ret = localRet;
                }
            }
        }.bind(this));
        this._storeKeysToRetrieve = [];

        return ret;
    },
    /***
     * Pigeon hole each storeKey's id in the values of the a dict keyed by its resolved recordType name
     * Thus records that came into the system as subclasses are associated with that subclass
     * @param storeKeys
     * @param store
     * @returns {{recordTypeNamesToStoreKeys: *, storeRecordTypeLookup: {}}}.
     * Return the recordTypeName to storeKeys dict as well as a dict mapping the resolved recordType name
     * to the store recordType (e.g. the base class)
     */
    recordTypeNameToStoreKeys: function(storeKeys, store) {
        // convert storeKeys into id’s sorted by recordType.
        var storeRecordTypeLookup = {}; // resolvedRecordType to SC Store's RecordType

        var nameToStoreKeys = $.mapToCollectionsObjectOneFunc(
            storeKeys,
            function (storeKey) {
                var recordType = SC.Store.recordTypeFor(storeKey);
                // map storeKey to ID
                var id = store.idFor(storeKey);
                // If a related record came with a more specific recordType, the type will have been cached.
                // Retrieve the type and use it. It's possible that the type isn't modeled in SproutCore, so
                // we rely on names
                var typedRecordKey = '%@_%@'.fmt(recordType.toString(), id);
                var resolvedRecordTypeName = Footprint.DataSource._serverTypeLookup[typedRecordKey] ||
                                             recordType.toString();
                if (!storeRecordTypeLookup[resolvedRecordTypeName]) {
                    storeRecordTypeLookup[resolvedRecordTypeName] = recordType;
                }
                return [resolvedRecordTypeName, storeKey];
            }
        );
        return {recordTypeNamesToStoreKeys: nameToStoreKeys, storeRecordTypeLookup: storeRecordTypeLookup};
    },

    /***
     * Retrieves all records of a particular type that the API knows about. Sproutcore's knowledge of the record
     * type may be a base type refered to by storeRecordType if Sproutcore doesn't model the subclass explicitly
     * @param store
     * @param recordTypeName
     * @param storeRecordType
     * @param ids
     * @param retry
     * @returns {boolean}
     */
    retrieveRecordsOfType: function(store, recordType, storeRecordType, ids, retry) {
        for (var i=0; i<ids.length; i+=Footprint.DataSource.MAX_SPARSE_REQUEST_SIZE) {
            var slicedIds = ids.slice(i, i+Footprint.DataSource.MAX_SPARSE_REQUEST_SIZE);
            if (slicedIds.length > 0) {
                var apiCaller = this.recordTypeToApiCaller(recordType, {ids: slicedIds}, 'GET');
                // if apiCaller was found - initiate request
                if (apiCaller) {
                    apiCaller.load(
                        this,
                        this._didRetrieveRecords,
                        { store: store, recordType: storeRecordType, ids: slicedIds, retry:retry });
                }
            }
        }
        return YES;
    },

    // Called when a group of records have returns. assume result is array of data hashes
    // Also used for updates and creates that need to update the record/s that was/were saved
    _didRetrieveRecords: function(response, params) {
        var store = params.store,
            recordType = resolveObjectForPropertyPath(params.recordType);

        // normal: load into store...response == dataHash
        if (SC.$ok(response) && !response.get('body')['not_found']) {
            if (!response.get('body')['objects'] || response.get('body')['objects'].length==0) {
                Footprint.logError('Response body has no objects!');
            }
            else {
                // If the API returned a list there will be an 'objects' property containing all the object
                var self = this;
                var objs = response.get('body')['objects'].map(function(obj) {
                    // TODO this shouldn't be needed anymore, just make features a non nested property
                    return self._transformTastypieJsonToSproutcore(obj, recordType);
                });
                if (params.create)
                    params.storeKeys.forEach(function(storeKey, i) {
                        var object = objs[i];
                        if (!(store.peekStatus(storeKey) & SC.Record.BUSY)) {
                            logWarning('id %@ of recordType: %@ is not BUSY!'.fmt(object.id, recordType));
                        }
                        else {
                            store.dataSourceDidComplete(storeKey, object, object.id);
                        }
                    });
                else {
                    // There seems to be a bug where READY_CLEAN records are occasionally retrieved.
                    var busy_objs = [];
                    if (params.ids) {
                        params.ids.forEach(function(id, i) {
                            if (!(store.peekStatus(recordType.storeKeyFor(id)) & SC.Record.BUSY)) {
                                logWarning('id %@ of recordType: %@ is not BUSY!'.fmt(id, recordType));
                            }
                            else {
                                if (objs[i]) {
                                    busy_objs.push(objs[i]);
                                }
                            }
                        });
                    }
                    else {
                        params.storeKeys.forEach(function(storeKey, i) {
                            if (!(store.peekStatus(storeKey) & SC.Record.BUSY)) {
                                logWarning('storeKey %@ of recordType: %@ is not BUSY!'.fmt(storeKey, recordType));
                            }
                            else {
                                if (objs[i]) {
                                    busy_objs.push(objs[i]);
                                }
                            }
                        });
                    }
                    // store.flushFakeChanges(); // Deals with a nested record bug Dave's patch removes the need for this
                    var storeKeys = store.loadRecords(recordType, busy_objs, busy_objs.mapProperty(recordType.prototype.primaryKey));

                    // Attempts to fix buggy nested stores' inability to sync the records that they themselves requested.
                    // This is only a problem when you call retrieveRecords from a nested store record, which delegates to the parentStore
                    // If the parentStore requests directly all the nested stores are correctly updated.
//                    (store.nestedStores || []).forEach(function(nstore) {
//                        nstore.loadRecords(recordType, busy_objs, busy_objs.mapProperty(recordType.prototype.primaryKey));
//                    });

                    storeKeys.forEach(function(storeKey) {
                        if (store.peekStatus(storeKey) !== SC.Record.READY_CLEAN) {
                            logWarning('storeKey %@ of recordType: %@ is not READY_CLEAN!'.fmt(storeKey, recordType));
                        }
                    });
                }
            }
            // error: indicate as such...response == error
            //TODO storeKey expected but this ran on multiple storeKeys
        } else {
            //store.dataSourceDidError(storeKey, response.get('body'));
            if (params.retry && !response.get('body')['not_found']) {
                logWarning('DataSource did error for recordType: %@. Response: %@. Retrying'.fmt(recordType, response.get('body')));
                this.retrieveRecordsOfType(store, recordType, params.ids, params.retry-1);
            }
            else
                Footprint.logError('DataSource did error for recordType: %@. Response: %@'.fmt(recordType, response.get('body')));
        }
    },


    /***
     * Creates a new record.
     * @param store
     * @param storeKey
     * @param uriOnly: Set to YES to return the url without  making the server call. This is
     * for the file upload hack
     * @returns {*}
     */
    createRecord: function(store, storeKey) {

        var recordType = store.recordTypeFor(storeKey);

        if (recordType==Footprint.User) {
            // We don't allow creating users at the moment, and we don't want create to trigger an API call
            store.dataSourceDidComplete(storeKey, null, store.idFor(storeKey));
            return YES;
        }

        // Hack for Scenario type
        // TODO Sproutcore should be able to handle subclasses mixed in a list, but right
        // now our Scenarios are all the base class Footprint.Scenario
        if (recordType==Footprint.Scenario) {
            var scenario = store.materializeRecord(storeKey);
            recordType = scenario.getPath('origin_instance.categories.firstObject.value') == 'Base' ?
                Footprint.BaseScenario : Footprint.FutureScenario;
        }

        // Create is always performed as a PATCH, so convert this to a multi-object request with storeKeys
        this.recordTypeToApiCaller(recordType, {}, 'POST').create(
            this,
            this._didCreate,
            { store: store, storeKeys: [storeKey], recordType: recordType }
        );

        return YES;
    },


    updateRecords: function(store, storeKeys) {

        var struct = this.recordTypeNameToStoreKeys(storeKeys, store),
            recordTypeNameToIds = struct['recordTypeNamesToStoreKeys'],
            storeRecordTypeLookup = struct['storeRecordTypeLookup'];

        // now for each recordType, initiate a request
        var self = this;
        $.each(recordTypeNameToIds, function(recordTypeName, storeKeys) {
            var recordType = storeRecordTypeLookup[recordTypeName];
            var apiCaller = self.recordTypeToApiCaller(
                recordType,
                {config_entity:Footprint.scenarioActiveController.get('content')},
                'PATCH'
            );
            storeKeys.forEach(function(storeKey) {
                var status = store.readStatus(storeKey);
                if (!(status & SC.Record.BUSY)) {
                    Footprint.logError('About to update %@ record that is not BUSY! storeKey: %@, status %@'.fmt(recordTypeName, storeKey, getStatusString(status)));
                }
            }, self);

            apiCaller.update(
                self,
                self._didUpdate,
                { store: store, storeKeys: storeKeys, recordType: recordTypeName }
            );
        });

        return YES;
    },
    updateRecord: function(store, storeKey) {
        var recordType = store.recordTypeFor(storeKey);

        var apiCaller = this.recordTypeToApiCaller(
            recordType,
            {id:store.idFor(storeKey), config_entity:Footprint.scenarioActiveController.get('content')},
            'PATCH');
        apiCaller.update(
            this,
            this._didUpdate,
            { store: store, storeKey: storeKey, recordType: recordType }
        );

        return YES;
    },


    /***
     * Called upon completing the API call to create the record.
     * @param response
     * @param store
     * @param storeKey
     * @private
     */
    _didCreate: function(response, params) {
        this._didSave(response, params, YES);
    },

    _didUpdate: function(response, params) {
        this._didSave(response, params, NO);
    },

    _didSave: function(response, params, create) {
        var recordType = resolveObjectForPropertyPath(params.recordType);
        if (SC.ok(response)) {
            // Check if the store is destroyed by a subsequent update. If so do nothing return YES.
            if (params.store.get('isDestroyed'))
                return YES;

            // Single update cases
            if (params.storeKey) {
                var status = params.store.readStatus(params.storeKey);

                // Some temporary state error handling
                if (!(status & SC.Record.BUSY)) {
                    Footprint.logError('After save %@ record is not BUSY! This should never happen. storeKey: %@, status: %@'.fmt(recordType, params.storeKey, getStatusString(status)));
                }
                else
                    if (create)
                        params.store.dataSourceDidComplete(params.storeKey, response.get('body'), response.getPath('body.id'));
                    else
                        params.store.dataSourceDidComplete(params.storeKey);
            }
            // Multiple save cases
            else {
                // Save that returned a response
                if (response.get('body')['objects'])
                    // Handle Record types that need to return the records upon saving
                    this._didRetrieveRecords(response, $.extend({}, params, {create:create}));
                // Update without a response
                else {
                    params.storeKeys.forEach(function(storeKey) {
                        if (params.store.peekStatus(storeKey) & SC.Record.BUSY) {
                            params.store.dataSourceDidComplete(storeKey);
                        }
                    });
                }
            }
        } else {
            if (params.storeKey) {
                params.store.dataSourceDidError(params.storeKey);
            }
            else {
                params.storeKeys.forEach(function(storeKey) {
                    if (params.store.peekStatus(storeKey) & SC.Record.BUSY)
                        params.store.dataSourceDidError(storeKey, response.get('errorObject'));
                });
            }
        }
    },

    destroyRecord: function(store, storeKey) {
        if (SC.kindOf(store.recordTypeFor(storeKey), Todos.Task)) {
            SC.Request.deleteUrl(store.idFor(storeKey)).header({
                'Accept': 'application/json'
            }).json()
                .notify(this, this.didDestroyTask, store, storeKey)
                .send();
            return YES;

        } else return NO;
    },

    didDestroyTask: function(response, store, storeKey) {
        if (SC.ok(response)) {
            store.dataSourceDidDestroy(storeKey);
        } else store.dataSourceDidError(response);
    },

    /***
     * Resolves the API name of the record based on its type.
     * @param recordType: A RecordType subclass or a string of the name
     * @returns {*}
     */
    toApiResourceName: function(recordType) {
        var recordTypeName =typeof(recordType)=='string' ?
            recordType :
            // Some record types have this attribute so that they send a base class name to the server
            recordType.toString();
        return recordTypeName.toString().split('.')[1].decamelize();
    },

    getApiVersion: function(apiResourceName) {
        return Footprint.DataSource.V2_API_MODELS.indexOf(apiResourceName) > -1 ? 'v2' : 'v1';
    },

    /***
     * Constructs a relative URI for proxying to the Django server
     * TODO set up a non-proxy option for the production environment
     * @param apiModelName
     * @param id
     * @return {*}
     * @private
     */
    _constructUri : function(apiModelName, options) {
        // Append the id as 'id/' or ids in the form: 'set/id1;id2;....' or nothing

        var apiVersion = this.getApiVersion(apiModelName),
            idSegment = options['id'] ?
            '%@/'.fmt(options['id']) :
            (options['ids'] ?
                'set/%@/'.fmt(options['ids'].join(';')):
                null);
        return idSegment ?
            '/footprint/api/%@/%@/%@'.fmt(apiVersion, apiModelName, idSegment) :
            '/footprint/api/%@/%@/'.fmt(apiVersion, apiModelName);
    }
});

/***
 * Class constants to set the maximum number of records to retrieve at once
 * The SparseArrayDelegate has it's own default length
 */
Footprint.DataSource.mixin({
    /***
     * Limits the number or records simultaneously fetched by combining
     * retrieveRecords calls
     */
    MAX_SPARSE_REQUEST_SIZE: 100,

    /**
     * The limit of simultaneous items for retrieveRecords
     */
    MAX_REQUEST_SIZE: 10,

    /***
     * For failed API calls retry this many times before giving up
     */
    RETRY_COUNT: 5,

    /***
     * Classwide cache to keep trak of the original type of an object
     * in case it's subclass type is lost due to the way SC handles
     * related records. Sproutcore only stores the storeKey of the
     * relatedRecords, so we cache it's original type here
     * in the form [recordType_id] = original_type where
     * recordType is the type SC is seekeing, id is the record/object id,
     * and orignal type is in the from 'Footprint.api_endpoint' where
     * the api_endpoint could be a subclass of recordType. The api_endpoint
     * is then used to reform the URL when requesting the related record
     */
    _serverTypeLookup: {},

    // models using v2 of the api
    //V2_API_MODELS: ['project', 'scenario'],
    V2_API_MODELS: ['project'],

    /***
     * Data export currently uses Django views directly without Tastypie
     * So this is a class method until we move export to the API,
     * at which point it will be an API patch
     */
    'export': function(action, record) {
        // For recordTypes that are scoped to a DbEntity or ConfigEntity, use unique_id
        // Otherwise use id
        // It's up to the Django view to parse the id
        var recordId = record.get('unique_id') || record.get('id');
        var userPermissionDict = this.userPermissionDict();
        var request = SC.Request.getUrl('/footprint/%@/%@/%@/'.fmt(
            userPermissionDict['api_key'],
            action,
            recordId));
        request.send();
    },

    /***
     * Returns User permission attributes from the userController to authenticate API calls
     * @returns {{api_key: *, username: *}}
     */
    userPermissionDict: function() {
        return {
            api_key: Footprint.userController.getPath('content.firstObject.api_key'),
            username: Footprint.userController.getPath('content.firstObject.username')
        };
    }
});


Footprint.SparseArrayDelegate = SC.Object.extend({
    dataSource: null,
    apiCaller: null,
    length: Footprint.DataSource.MAX_SPARSE_REQUEST_SIZE,

    // Delegate to load the SC.SparseArray from the server as needed for Feature requests
    sparseArrayDidRequestLength: function(sparseArray) {
        return this.sparseArrayDidRequestRange(sparseArray, { start: 0, length: this.length });
    },

    sparseArrayDidRequestRange: function(sparseArray, range) {
        if (sparseArray._providingLength) // Prevents a duplicate call
            return;

        // Set the status to busy loading if there is nothing yet loaded,
        // otherwise use special statuses to indicate incremental loading
        if ((sparseArray.get('status') & SC.Record.READY_SPARSE_ARRAY_CONTINUOUS) == SC.Record.READY_SPARSE_ARRAY_CONTINUOUS) {
            // Used for continual incremental loading
            sparseArray.set('status', SC.Record.READY_SPARSE_ARRAY_CONTINUOUS_WILL_ADD);
            logProperty(sparseArray.get('status'), 'Sparse Array continuous loading will add');
        }
        else {
            // Indicate adding (non continually) to a sparse array, or if it has no indexes yet
            // tread it as a normal array
            sparseArray.set('status',
                sparseArray.definedIndexes().get('length') ?
                    SC.Record.READY_SPARSE_ARRAY_ADDING :
                    SC.Record.BUSY_LOADING);
            logProperty(sparseArray.get('status'), 'Sparse Array (non-continual) adding');
        }
        var apiCaller = this.apiCaller.clone({offset:range.start, limit: range.length});
        SC.info('sparseArrayDidRequestRange: %@ - %@'.fmt(range.start, range.start + range.length - 1));

        apiCaller.load(
            this.dataSource,
            this.dataSource._didFetch,
            {
                query: sparseArray.query,
                store: sparseArray.store,
                recordType: sparseArray.query.recordType,
                array: sparseArray,
                retry: Footprint.DataSource.RETRY_COUNT
            }
        );
    }
});
