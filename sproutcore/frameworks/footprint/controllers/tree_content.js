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

sc_require('controllers/tree_observer');

/***
 * Used by the tree controller to create a hierarchy
 * @type {*}
 */
Footprint.TreeItem = SC.Object.extend(SC.TreeItemContent, {
    keyObject:null,
    leaves:null,
    // The property of the keyObject that is its viewable name
    keyNameProperty:null,

    name:function() {
        return (this.get('keyObject').getPath(this.get('keyNameProperty')) || '').titleize();
    }.property('keyNameProperty'),

    treeItemIsExpanded: YES,
    treeItemChildren: function(){
        return this.get('leaves');
    }.property('leaves'),

    toString: function() {
        return '%@:\n%@'.fmt(sc_super(), this.toStringAttributes('keyObject keyNameProperty name'.w()));
    }
});

/**
 * Objectifies the relationship between top level items and second
 * level items (and possibly deeper) The data structure is:
 *
 *     { key_string1: {
 *         key: top_level_instance,
 *         values: second_level_instances
 *       },
 *       key_string2: ...
 * }
 *
 * where key_string1 is a string version of the top_level_instance so
 * that the values can be grouped under a single key.
 */
Footprint.TreeContent = SC.Object.extend(Footprint.SearchFilterMixin, Footprint.TreeObserver, {
    /***
     * The unique key objects used by the the TreeController. These are model instances that have a string property that label the top-level tree nodes
     * The leaves have objects matching keyObjects via their keyProperty. The leaves are shown under any
     * keyObject for which they have a matching object in their keyProperty collection (or single item). Thus
     * it's possible for a leaf to be under two objects if its keyProperty collection has more than 1 item
     * that is in keyObjects. A leaf that matches no keyObjects via its keyProperty collection will be placed
     * under the undefinedKeyObject.
     *
     */
    keyObjects: null,
    keyObjectsStatus:null,
    keyObjectsStatusBinding: SC.Binding.oneWay('*keyObjects.status'),
    /***
    * The property of node that resolves keyObject that matches one of keyObjects. This attribute hold a single
    * item or a collection. The keyProperty, keyProperty status and keyProperty [] (if it's a collection)
    * of each leaf is dynamically observed in case the value or an item in the value's collection changes
    */
    keyProperty:null,
    // For Footprint.TreeObserver call propertyDidChange on our tree property if any dependency changes
    // The SearchFilterMixin will also observe changes to our leaves
    treeProperties: ['tree'],

    treeProperty: 'tree',
    // The property of the nodes that access their name for display
    keyNameProperty:null,

    // Override to a return a function that resolves the leaf to a value for the tree
    // Normally the value of the tree will be the leaf itself
    leafValueLookup: null,

    // The leaves of the tree.
    leaves:null,
    leavesStatus:null,
    leavesStatusBinding:SC.Binding.oneWay('*leaves.status'),

    // Start the tree contracted to prevent SC.TreeItemObserver expandedState being wrong
    // This will become YES upon load of the treeItemChildren. See Footprint.TreeController
    treeItemIsExpanded: NO,

    // The name of the root element
    name: 'root',
    group: true,

    /***
     * When using the search box, filter leaves by their name by default
     */
    filterProperties: ['name'],
    /**
     * Filter the leaves. This means that calling this.get('filteredItems') will return the leaves
     * that are filtered by the search string
    */
    filteredItemsProperties: ['leaves'],

    /***
     * Default sorting properties for the leaf level of tree controller
     */
    sortProperties:['name'],
    /***
     * Dict with key: YES for any sortProperties item that should be reversed
     */
    reverseSortDict: null,
    /***
     * Default sorting properties for the KeyObjects of the tree controller
     */
    sortKeyProperties:[],
    /***
     * Dict with key: YES for any sortKeyProperties item that should be reversed
     */
    keyReverseSortDict: null,

    /***
     * A Default key object to use if no keys are found for a leaf.
     * If not specified unmatched leaves will not appear in the tree
     * This can also return a function that expects a leaf. THat way you can dynamicaly
     * resolve the KeyObject of choice based on the leaf.
     */
    undefinedKeyObject: null,

    // Track changes to membership of leaves
    leavesObserver: function() {
        this.invokeOnce(this._leavesObserver);
    }.observes('*leaves.[]', '*leaves.@each.status'),

    _leavesObserver: function() {
        this.propertyDidChange('tree')
    },

    /***
     * Creates a object whose attributes are the top-level tree key names and values are the leaves with that key.
     * This is used to create TreeItemChildren, the flat version of this data structure that is used by Tree
     * Example
     *  {key_string1: SC.Object(key: KeyObject, value: LeafObject),
     *   key_string2: SC.Object(key: KeyObject, value: LeafObject)}
     */
    tree:function() {
        var self = this;
        var keyObjects = this.get('keyObjects');
        // If the there are no keyObjects, or the leavesStatus is not ready (but not because of busy_creating or busy_committing)
        // then return null. These busy statuses should not impact the display of the tree
        if (!keyObjects || (
            !(this.getPath('leavesStatus') & SC.Record.READY) &&
            !((this.get('leaves') || []).mapProperty('status').filter(function(status) {
                return ![SC.Record.BUSY_CREATING, SC.Record.BUSY_COMMITTING].contains(status);
            }).max() & SC.Record.READY)
        ))
            return null;
        return $.mapToCollectionsObjectWithObjectKeys(
            // Get all the leaves or those matching the filter
            this.get('filteredItems') || [],
            // create keys. These are instances. The 3rd function below creates a hashable key with
            // which to group values since these are objects, which javascript can't hash
            function(leaf) {
                var list = arrayOrItemToArray(leaf.getPath(self.get('keyProperty'))).filter(
                    function(keyObject) {
                        // only accept the key objects that match keyObjects
                        // This allows us to filter out keyObjects of the leaves that we don't care about
                        // For instance, with Scenarios we only care about Category instances whose key property is
                        // 'category'
                        // Use id comparison since we traditionally load the full set as non-nested and the attribute
                        // version as nested. Comparing nested to non-nested records no longer works
                        return keyObjects.mapProperty('id').contains(keyObject.get('id'));
                    }
                );
                // If no keys match we use the undefinedKeyObject. If undefinedKeyObject is a function pass
                // the leaf to it for resolution
                var undefinedObjectOrFunc = self.get('undefinedKeyObject');
                return list.length > 0 ? list : arrayOrItemToArray(
                    typeof(undefinedObjectOrFunc)=='function' ?
                        undefinedObjectOrFunc(leaf) :
                        undefinedObjectOrFunc);
            },
            function(leaf) {
                // create 'values' attributes. These are the leaves themselves, unless a leafValueLookup function is defined,
                // in which case we pass the leaf to the function it returns
                return self.leafValueLookup ? self.leafValueLookup(leaf) : leaf;
            },
            // stringify keys so that we can hash by something.
            function(keyObject) {
                return keyObject.getPath(self.get('keyNameProperty'));
            },
            null,
            SC.Object);
    }.property('leavesStatus', 'filteredItems', 'keyProperty', 'keyObjects', 'keyObjectsStatus', 'keyObjectsLength').cacheable(),

    /***
     * This is the flattened version of tree which is actually used by the View. It contains a list of TreeItem instances
     * that each hold the top-level instance in the keyObject. These might be Categories, Tags, etc. The leaves are the
     * second-tier instances, such as Scenarios or BuiltForms
     */
    treeItemChildren: function() {
        var self = this;
        if (this.get('tree')) {
            return $.map(this.get('tree'), function(entry, keyString) {
                return entry.kindOf ? entry : SC.Object(entry);
            }).sortPropertyPath(
                 (self.get('sortKeyProperties') || []).map(function(path) {
                     // We need to add a key prefix to each attr since we are sorting
                     // based on the key property of each object
                     return 'key.%@'.fmt(path);
                 }),
                 mapObjectToObject(self.get('keyReverseSortDict') || {}, function(key, value) {
                     // We need to add a key prefix to each key since we are sorting
                     // based on the key property of each object
                     return ['key.%@'.fmt(key), value];
                 })
             ).map(function(entry) {
                 var values = entry.values;
                 values.sortPropertyPath(self.get('sortProperties'), self.get('reverseSortDict'));
                 return Footprint.TreeItem.create({
                     keyObject: entry.key,
                     leaves: values,
                     keyNameProperty: self.get('keyNameProperty')
                 });
             });
        }
        return null;
    }.property('tree').cacheable(),

    toString: function() {
        return '%@:\n%@'.fmt(sc_super(), this.toStringAttributes('leafSet leaves keyProperty keyObjects keyNameProperty tree treeItemChildren'.w()));
    }
});
