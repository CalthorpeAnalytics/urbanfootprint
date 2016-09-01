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

sc_require('resources/sproutcore_utils');

/**
 * Mixin for SC.Observables to add search functionality.
 * The searchFilter returns a filter function that expects an item from the collection being filtered.
 * It returns YES if any of item's attributes specified by searchProperties match the current searchString.
 * Wildcards: * can be used as wildcard. / can be used at the start of the search string to do a regex search
 */
Footprint.SearchFilterMixin = {
    // Optionally use to filter which leaves are part of the tree based on searchProperties and searchFilter
    searchString: null,
    // Can be set to anything and used in the filteredItemsPropertyResolver
    // to help resolve which filteredItemsProperties are eligible for the search
    searchContext: null,
    // Used by the searchFilter to match on any record properties that are strings
    searchProperties: ['name'],
    // Optional additional filter to apply to items being filtered.
    // The filtering will run the searchFilter followed by this one if is defined
    additionalFilter: null,
    /**
     * Filter the properties of the specified here.
     * If only one property is specified it will always be the source list of the filter
     * This means that calling this.get('filteredItems') will return the items of this property
     * that are allowed through by the search string.
     * If multiple properties are specified then you must use the filteredItemsPropertyResolver
     * to resolve the source properties or sources if you want combined results
    */
    filteredItemsProperties: ['content'],
    /***
     * Resolves the searchString to one or more of the filteredItemsProperties.
     * the corresponding collection of each filteredItemProperty returned is combined to
     * present the filteredItems. By Default this returns
     * filteredItemsProperties. Override to return based on the searchString.
     * This also depends on the searchContext, which can be anything about the search that
     * is useful to resolving the filteredItemsProperties. It could, for instance, contain
     * the entire query string entered by the user if the searchString is just the portion
     * they are currently typing
     */
    filteredItemsPropertyResolver: function() {
        return this.get('filteredItemsProperties');
    }.property('searchString', 'searchContext', 'filteredItemsProperties').cacheable(),


    // Observe changes ot the filteredItems collection or its status in order to notify filteredItems
    // This doesn't check for addition and removal of items from filteredItems, just the overall content instance
    // TODO This doesn't reliably observe array range changes. I can't figure out why
    // The equivalent static observers (*property.[]) works fine
    filteredItemsPropertyDidChange: function() {
        if (!this.didChangeFor('filteredItemsPropertyCheck', 'filteredItemsProperties'))
            return;
        // Add observers to track each filteredItemsProperty
        this.get('filteredItemsProperties').forEach(function(filteredItemsProperty) {
            SC.ObservableExtensions.propertyItemsAndStatusObservation(
                'filteredItemsObserving_%@'.fmt(filteredItemsProperty),
                this,
                filteredItemsProperty,
                this,
                'filteredItemsNeedUpdate');
        }, this);
        this.filteredItemsNeedUpdate();
    }.observes('.filteredItemsProperties'),

    /***
     * If one of the filteredItemsProperties changes, overall, membership, status, whatever, call this.
     */
    filteredItemsNeedUpdate: function() {
        this.invokeOnce(this._filteredItemsNeedUpdate);
    },

    _filteredItemsNeedUpdate: function() {
        this.propertyDidChange('eligibleItemsOfFilteredProperties');
    },

    _observersInited: NO,
    /***
     * The items of the enumerable at specified one or more filteredItemsProperties that pass the
     * current searchString filter and optionally filteredItemsPropertyResolver
     * If filteredItemsProperties is one item this returns a list of its filtered items.
     * Otherwise it returns a dict keyed by filteredItemsProperty
     */
    filteredItems: function() {
        if (!this._observersInited) {
            // This needs to be called manually initially. I have no idea why it doesn't fire once at instantiation
            this.filteredItemsPropertyDidChange();
            this._observersInited = YES;
        }

        if (!this.getPath('filteredItemsProperties.length'))
            return null;

        // Get the all items of each filteredItemsProperty based on the searchString
        // This simply gives us all items that might be eligible based on the searchString
        // and optionally the searchContext
        var filteredPropertyItemsObj = this.get('eligibleItemsOfFilteredProperties');
        if (this.getPath('filteredItemsProperties.length')==1)
            // If only one property just return its items
            return filteredPropertyItemsObj[this.getPath('filteredItemsProperties.firstObject')];
        else
            // Otherwise return a dict
            return filteredPropertyItemsObj;

    }.property('filteredItemsProperties', 'eligibleItemsOfFilteredProperties').cacheable(),

    /***
     * Returns the combined items of the enums filteredItemsPropertyResolver properties.
     * Returns an SC.Object of items keyed by filteredItemsProperty with the search
     * This list of items is then filtered against the searchString
     */
    eligibleItemsOfFilteredProperties: function() {
        // Init ret to all properties with empty array
        var ret = mapToSCObject(this.get('filteredItemsProperties'), function(property) {
            return [property, []];
        });

        // Create our filter
        var searchFilter = this.get('searchFilter');
        var additionalFilter = this.get('additionalFilter');
        // Add the additionalFilter to the searchFilter if the former is specified
        var filterFunc = additionalFilter ?
            function(item) {
                return searchFilter.apply(this, [item]) && additionalFilter.apply(this, [item]);
            } :
            searchFilter;

        // Get the properties based on the current value of the searchString
        var filteredItemsProperties = this.get('filteredItemsPropertyResolver') || [];
        filteredItemsProperties.forEach(function (filteredItemProperty) {
            var items = (this.getPath(filteredItemProperty) || []).toArray().compact();
            // Apply the filter to each item
            ret.setPath(filteredItemProperty, items.filter(filterFunc, this));
        }, this);
        return ret;
    }.property('filteredItemsPropertyResolver', 'searchString', 'searchFilter', 'additionalFilter').cacheable(),

    // Creates a filter based on the current searchString, if it is non-null or not an empty string
    // Optionally this to a function that filters the leaves.
    // This will be called prior to leafValueLookup (if leafValueLookup) is defined to filter
    // the leaves that are allowed. The function must return true to allow a leaf and false to block it
    // It will be called with the TreeContent as the caller, so you can safely use this within the function
    searchFilter: function () {
        var searchString = this.get('searchString');
        if (!searchString) {
            return identityFunction;
        }
        try {
            var searchRegex = (searchString.indexOf('/') == 0) ?
                // If the user starts the string with a slash assume a regex. This is probably a useless feature
                new RegExp(searchString.slice(1, -1)) :
                // Don't let anything the user types be used for regex
                // Change any * to .*. We could add other wildcards here in the future
                new RegExp(escapeRegExp(searchString).replace('*', '.*'));
            return function (item) {
                // If we have primitive items just match. We don't care about the searchProperties
                if (['number', 'string'].contains(typeof(item)))
                    return item.toString().match(searchRegex);
                if (!this.getPath('searchProperties.length'))
                    return YES;
                // Return YES if any of the property of the item in searchProperties match the regex
                return $.any(
                    this.get('searchProperties'),
                    function(searchProperty) {
                        return (item.getPath(searchProperty) || '').match(searchRegex);
                    },
                    this
                );
            };
        }
        catch (e) {
            logWarning('Bad RegExp: %@. Exception: %@'.fmt(searchString, e.message));
            return null;
        }
    }.property('searchString', 'searchProperties').cacheable()
};
