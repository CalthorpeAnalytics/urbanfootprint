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


Footprint.TableController = Footprint.ArrayController.extend({
    /***
     * The content used by the formattedContent. Override
     * to use nested store content
     */
    //nested Store Version of the content that will be edited or changed by the user
    editContent: null,
    presentationContent: function() {
        return this.get('editContent')
    }.property('editContent').cacheable(),

    /***
     * Maps the loaded content. This is all presentationContent that is loaded via SparseArray
     * @param func: The mapping function, which can expect the mapped item and optionally the index as the second argument
     * @returns {*}
     */
    mapLoadedContent: function(func) {
        // If we are using a SparseArray we only map the loaded records. Otherwise map everything
        // (ChildArray defines mapLoadedRecords but it delegates to map)
        var mapLoadedRecords = this.get('presentationContent').mapLoadedRecords || this.get('presentationContent').map;
        return mapLoadedRecords.apply(this.get('presentationContent') || [], [func, this])
    },

    recordType: null,
    /***
     * Optional override with an SC.Object that maps field values to other values
     */
    mapProperties: null,

    /***
     * The fields of the content. These are mapped to created the columnNameMap
     */
    resultFields: null,

    /***
     * Optional lookup mapping field names to different column names
     */
    resultFieldsTitleLookup: null,

    /***
     * Keeps track of the number of items that the underlying SparseArray has loaded
     * if a sparse array is in use
     */
    loadedCount: null,
    loadedCountBinding: SC.Binding.oneWay('*content.storeKeys.loadedCount'),

    /***
     * This is the content used by the TableDelegate to render each cell.
     * Cells are accessed by rowIndex and then by column.
     * Only content for loaded rows is available here. It's up to the
     * TableDelegate to deal with missing rows by showing a loading status or similar.
     * Note that content property is used by the SCTable overall so that it correctly
     * requests new indexes from the underlying SC.SparseArray. Here we use
     * presentationContent, which might be bound to content or might be bound to
     * something intermediate, like nestedStore content
     */
    formattedContent:function() {
        if (!this.get('presentationContent') || !this.getPath('presentationContent.length') || !(this.getPath('status') & SC.Record.READY) || !this.getPath('resultFields.length'))
            return [];
        // Use the unsorted resultFields, since these correspond
        // exactly with the raw Record attributes
        var fields = this.get('resultFields');
        var mapProperties = this.get('mapProperties') || SC.Object.create();
        // Create an array where the index corresponds to that of the content
        return mapToExplicitIndexArray(
            // Map each loaded record to its index and formatted representation
            this.mapLoadedContent(
                function(item, index) {
                    // Map column values using mapProperties and formatForType
                    return [index, mapToSCObject(
                        fields,
                        function (field) {
                            var path = mapProperties.getPath(field);
                            return [
                                field,
                                // Map the field to a custom path if one is defined in mapProperties
                                // Default to the field lookup if path resolves to null or undefined
                                path && item.getPath(path) || item.get(field)
                            ];
                        },
                        this)];
                }
            ),
            function(indexAndObj) { return indexAndObj });
    }.property('presentationContent', 'loadedCount', 'resultFields', 'mapProperties', 'presentationContentStatus').cacheable(),

    /***
     * Dynamically adds observers to the attributes of the content so that the table cell can be
     * updated when the values are edited elsewhere.
     */
    attributeObserver:function(content, property) {
        // For some reason the content is sometimes null
        if (!content)
            return;
        // when merging develop-scenarios do not merge in the status checking conditional at
        // https://bitbucket.org/calthorpe/urbanfootprint/commits/97185b794771eced5e27bab327870e92eb55c42f#Lsproutcore/frameworks/footprint/controllers/table/table_controllers.jsT101
        (this.get('_attributeObservers') || []).forEach(function(item_path) {
            item_path[0].removeObserver(item_path[1], this, 'attributeDidChange');
        }, this);
        if (this.getPath('presentationContent.length') > 0) {
            var fields = this.get('resolvedFields');
            // Create the observers and cache them
            this.set(
                '_attributeObservers',
                $.shallowFlatten(this.mapLoadedContent(function(item) {
                    return fields.map(function(key) {
                        item.addObserver(key, this, 'attributeDidChange');
                        return [item, key];
                    }, this);
                }))
            );
        }
    // when merging in develop-scenarios do not re-introduce '*editContent.@each.status' observer
    // https://bitbucket.org/calthorpe/urbanfootprint/commits/97185b794771eced5e27bab327870e92eb55c42f#Lsproutcore/frameworks/footprint/controllers/table/table_controllers.jsF112T124
    }.observes('.presentationContent'),

    attributeDidChange: function() {
        this.invokeOnce('contentDidChange');
    },

    contentDidChange: function() {
        this.propertyDidChange('editContent');
    },

    /**
     * The columns in the correct order. These are based on the resultsFields if available
     * and are sorted according to the sortedProperties function.
     */
    resolvedFields: function() {
        if (this.getPath('resultFields.length'))
            return this.get('resultFields');
        else if (this.get('recordType') && this.get('recordType') != Footprint.Feature) {
            var recordType = this.get('recordType');
            return this.get('derivedProperties');
        }
        else if (this.getPath('content.firstObject.attributeKeys'))
            return this.getPath('content.firstObject').attributeKeys();
        else
            return [];
    }.property('recordType', 'resultFields', 'content', 'derivedProperties').cacheable(),

    /***
     * Apply the mapping to the fields if the mapping exists to set the name of the Column instances
     * The valueKey is always the field name
     */
    columns: function () {
        var resultFieldsTitleLookup = this.get('resultFieldsTitleLookup') || {};
        return this.get('resolvedFields').map(function (field) {
            return SC.Object.create(SCTable.Column, {
                name: resultFieldsTitleLookup[field] || field,
                valueKey: field,
                width: 150
            });
        });
    }.property('resolvedFields').cacheable(),

    /***
     * Properties derived from the class attributes when no other column information is provided
     */
    derivedProperties: function() {
        var recordType = this.get('recordType');
        if (!recordType)
            return null;
        return recordType.allRecordAttributeProperties();
    }.property('recordType').cacheable(),

    /***
     * Override to handle SparseArrays
     * @returns {*}
     */
//    toString: function() {
//        return this.toStringAttributes(['content'], {content: function(content) {
//            return this.mapLoadedContent(function(item) {
//                    return item.toString()
//                }, this).join("\n---->");
//        }});
//    }
});
