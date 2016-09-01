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


sc_require('data_sources/server_api_caller');

Footprint.Request = SC.Request.extend({
    patchUrl: function(address, body) {
        var req = this.create().set('address', address).set('type', 'PATCH');
        if(body) { req.set('body', body) ; }
        return req ;
    },
});

Footprint.ServerApiCaller = SC.Object.extend({
    viewModel: null,
    protectedViewModel: null,
    uriOptions: null,

    uri: function() {
        return '%@?%@'.fmt(
            this.get('uriPath'),
            $.map(this.get('uriOptions'),
                function(value, key) {
                    return '%@=%@'.fmt(key, value);
                }
            ).join('&'));
    }.property('uriPath', 'uriOptions').cacheable(),

    /***
     * Clones the existing ServerApiCaller with the given parameters updated.
     * This is used by the SparseArray for changing the offset and limit parameters
     * @param uriOptions: key values to replace the existing uriOptions of matching keys.
     */
    clone: function(uriOptions) {
        return this.constructor.create({
            uriPath:this.get('uriPath'),
            uriOptions: $.extend({}, this.get('uriOptions'), uriOptions)
        })
    },

    /***
     * Creates the viewModel instance according to the structure of the JSON data
     */
    load: function(datasource, success, notificationData) {
        Footprint.Request.getUrl(this.get('uri'))
            .set('isJSON', YES)
            .notify(datasource, success, notificationData)
            .send();
    },

    create: function(datasource, success, data) {
        // We always PATCH instead of POST so that we can support multiple objects
        // Tastypie post_list doesn't seem to actually process more than on object
        this.write(Footprint.Request.postUrl, 'PATCH', 'postUrl', datasource, success, data);
    },

    update: function(datasource, success, data, method) {
        this.write(Footprint.Request.patchUrl, method || 'PATCH', 'patchUrl', datasource, success, data);
    },

    write: function(func, method, call, datasource, success, data) {
        var storeKeys = data.storeKeys || [data.storeKey];
        // Look up the request function name ('postUrl', 'patchUrl', etc.)
        // Footprint.Request extends SC.Request to implement patchUrl
        // We accept a recordType or recordType name here
        var recordType = resolveObjectForPropertyPath(data['recordType']);
        Footprint.Request[call](this.get('uri')).header($.extend({
            'Accept': 'application/json'},
            YES || method=='PATCH' ? {'X-HTTP-Method-Override': method} : {}
            )).json()
            .notify(datasource, success, data)
            .send({
                objects: storeKeys.map(function(storeKey) {
                    // Get the dataHash for the storeKey, performing any recordType specific preprocessing
                    var dataHash = this._processDataHash(data.store.readDataHash(storeKey), recordType, data.store.materializeRecord(storeKey));
                    // Get the parent store data hash so that we only send values that have actually changed
                    // Don't create an originalDataHash for LayerSelection. We want to always submit all its attributes for now
                    var originalDataHash = data.store.parentStore && ![Footprint.LayerSelection].contains(recordType) ?
                        this._processDataHash(data.store.parentStore.readDataHash(storeKey), recordType) :
                        null;

                    return datasource._transformSproutcoreJsonToTastypie(data.store, dataHash, originalDataHash, recordType);
                }, this)
            });
    },

    _processDataHash: function(dataHash, recordType, record) {
        return recordType.processDataHash(dataHash, record);
    },

    // TODO ALL BELOW
    saveAsDraft: function(success) {
        var saveDraftUri = '%@%@'.fmt('/draft/save', uriPath);
        $.ajax(
            saveDraftUri, {
                type:'POST',
                contentType:'application/json',
                data:JSON.stringify($.merge({}, {draft:true},this.unmap())),
                success:success,
                error:function(jqXHR, textStatus, errorThrown) {}
            }
        );
    },

    revertToCurrent: function(success) {
        // TODO this could discard the draft on the server
        this.update(success)
    },
    recoverDraft: function(success) {
        var loadDraftUri = '%@%@'.fmt('/draft/load', uriPath);
        this._ajax(loadDraftUri, function(data) {
            this.update(data);
            success(data);
        });
    },
    getRevisions: function(success) {
        var loadDraftUri = '%@%@'.fmt('/draft/load', uriPath);
        this._ajax(loadDraftUri, function(data) {
            _update(data);
        });
    },

    revertToRevision: function(success) {
        var loadDraftUri = '%@%@'.fmt('/draft/load', uriPath);
        this._ajax(loadDraftUri, function(data) {
            _update(data);
        });
    },

    _ajax: function(uri, success) {
        $.getJSON(uri, success);
    }
});

// created for first time sproutcore login in order to prevent a get request to the server with email and password info
// this bypasses tastypie
Footprint.LoginApiCaller = SC.Object.extend({
    // this function does a direct post request to the server and gets back a response that matches the format tastypie
    // would have returned
    load: function(datasource, success, notificationData) {
        var uriPath = '/footprint/login/?output=json';
        var parameters = this.get('parameters'); // {email: email, password: password}
        $.ajax({
            url: uriPath,
            type: 'post',
            data: parameters,
            dataType: 'json',
            success: function(userResult){
                success.call(datasource, SC.Object.create({body: userResult}), notificationData);
            },
            error: function(userResult){
                success.call(datasource, SC.Object.create({body: null}), notificationData);
            },
        });
    },
});
