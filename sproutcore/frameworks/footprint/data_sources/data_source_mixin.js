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


Footprint.DataSourceMixin = {
    /**
     * Returns the child record type for the RecordAttribute that the key represents, if any
     * @param recordType - the recordType that owns the key. If this is null the function returns null
     * @param key - the key of the recordType
     * @returns {*} The record type of the attribute or null
     * @private
     */
    _modelClassOfAttribute: function(recordType, key) {
        if (recordType) {
            var attribute = recordType.prototype[key];
            if (attribute &&
                attribute.kindOf &&
                attribute.kindOf(SC.RecordAttribute)) {

                return (typeof attribute.type == 'string' || attribute.type.kindOf) ? eval(attribute.type) : null;
            }
            else if (recordType.prototype.resolveAttributeType) {
                return recordType.prototype.resolveAttributeType(key);
            }
        }
        else
            return null;
    },

    /***
     * Get the create uri for uploading files.
     * @param store
     * @param storeKey
     * @returns {*}
     */
    uploadUri: function(context) {
        // Strip the api url to make it a django call
        return this.recordTypeToApiCaller(null, {config_entity:context.get('configEntity')}, 'UPLOAD').get('uri');
    },

    /***
     * Creates an ApiCaller instance for the record type and the given options.
     * @param recordType. The SC.RecordType subclass or full nae
     * @param parameters: The options are usually based on the Sproutcore query parameters, but the api call
     * @param method: Optional: 'POST', 'PATCH', 'GET', or 'UPLOAD'. 'UPLOAD' is a pseudomethod that tells
     * the API caller to create the upload URL. For now that means that recordType is ignored for UPLOAD
     * is only interested in certain parameters, which sometimes depend on the recordType
     */
    recordTypeToApiCaller: function(recordType, parameters, method) {
        parameters = parameters || {};
        if (method==='UPLOAD') {
            // Upload doesn't care about the recordType nor ids.
            uriPath = '/footprint/upload/';
            recordType = Footprint.Record;
        }
        // When actually passing in a password, the user must be logging in.
        // Skip tastypie server call and do a direct server post request for the first time through sproutcore login page.
        else if (recordType === Footprint.User && parameters.password) {
            var result = Footprint.LoginApiCaller.create({parameters:parameters});
            return result;
        }
        else {
            // Map the recordType API name to another name, if toApiRecordType doesn't already do the job
            var recordTypeName = recordType.apiRecordType(parameters, method).toString();

            var apiModelName = this.toApiResourceName(recordTypeName);
            var uriPath,
                uriOptions,
                // The id to append to the url for single record queries
                id = parameters && parameters.id && parameters['id'],
                ids = parameters && parameters.ids && parameters['ids'];
            uriPath = this._constructUri(apiModelName, {id:id, ids:ids});
        }

        uriOptions = $.extend(
            {},
            {format:'json'},
            Footprint.userController.get('status') & SC.Record.READY ?
                this.constructor.userPermissionDict() : {},
            // Add the options.
            this._contextParameters(recordType, parameters, method)
        );

        return Footprint.ServerApiCaller.create({uriPath:uriPath, uriOptions:uriOptions});
    },

    /***
     * Adds contextual parameters to resolve dynamic subclasses on the server
     * @param recordType
     * @param parameters
     * @private
     */
    _contextParameters: function(recordType, parameters, method) {
        var recordTypeName = recordType.apiRecordType().toString();
        var modified_parameters = {};
        if (parameters.layer) {
            // Convert any reference to a Footprint.Layer to a layer__id parameter
            modified_parameters['layer__id'] = parameters.layer.get('id');
        }
        else if (parameters.db_entity) {
            // Convert any reference to a Footprint.DbEntity to a db_entity__id parameter
            modified_parameters['db_entity__id'] = parameters.db_entity.get('id');
        }
        else if (['PATCH', 'GET'].contains(method) && ['Footprint.Feature', 'Footprint.LayerSelection'].contains(recordTypeName)) {
            // Hacky, but we the API needs at the moment to resolve the LayerSelection class
            modified_parameters['layer__id'] = Footprint.layerSelectionActiveController.getPath('layer.id');
        }
        else if (['PATCH', 'POST', 'PUT'].contains(method) && ['Footprint.Scenario'].contains(recordTypeName)) {
            // DITTO
            modified_parameters['origin_instance__id'] =
                Footprint.scenariosEditController.getPath('selection.firstObject.origin_instance.id');
        }

        if (parameters.config_entity || parameters.parent_config_entity ||
            (SC.objectForPropertyPath(recordTypeName) || Footprint.Record).kindOf(Footprint.ClientLandUseDefinition)) {
            // Many recordTypes, including Feature subclasses, belong to a ConfigEntity instance. Pass it to the API
            // to filter the results.
            // ClientLandUseDefinition is sometimes requested as a related instance, so we need to
            // give it the active config_entity id
            var config_entity_filtering = null;
            if (parameters.config_entity)
                config_entity_filtering = {config_entity__id: parameters.config_entity.get('id')};
            else if (parameters.parent_config_entity) {
                if (parameters.parent_config_entity.isEnumerable)
                    // If parent_config_entity is an array of instances
                    config_entity_filtering = {parent_config_entity__id__in: parameters.parent_config_entity.mapProperty('id').join(',')};
                else
                    // If parent_config_entity is a single instance
                    config_entity_filtering = {parent_config_entity__id: parameters.parent_config_entity.get('id')};
            }
            else
                // If config_entity is null this is as stopgap measure
                config_entity_filtering = {config_entity__id: Footprint.scenarioActiveController.get('id')};

            $.extend(
                modified_parameters,
                config_entity_filtering);
        }

        if (parameters.layer_selection) {
            // If a layer_selection parameter is passed, send both its id and the layer id, since layer_selection
            // classes are specific to layers
            modified_parameters['layer_selection__id'] = parameters.layer_selection.get('id');
            modified_parameters['layer__id'] = parameters.layer_selection.getPath('layer.id');
        }

        return Object.keys(modified_parameters).length > 0 ?
            merge(modified_parameters, filterKeys(parameters, ['limit'])) :
            parameters;
    }
};
