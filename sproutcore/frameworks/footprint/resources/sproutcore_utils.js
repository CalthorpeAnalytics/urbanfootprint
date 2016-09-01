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


sc_require('resources/jquery_extensions');

/***
 * Creates an alias to the property name held in the given property
 * the given property must have a constant value
 * @param property. For example 'property_field' which is the
 * name of the property that has a constant value of the alias
 * @returns {Function}
 */
function aliasProperty(property) {
    return function (propKey, value) {
        if (value) {
            this.set(property, value)
        }
        return this.get(property)
    }.property(property).cacheable();
}

/***
 * Gets the keys of the obj
 * @param obj
 * @returns {*}
 */
function getKeys(obj) {
    return $.map(obj, function(v,k) {return k;});
}
function removeKeysMatchingObject(obj, other_obj) {
    var keys = getKeys(other_obj);
    return removeKeys(obj, keys);
}
function removeKeys(obj, keys) {
    var results = {};
    $.each(obj, function(k,v) {
        if (!keys.contains(k))
            results[k] = v;
    });
    return results;
}
/***
 * Convert obj to a new object with only the given keys
 * If obj is a sproutcore object the result will be an SC.Object.
 * Otherwise it will be a plain old js object. Use the optional
 * resultType to force it one way of the other
 * @param obj: object or SC.Object
 * @param keys: keys to filter down to
 * @param resultType: Optionally set to 'object' or SC.Object class to force the result type
 * @param filterValues: If specified, this function is called with each key and value. It
 * returns true to pass the key/value to the result, and false to block it
 * @returns {*}
 */
function filterKeys(obj, keys, resultType, filterValues) {
    if (obj.kindOf && (!resultType || resultType==SC.Object)) {
        var func = resultType=='object' ? mapToObject : mapToSCObject;
        return func(
            keys,
            function(key) {
                return obj.get(key) != undefined ? [key, obj.get(key)] : null;
            },
            null,
            resultType
        );
    }
    else if (!resultType || resultType=='object') {
        var results = {};
        keys.forEach(function(key) {
            if (typeof obj[key] != 'undefined' && (!filterValues || filterValues(key, obj[key]))) {
                results[key] = obj[key];
            }
        });
        return results;
    }
    else {
        throw Error("Invalid value for resultType. Must be null, SC.Object, or 'object");
    }
}

var statusLookup = null;
function getStatusString(status) {
    statusLookup = statusLookup || $.mapToDictionary($.grep(
        $.map(SC.Record, function(key,value) {
            return [[key, value]]; }),
        function(a) { return a[1].match(/^[A-Z_]+$/) != null; }
    ));
    return statusLookup[status] || "Unmatched status: %@".fmt(status);
}

function logProperty(property, propertyName, dependentPropertyName) {
    if (dependentPropertyName) {
        SC.Logger.debug("%@: %@ observing %@ with value %@ and status %@",
            new Date(),
            dependentPropertyName,
            propertyName,
            property,
            property ? (property.status ? getStatusString(property.get('status')) : 'no status') : 'no property');
    }
    else {
        SC.Logger.debug("%@: property %@ with value %@ and status %@",
            new Date(),
            propertyName,
            property,
            property ? (property.status ? getStatusString(property.get('status')) : 'no status') : 'no property');
    }
}
function logStatus(property, propertyName, dependentPropertyName) {
    if (dependentPropertyName) {
        SC.Logger.debug("%@: %@ observed change to %@: Observed status: %@", new Date(), dependentPropertyName, propertyName,
            property ? getStatusString(property.get('status')) : 'Property undefined!');
    }
    else {
        SC.Logger.debug("%@: Status of property %@ is: %@", new Date(), propertyName,
            property ? getStatusString(property.get('status')) : 'Property undefined!');
    }
}
function logDidFetch(recordType) {
    SC.Logger.debug("%@: Did fetch recordType: %@", new Date(), recordType.toString());
}
function logDidCachedFetch(recordType) {
    SC.Logger.debug("%@: Did cached fetch recordType: %@", new Date(), recordType.toString());
}
function logCached(recordType) {
    SC.Logger.debug("%@: Added recordType %@ to the cache", new Date(), recordType.toString());
}

function logCount(property, propertyName) {
    SC.Logger.debug("Property %@, length %@", propertyName,
        property ? (typeof(property.length) == 'function' ? property.length() : property.length) : "null!");
}

function logWarning(error) {
    SC.Logger.warn(error.message || error || "Unknown Error");
    if (error.stack)
        SC.Logger.error(error.stack);
}

Footprint.logError = function(error) {
    SC.Logger.error(error.message || error || "Unknown Error");
    if (error.stack)
        SC.Logger.error(error.stack);
}

function logInfo(message) {
    SC.Logger.info(message);
}

/***
 * Asserts that the given state is one of the current states (or the current state)
 * @param state
 */
function assertCurrentState(state) {
    ok($.any(Footprint.statechart.currentStates(), function(state) {
        return state.kindOf(Footprint.LoadingApp);
    }),
    "Expect current state to be Footprint.statechart.loadingApp. Actual state(s): %@".fmt(Footprint.statechart.currentStates().join(', ')));
}
/**
 * Assert the given property is not null
 * @param propertyValue: the evaluated property
 * @param propertyName: the name of the property
 */
function assertNotNull(propertyValue, propertyName) {
    ok(null != propertyValue, "Expect %@ not null".fmt(propertyName));
}
function assertNull(propertyValue, propertyName) {
    ok(null != propertyValue, "Expect %@ to be null, but was %@".fmt(propertyName, propertyValue));
}

function assertStatus(property, status, propertyName) {

    assertNotNull(property, propertyName);
    equals(
        property.get('status'),
        status,
        "For property %@, expect status %@. Actual status: %@. Property value:".fmt(
            propertyName,
            getStatusString(status),
            getStatusString(property.get('status')),
            property.toString()));
}
function assertNonZeroLength(value, propertyName) {
    var length = typeof(value.length) == 'function' ? value.length() : value.length
    ok(length,
       'Expect non-zero items for %@. Actual %@'.fmt(propertyName, length));
}

function assertLength(expectedLength, property, propertyName) {
    length = typeof(property.length) == 'function' ? property.length() : property.length
    equals(expectedLength, length,
        'Expect %@ items for %@. Actual %@'.fmt(expectedLength, propertyName, length));
}

function assertEqualLength(expectedLength, actualLength, propertyName) {
    equals(expectedLength, actualLength,
        'Expected %@ items for %@. Actual %@'.fmt(expectedLength, propertyName, length));
}

function assertKindForList(type, property, propertyName) {
    var list = typeof(property.length) == 'function' ? property.toArray() : property;
    $.each(list, function(i, item) {
        ok(item.kindOf(type), 'Expected items of type %@ for %@. Actual [%@]'.fmt(
            type.toString(), propertyName, $.map(list, function(item, i) { return item.toString()}).join(';')));
    })
}

//http://stackoverflow.com/questions/3115982/how-to-check-javascript-array-equals
function normalEquals(array) {
    return array.every(function(x){return x==array[0]});
}
function zip(arrays) {
    return arrays[0].map(function(_,i){
        return arrays.map(function(array){return array[i]})
    });
}
function type(x) {
    return Object.prototype.toString.call(x);
}
function allTrue(array) {
    return array.reduce(function(a,b){return a&&b},true);
}

function deepEquals(things) {


    if( type(things[0])==type([])
        && normalEquals(things.map(type))
        && normalEquals(things.map(function(x){return x.length})) )
        return allTrue(zip(things).map(superEquals));
    else
        return normalEquals(things);
}

function _dump(view) {
    if (!view)
        return 'null';
    var viewString = 'id: %@, type: %@\n'.fmt(view.get('layerId'), view.toString());
    if (!view || view.kindOf(SC.MainPane) )
        return [view ? viewString: 'null'];
    else
        return [viewString].concat(_dump(view.get('parentView')));
}
/***
 * Creates an array of parent views starting with the given view and going up the parents
 * @param view
 * @returns an array of strings produced by view.toString()
 */
function parentViews(view) {
    return _dump(view);
}
/***
 * Dump the view and all its parents to a string separated by '\n\n'
 * @param view
 * @returns {Client|*|string|String}
 */
function dumpParentViews(view) {
    return console.log(_dump(view).join("\n"));
}

/***
 * Dumps the given view and all its parents along with the value
 * of the given property, which may be a chained property
 * @param view
 * @param property
 * @param justValueType: Default false, set true to show just the
 * property value's type, instead of dumping the whole value. This
 * only applies to SC types (anything with a constructor property)
 * @returns {*|Socket|string|String}
 */
function dumpPropertyForParentViews(view, property, justValueType) {
    return _mapPropertyForParentViews(view, property, justValueType).join('\n');
}
function _mapPropertyForParentViews(view, property, justValueType) {
    var value = view.getPath(property);
    var parentViewProperty = view.get('anchor') ? 'anchor' : 'parentView';
    var displayValue;
    if (value===undefined)
        displayValue = 'undefined';
    else if (value===null)
        displayValue = 'null';
    else
        displayValue = justValueType ? (value.constructor || value) : value;
    return [[view.constructor, displayValue].join(':')].concat(
        view.get(parentViewProperty) ?
            _mapPropertyForParentViews(view.get(parentViewProperty), property, justValueType) :
            [])
}

/***
 * Return the parentView at the index number
 * @param index
 */
function getParentView(view, index) {
    if (index > 0)
        return getParentView(view.get('parentView'), index-1);
    else
        return view;
}

function findParentViewByKind(view, clazz) {
    var parentView = view.get('parentView');
    if (!parentView) {
        return null;
    }
    else if (parentView.kindOf(clazz)) {
        return parentView;
    }
    else {
        return findParentViewByKind(parentView, clazz)
    }
}

function firstOrNull(array) {
    return array.length > 0 ? array[0] : null
}

function oneAndOnlyOne(array) {
    if (array.length != 1)
        throw "Expected exactly one value, found %@".fmt(array);
    return array[0];
}

// For some reason the SC.View.views array doesn't contain all the views. Use this to find relative to a known view
function findChildView(view, viewId) {
    return firstOrNull($.map(view.childViews || [], function(childView) {
        if (childView.$().attr('id')==viewId) {
            return childView;
        }
        else {
            return findChildView(childView, viewId)
        }
    }))
}

function findChildViewByKind(view, clazz) {
    return firstOrNull($.map(view.childViews || [], function(childView) {
        if (childView.kindOf(clazz)) {
            return childView;
        }
        else {
            return findChildViewByKind(childView, clazz)
        }
    }));
}

function findViewsByKind(clazz) {
    return $.grep($.values(SC.View.views), function(value) {
        return value.kindOf(clazz);
    });
}
function findChildViewsByKind(view, clazz) {
    return (view.childViews || []).map(function(childView) {
        if (childView.kindOf(clazz)) {
            return childView;
        }
        else {
            return this.findChildViewsByKind(childView, clazz)
        }
    }, this);
}

/***
 * Adds an _fpViewName and _fpViewPath to each view for debugging.
 * The _fpViewName is based on the parent view's child view name,
 * and the _fpViewPath is the concatination of the lineage of these names (e.g. mainPane.sectionView.listView.exampleView)
 */
Footprint.applyNamesToViews = function() {
    findViewsByKind(SC.Pane).forEach(function(pane) {
        // Resolve the name of the pane's page
        var pageName = $.map(Footprint, function(k, v) { return (Footprint[v] == pane.page) ? v : null })[0] || 'none';
        // TODO Resolving the name of the pane is hard, but it should match something in the top-level Footprint object
        pane._fpViewName = pane.constructor;
        pane._fpViewPath = 'page:%@.pane:{%@}'.fmt(pageName, pane._fpViewName);
        Footprint.applyNamesToView(pane)
    });
};

/***
 * Called by applyNamesToViews to recursively give each view an _fpViewName and _fpViewPath
 * @param view
 */
Footprint.applyNamesToView = function(view) {
    var childViewNames = view.constructor.prototype.childViews;
    return (view.childViews || []).forEach(function(childView) {
        // First try to match the view to a named child view from the parent view prototype
        childView._fpViewName = childViewNames.find(function(childViewName) { return view[childViewName]}) ||
                // Failing that just find the index of the child view in the parent view's child view instances
                view.childViews.map(function(aChildView, i) { return childView==aChildView ? 'child_%@'.fmt(i) : null }).compact()[0] ||
                // Failing all...this should not happen
                'unknown';
        childView._fpViewPath = '%@.%@'.fmt(view._fpViewPath, childView._fpViewName);
        Footprint.applyNamesToView(childView)
    }, this);
};

function mouseClick(target) {
    if (!target)
        throw "view is null";
    SC.Event.trigger(target, "mousedown");
    SC.Event.trigger(target, "mouseup");
    SC.RunLoop.begin();
    SC.RunLoop.end();
}

function mouseDoubleClick(target) {
    SC.Event.trigger(target, "mousedown");
    SC.Event.trigger(target, "mouseup");
    SC.Event.trigger(target, "mousedown");
    SC.Event.trigger(target, "mouseup");
    SC.RunLoop.begin();
    SC.RunLoop.end();
}

function keyboardEnterClick(target) {
    var event = SC.Event.simulateEvent(target, "keydown", {
        which: 13,
        keyCode: 13
    });
    SC.Event.trigger(target, "keydown", event);
    event = SC.Event.simulateEvent(target, "keyup", {
        which: 13,
        keyCode: 13
    });
    SC.Event.trigger(target, "keyup", event);
    SC.RunLoop.begin();
    SC.RunLoop.end();
}

/***
 * Edits the text of the given labelView, adding __Test to the current value
 * @param labelView
 */
function editLabel(labelView, pane) {
    var parentView = labelView.get('parentView');
    var target = labelView.$().get(0);
    mouseDoubleClick(target);
    var input = parentView.$('input')[0] || (pane && pane.$('.inline-editor').find('input')[0]);
    if (!input) {
        ok(false, "Failed to invoke inline-editor with double click");
    }
    else {
        var value = labelView.get('value');
        input.value = '%@__Test'.fmt(value);
        keyboardEnterClick(target);
        parentView.$().css('position', 'relative');
    }
}

function updateNameAndValidate(pane, nameView, content, i) {
    equals(
        content.get('name'),
        nameView.get('value'),
        'Expecting a name for item index %@, representing instance %@'.fmt(i, content.toString()));
    var name = nameView.get('value');
    var updatedName = '%@__Test'.fmt(name);
    editLabel(nameView, pane);
    equals(
        updatedName,
        nameView.get('value'),
        'Expecting a view name to be updated to %@ for item index %@, representing instance %@'.fmt(updatedName, i, content.toString()));
    equals(
        updatedName,
        nameView.$().text(),
        'Expecting a view label text to be updated to %@ for item index %@, representing instance %@'.fmt(updatedName, i, content.toString()));
}

/***
 * Simply returns 'parentView' concatinated by strings for the number of times needed. A period is placed at the start but not at the end
 * @param times
 * @param path: the path to append to the parentView string
 */
function parentViewPath(times, path) {
    return '.'+$.map(new Array(times), function(x) { return 'parentView'}).join('.')+path;
}

/***
 * Vefiry that the given object is a SC.Object derivative of the specified kind
 * @param obj
 * @param kind SC.Object derived class.
 * @returns {*|Boolean}
 */
function isSCObjectOfKind(obj, kind) {
    return obj && obj.kindOf && obj.kindOf(kind);
}

/***
 * Joins all non-null path segments with a '.'. This is useful when some segments might be null
 * @param segments
 */
function formPropertyPath(segments) {
   return segments.map(function(segment) { return  segment || null }).compact().join('.')
}

/***
 * Inspects the item, which might be a Sproutcore Array and converts it to an normal array.
 * For non-arrays, the item is wrapped as an array
 * @param array
 * @returns {*}
 */
function arrayOrItemToArray(array) {
    if (!array)
        return []
    if (array.isEnumerable)
        return array.toArray();
    else
        return [array];
}

function arrayIfSingular(array) {
   return array.isEnumerable ? array : [array];
}
function firstIfArray(array) {
    return array.isEnumerable ? array.get('firstObject') : array;
}
function singularize(array) {
    if (array && array.isEnumerable && array.get('length') != 1) {
        throw Error("Attempt to singularize an array with 0 or > 1 values: %@".fmt(array))
    }
    return array && array.isEnumerable ? array.get('firstObject') : array;
}
/***
 * Returns true if the given item is one of the SC Array types
 * @param array
 * @returns {*|Boolean}
 */
function isSCArray(array) {
    return (array.kindOf && (array.kindOf(SC.Enumerable) || array.kindOf(SC.ChildArray) || array.kindOf(SC.ManyArray) || array.kindOf(SC.RecordArray) ));
}

/***
 * Returns an ArrayController with the content property made into an array if needed
 * @param context - Any number of objects
 */
function toArrayController() {
    if (!arguments.length > 0 || !arguments[0]) {
        Footprint.logError("toArrayController called without context or a null context. You probably didn't want to do this. Returning an empty ArrayController");
        return SC.ArrayController.create();
    }
    // Merge the arguments
    var arrayController = SC.ArrayController.create.apply(SC.ArrayController, arguments);
    // Make sure any content is an array
    if (arrayController.get('content'))
        arrayController.set('content', arrayIfSingular(arrayController.get('content')));
    return arrayController;
}

/***
 * Maps an array of values with a function that returns a two-item array. The first item is the attribute name, the second is the mapped value
 * Returns a new SC.Object instance with those attributes and values
 * @param array
 * @param func
 * @returns {*}
 */
function mapToSCObject(array, func, target) {
    return SC.Object.create($.mapToDictionary(array, func, null, target));
}
function mapToObject(array, func, target) {
    return $.mapToDictionary(array, func, null, target);
}
/***
 * Like mapToSCObject, but the end result is an Array. The function returns
 * and index and value for each item of the array. This allows one to
 * create an array with specific indexes.
 * @param array
 * @param func
 * @param target
 */
function mapToExplicitIndexArray(array, func, target) {
    var target = target || this;
    var obj = [];
    (array || []).map(function(value, index) {
        var indexAndResult = func.apply(target, [value, index]);
        if (indexAndResult)
            obj[indexAndResult[0]] = indexAndResult[1];
    });
    return obj;
}
/***
 * Uses the given store and recordType to create a record in the store of the given record type with dictionary
 * that is created by mapping each item of the array to the func
 * @param array
 * @param func. Returns a two-value array, the attribute and value for the dict
 * @param store
 * @param recordType
 * @param target
 * @returns {*|Boolean|SC.Record}
 */
function mapToRecord(array, func, store, recordType, target) {
    return store.createRecord(recordType, $.mapToDictionary(array, func, null, target));
}
function mapObjectToSCObject(obj, func, target) {
    return SC.Object.create($.mapObjectToObject(obj, func, null, target));
}
/**
 * Maps an object to another object
 * @param obj
 * @param func. Function that expects each key and value as args and returns a two-element
 * array to represent the mapped key/value
 * @param target. Optional target to call the function with
 * @returns {{}}
 */
function mapObjectToObject(obj, func, target) {
    var resultObj = {};
    Object.keys(obj).forEach(function(key) {
        var result = func.apply(target || this, [key, obj[key]]);
        if (result)
            resultObj[result[0]] = result[1];
    });
    return resultObj;
}
/***
 * Maps an object to a list
 * @param obj
 * @param func
 * @param target
 * @returns {Array}
 */
function mapObjectToList(obj, func, target) {
    func = func || function(a) { return a;}
    var results = [];
    var i = 0;
    $.each(obj, function(key, value) {
        results.push(func.apply(target, [key,value, i++]));
    });
    return results;
}

/***
* Returns the unique recordTypes for the given records of the given store
 */
function uniqueRecordTypes(store, records) {
    return records.map(function(record) {
        return store.recordTypeFor(record.get('storeKey'));
    }, this).uniq()
}

/***
 * Change a record's status to the toStatus if it matches the fromStatus.
 * This only works in limited situations, e.g. ERROR to DIRTY.
 * @param store
 * @param record
 * @param fromStatus
 * @param toStatus
 */
Footprint.changeRecordStatus = function(store, record, fromStatus, toStatus) {
    if (record.get('status') === fromStatus) {
        record.propertyWillChange('status');
        store.writeStatus(record.get('storeKey'), toStatus);
        record.propertyDidChange('status');
    }
}

function getCallStackDuplicateSize(start, max, match) {
    max = max || 50;
    start = start || 0
    var count = 0, fn = arguments.callee;
    while (start-- > 0)
        fn = fn.caller;
    while ( (fn = fn.caller) ) {
        if (!fn.toString().match(match))
            break;
        SC.Logger.debug(fn.toString());
        count++;
        if (count > max) {
            Footprint.logError('getCallStackSize over %@'.fmt(max));
            break;
        }
    }
    return count;
}

function getCallStackSize(max) {
    max = max || 50;
    var count = 0, fn = arguments.callee;
    while ( (fn = fn.caller) ) {
        count++;
        if (count > max)
            Footprint.logError('getCallStackSize over %@'.fmt(max));
    }
    return count;
}

/***
 * Like Array.mapProperty, but maps any number of properties.
 * @param content
 * @param keys
 * @param mapFunction. Optional map function to apply to all results, such as a toString
 * @returns {*|Array}
 */
function mapProperties(content, keys, mapFunction, target) {
    return content.map(function (next) {
        return keys.map(function(key) {
            var item = next ? (next.get ? next.get(key) : next[key]) : null;
            return mapFunction ? mapFunction.apply(target || this, [item]) : item;
        }, target);
    }, target || this);
}

function mapPropertyPath(content, propertyPath) {
    if (!propertyPath || propertyPath == '')
        return content;
    var segments = propertyPath.split('.');
    return mapPropertyPath((content || []).mapProperty(segments[0]), segments.slice(1).join('.'));
}

/***
 * Returns the value if not equal to null or undefined, otherwise return the default value
 * @param value
 */
function passThroughNeitherNullNorUndefined(value, defaultValue) {
    return value==null || typeof(value) == 'undefined' ? defaultValue : value
}
function neitherNullNorUndefined(value) {
    return value !=null && typeof(value) != 'undefined';
}

/***
 * Returns a reversed object, meaning keys and values swap.
 * This expects all unique values and doesn't make sense for SC.Object
 * @param obj
 */
function reverseObject(obj) {
    return $.mapObjectToObject(obj, function(key, value) { return [value, key]});
}

/***
 * Ternary operator that passes the first value to the second or third as a function argument
 * @param obj. Value to test
 * @param ifNonNull. Function to call if obj is non-null. obj and optional caller are passed as args
 * @param ifNull. Function to call if obj is null. obj and optional caller are passed as args
 */
function ifCond(obj, ifNonNull, ifNull, caller) {
    if (obj) {
        return caller ? ifNonNull(obj, caller) : ifNonNull(obj);
    }
    else {
        return caller ? ifNull(obj, caller) : ifNonNull(obj);
    }
}
/***
 * Like ifCond but uses a different test and the calls the functions
 * @param condition
 * @param obj
 * @param ifTrue
 * @param ifNull
 * @param caller
 * @returns {*}
 */
function ifExternalCond(condition, obj, ifTrue, ifFalse, caller) {
    if (condition) {
        return caller ? ifTrue(obj, caller) : ifTrue(obj);
    }
    else {
        return caller ? ifFalse(obj, caller) : ifFalse(obj);
    }
}

/***
 * Just returns the argument
 * @param obj
 * @returns {*}
 */
function identityFunction(obj) {
    return obj;
}

/***
 * Resolves the object for the path or leaves it alone if it's already a type
 * @param typeOrPath
 * @returns {*}
 */
function resolveObjectForPropertyPath(typeOrPath) {
   return typeof typeOrPath === 'string' ?
       SC.objectForPropertyPath(typeOrPath):
       typeOrPath;
}

/***
 * Merges any number of dicts together, returning a new dict
 */
function merge() {
    return $.extend.apply($, [{}].concat(Array.prototype.slice.call(arguments)));
}

// http://stackoverflow.com/questions/3446170/escape-string-for-use-in-javascript-regex
/***
 * Escape a string to be used in regex
 * @param str
 * @returns {*|SC.SparseArray|SC.ChildArray|XML|string|SC.TreeItemObserver}
 */
function escapeRegExp(str) {
  return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
}

/**
 * This wraps an event handler that handles events outside the normal SproutCore event loop, so that
 * the event handler can do SproutCore-related things, such as set properties. This is most useful when
 * you have a 3rd party library like d3 or leaflet and you need to use that library's event binding.
 *
 * For example:
 *
 *     var lines = d3.select(...).data(...).append(...);
 *
 *     lines.on('click', Footprint.nativeEventHandler(function(e) {
 *        // regular sproutcore stuff here.
 *     }, this));
 *
 * The optional second argument can be used to override the target of the handler, like with other SC calls.
 * It defaults to the local this, which is the SC.Application
 */
Footprint.nativeEventHandler = function nativeEventHandler(handler, target) {
    var handleEvent = function handleEvent() {
        SC.RunLoop.begin();
        try {
            handler.apply(target || this, arguments);
        } catch(ex) {
            SC.RunLoop.end();
            // On some browsers, this will lose the stack, and the
            // exception will appear to originate here, but this works
            // in Chrome.
            throw ex;
        }
        SC.RunLoop.end();
    }.bind(this);

    return handleEvent;
};

/**
 *
 */
Footprint.makeEntityFeatureId = function(dbEntityId, featureId) {
    return '%@_%@'.fmt(dbEntityId, featureId);
};

/**
 * Adds class names to everything in Footprint.*.
 * TODO: Better distinguish between classes, instances, and raw constants.
 * Also crawls all the views to name views by their child name and full name
 */
Footprint.addClassNames = function() {
    for (var cls in Footprint) {
        if (Footprint[cls]) {
            Footprint[cls]._fpName = 'Footprint.' + cls;
        }
    }
    Footprint.applyNamesToViews();
};

/***
 * Adds _1 to a name when the name is a duplicate and needs to be distinguisted. If
 * _1 is already there it becomes _2, etc
 * @param name. The name to add _1 to or something greater
 * @returns {*} the name with the _n added
 */
function incrementName(name) {
    var r = /(.+)_(\d+)$/;
    var m = name.match(r);
    return m ?
        '%@_%@'.fmt(m[1], parseInt(m[2]) + 1) :
        '%@_1'.fmt(name);
}
