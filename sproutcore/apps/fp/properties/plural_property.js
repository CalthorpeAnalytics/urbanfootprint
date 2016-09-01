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
 * Displays the single value if a single value is shared among propKey property value of the 'content' items
 * If all resolved values are the same, the value is returned. Otherwise null is returned
 * If value is passed, the property value of all items is set to value
 * @type {Function}
 */
Footprint.pluralProperty = function(propKey, value) {
    var content = this.get('content');
    if (!content || !(this.getPath('contentStatus') & SC.Record.READY))
        return;

    if (value !== undefined) {
        // Setter
        content.forEach(function(item) {
            // Set all items' property to the value
            item.set(propKey, value)
        })
    }
    // Getter
    // For multiple items return null unless all have the same property value
    return content.mapProperty(propKey).uniq().length==1 ? content.firstObject().get(propKey) : null;
}.property('contentStatus', 'content');

/***
 * The function used by the Footprint.pluralContentValuePropertyCreator property
 * @param propKey: The attribute to which the computed property is assigned. Not used.
 * @param value: If defined, the value to set all contentValueKey values
 * @param contentKey: An array attribute of the view to which the property belongs. This could be 'content' or something
 * else in the case that using content would conflict. This is especially true for Footprint.LabelSelectView
 * where the content represents the plural objects whose key we are reading/editing, so we need to use something else.
 * @param contentStatusKey: The status of the array represented by contentKey. We check this is ready and otherwise
 * return immediately
 * @param contentValueKey: The property of each item of the array pointed to by contentKey. We check that all these
 * resolved values are the same and if so we return the unique value, otherwise null. When setting all items
 * of the array have this property updated. If not set this defaults to this.get('contentValueKey')
 * @returns Returns the unique value if there is one. Returns null if contentValueKey values are not all unique.
 * @private
 */
Footprint._pluralContentValueProperty = function pluralContentValueProperty(propKey, value, contentKey, contentStatusKey, contentValueKey) {
    contentValueKey = contentValueKey || this.get('contentValueKey');
    // Gets all available values from the content
    var content = this.get(contentKey);
    if (!content || !(this.getPath(contentStatusKey) & SC.Record.READY)) {
        return;
    }

    if (value !== undefined) {
        // Setter
        // Update each item to value
        content.forEach(function(item) {
            item.set(contentValueKey, value)
        })
    }

    // Getter
    // For multiple items return null unless all have the same property value
    return (content.mapProperty(contentValueKey).uniq().length==1) ?
        content.firstObject().get(contentValueKey) :
        null;
};

/***
 * Dynamically creates a computed property. See _pluralContentValueProperty for details about the function created.
 * The plural property observes a list of values pointed to by contentKey, where contentKey is a key of the
 * view to which we've affixed this property. It also observes contentStatusKey, which is a property of the view
 * that tracks the status of the list pointed to by contentKey. contentValueKey is the key of each item of
 * the list that we want to read/update. The computed property returns null unless all values of contentValueKey
 * are the same, in which case it returns that value. If the computed property is set, all values of contentValueKey
 * are updated to the given value.
 * @param contentKey
 * @param contentStatusKey
 * @param contentValueKey
 * @param refreshValue
 * @returns {*|Function}
 */
Footprint.pluralContentValuePropertyCreator = function(contentKey, contentStatusKey, contentValueKey, refreshValue) {
    var result = function(propKey, value) {
        return Footprint._pluralContentValueProperty.apply(this, [propKey, value, contentKey, contentStatusKey, contentValueKey]);
    }.property(contentStatusKey, contentKey, refreshValue).cacheable();
    return result
};

/***
 * Creates a simple computed plural property for a view that has a content, contentStatus, and refreshValue property
 * content is the array of items to observe
 * contentStatus is the status of that array
 * refreshValue is a property used to tell the computed property to recompute. It can be left null put then
 * triggered with propertyDidChange. You must define refreshValue to null even if you don't need it, since
 * computed properties can't observe undefined properties
 * See _pluralContentValueProperty for its required properties, which specified what property of the list items is
 * being read/updated
 * @type {*|Function}
 */
Footprint.pluralContentValueProperty = function(propKey, value) {
    return Footprint._pluralContentValueProperty.apply(
        this, [propKey, value, 'content', 'contentStatus']);
}.property('contentStatus', 'content', 'refreshValue').cacheable();


/***
 * Displays the range shared among the propKey property values of the content items
 * Assumes the propKey is the name of the content's attribute that we are interested in display in the form attribute__range
 * TODO make the content and property properties function arguments
 * @type {Function}
 */
Footprint.pluralRangeProperty = function(propKey, value) {
    var property = propKey.split('__')[0];
    var content = this.get('content');
    if (!content || !(this.get('contentStatus') & SC.Record.READY))
        return;

    // Getter
    // For multiple items return the range unless only 1 value exists
    return content.mapProperty(property).uniq().length==1 ? null : 'range %@-%@'.fmt(content.mapProperty(property).min(), content.mapProperty(property).max());
}.property('contentStatus', 'content');
