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



sc_require('controllers/controllers');

 /***
  * Reports the attributes of the recordType
  */
Footprint.AttributesController = SC.ArrayController.extend(Footprint.SingleSelectionSupport, {
    recordType: null,
    fields: null,

    /***
     * A template instance of the DbEntity's Feature class which gives us access to the Feature table's fields
     * This is only required if contentAsSchema is YES
     */
    templateFeature: null,
    /***
     * Bind this to the status of the controller loading the templateFeature
     */
    templateFeatureStatus: null,

    /***
     * Bind this to the templateFeatureStatus when needed. Doing it here causes infinite loops
     */
    status: null,

    /**
     * By default the content is simply a list of string fields.
     * Set this to YES to get the contact back as Footprint.Schema instances
     */
    contentAsSchema: NO,

    /***
     * Returns the fields property or allRecordAttributeProperties if there are no explicit fields
     * if contentAsSchema is true, this returns the Footprint.Schema instances for each field,
     * otherwise it just returns the field strings
     *
     */
    content: function() {
        var fields = [];
        if (this.get('fields'))
            fields = this.get('fields');
        else if (this.get('recordType'))
            fields = this.get('recordType').allRecordAttributeProperties();
        return this.get('contentAsSchema') ?
            this.getPath('templateFeature.schemas') || []:
            fields;
    }.property('contentAsSchema', 'templateFeature', 'templateFeatureStatus', 'fields', 'recordType').cacheable()
});
