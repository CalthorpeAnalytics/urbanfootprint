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


/**
 *  A Library of functional extensions to jquery to be created as needed.
 *  Functions and methods can be created as follows:
 *
 *  $.fn.extend({
 *	    myMethod: function(){...}
 *	});
 *	//jQuery("div").myMethod();
 *
 *	$.extend({
 *	    myFunction: function(){...}
 *	});
 *	//jQuery.myFunction();
 */

$.extend({
    /**
     * Returns true if any item passed to fun returns true. I can't believe this doesn't already exist in jQuery for non-selectors
     * @param list
     * @param func
     * @param target. Optional define the target (this) of the function
     * @return {*}
     */
    any: function(list, func, target) {
        var found = false;
        $.each(list, function(index, value) {
            // TODO this should pass i as the first arg to be consistent
            if (func.apply(target || this, [value])) {
                found = true;
                return false; // break from loop
            }
        });
        return found;
    },

    /***
     * Returns true if all items pass the func filter
     * @param list
     * @param func
     * @returns {boolean}jqueryE
     */
    allMatch: function(list, func) {
        return $.grep(list, func || function(x) { return x; }).length == list.length;
    },

    /***
     * Grep the obj to a new object
     * @param obj
     * @param func
     * @returns {{}}
     */
    grepObject: function(obj, func) {
        var results = {};
        $.each(obj, function(key, value) {
           if (func(key,value))
            results[key] = value;
        });
        return results;
    },

    /***
     *  extract just the values of an object into an array
     * @param obj
     */
    values: function(obj) {
        var results = [];
        $.each(obj, function(key, value) {
           results.push(value);
        });
        return results;
    },

    /**
     * dualMap allows two equal length collections to be mapped in parallel
     */
    dualMap: function(array1, array2, func) {
        if (array1.length != array2.length) {
            throw new Error($.format("Array lengths are not equal. array1:{0}, array2:{1}",
                array1.length,
                array2.length));
        }
        return $.map(array1, function(value, index) {
           return func(value, array2[index], index);
        });
    },

    /**
     * dualMaps and returns true if all map to true
     * @param array1
     * @param array2
     * @param func
     * @returns {boolean}
     */
    dualAllMatch: function(array1, array2, func) {
        return $.allMatch($.dualMap(array1, array2, func));
    },

    /**
     * dualMapToDictionary maps two arrays to keys and values, respectively. The array must be the same length.
     */
    dualMapToDictionary: function(array1, array2) {
        if (array1.length != array2.length) {
            throw new Error($.format("Array lengths are not equal. array1:{0}, array2:{1}",
                array1.length,
                array2.length));
        }
        return $.mapToDictionary(array1, function(value, index) {
            return [value, array2[index]];
        });
    },

    /* Maps each value to a two item array which becomes a key value of a dictionary. Duplicates are overridden.
     * The third optional argument is the objectType to construct.
     * func takes a key values and should return a two item array, the transformed key value. If null is returned the key/value are not included
     * if combinedValues is specified, values with the same key are grouped in an array. Values that
     * don't share a key are put in a single array
    */
    mapToDictionary: function(array, func, objectType, target, combinedValues) {
        func = func || function(a) { return a;}
        var target = target || this;
	    var obj = objectType ? objectType() : {};
        (array || []).map(function(value, index) {
	        var result = func.apply(target, [value, index]);
            if (result) {
                if (!combinedValues) {
                    obj[result[0]] = result[1]
                }
                else {
                    obj[result[0]] = obj[result[0]] || [];
                    obj[result[0]].push(result[1]);
                }
            }
        });
	    return obj;
    },

    /***
     *  Maps each value to a two item array which becomes a key and value of a result Object. Duplicates are overridden. The third optional argument is the Object type to construct
     * @param obj: The object to map
     * @param func: A function that expects a key and value, which maps each pair from obj. Return null to exclude a pair from the results
     * You can also return more than a pair. Every two items will be added two the result array as a key value
     * @param objectType: The optional objectType to use to construct the result object. Defaults to Object. This can also be a function that returns the constructed object
     * @param keyRegex Filter through only keys matching the regex, /^[a-z]/ by default
     * @return {*} An object with the mapped key/values
     */
    mapObjectToObject: function(obj, func, objectType, keyRegex) {
        func = func || function(a) { return a;}
        var resultObj = objectType ? objectType() : {};
        $.each(obj, function(key, value) {
            if (!keyRegex || key.match(keyRegex)) {
                var result = func(key, value);
                if (result)
                    for (i=0; i<result.length; i+=2)
                        resultObj[result[i]] = result[i+1];
            }
        });
        return resultObj;
    },

    /**
     * Maps the array to a function that returns a list of values where each value represents a dimension of the result hash,
     * except for the last value which represents the value of the inner most hash.
     * Thus three function returning ['a','b','c'], ['a','d','e'], ['b','f','g']
     * create a hash {a:{b:c}, a:{d:e}, b:{f:g}}
     * Duplicates are overwritten
     * @param array
     * @param func
     * @return {Object}
     */
    mapToMultiDimensionalDictionary: function(array, func) {
        var hash = {};
        $.each(array, function(index, value) {
            results = func(value, index);
            $.addDeep(hash, results)
        });
        return hash;
    },

    /**
     * Maps the given array to a dictionary keyed by the results of keyFunc and valued by the results of valueFunc. Duplicate key results merge their value results into a single array. Use this function when the keyFunc needs to return objects. Javascript doesn't support objects as keys, so you must supply a keyToString function that maps the result of keyFunc to a string to use for the actual key. The key object will be stored in the value, as described below.
     * @param array - values to map
     * @param keyFunc - operates on each array item and returns a single or array of keys. Each key value returned becomes a key of the result hash. The key is also added to the value of each hash entry at entry.key. The reason for this is that hash keys are always strings, so this maintains the obj value of the key
     * @param valueFunc - operates on each array item and adds the value for the result hash entry.values attribute. The same value is applied to each result of keyFunc
     * @param keyToString - optionally converts each key from keyFunc to a string for the actual keys of the result hash. It's important to have a simple key like an id so that the uniqueness check works on the keys
     * @param objectType The object type to use for the result. {} by default. You can pass a function or class here, either will be invoked using objectType() or class.create
     * @param entryObjectType The object type to use for each entry. {} by default. You can pass a function or class here, either will be invoked using objectType() or class.create
     * Example args [1,2,3], function(x) { return [new Foo(bar:'a'),new Foo(bar:'b')] }, function (foo) { return foo.bar; } results in
     * {'a':[{key:foo(with bar a), values:[1,2,3], 'b':{key:foo(with bar b), values:[1,2,3]}}
     * @return {Object}
     */
    mapToCollectionsObjectWithObjectKeys: function(array, keyFunc, valueFunc, keyToString, objectType, entryObjectType) {
        objectType = objectType || Object;
        var resultObj = objectType ?
            (objectType.kindOf ? objectType.create() : objectType()) :
            {};
        keyToString = keyToString || function(k) { return k;};
        array.forEach(function(value, index) {
            key = keyFunc(value, index);
            value = valueFunc(value, index);
            arrayOrItemToArray(key).forEach(function(k, i) {
                var keyString = keyToString(k);
                if (!resultObj[keyString]) {
                    var entry = entryObjectType ?
                                (entryObjectType.kindOf ?
                                    entryObjectType.create({key:k, values:[]}) :
                                    objectType({key:k, values:[]})) :
                                {key:k, values:[]};
                    if (objectType.kindOf)
                        resultObj.setPath(keyString, entry)
                    else
                        resultObj[keyString] = entry;
                }
                jQuery.merge(resultObj[keyString].values, [value]);
            });
        });
        return resultObj;
    },
    /**
     * Likes mapToCollectionsObjectWithStrongKeys, but assumes the key is a primitive, and thus returns a simple Object of the mapped keys and value collections
     * @param array The array or enumerable to map
     * @param keyFunc Maps an array value to a key or array of keys.
     * @param valueFunc Maps an array value to a value. values of the same key are concatinated into a single array
     * @param objectType The object type to use for the result. {} by default. You can pass a function or class here, either will be invoked using objectType()
     * @param keyRegex Filter through only keys matching the regex, /^[a-z]/ by default
     * @returns {Object} An object of the given objectType keyed by the results of keyFunc and valued by the concatinated items of valueFunc
     */
    mapToCollectionsObject: function(array, keyFunc, valueFunc, objectType, keyRegex) {
        keyRegex = keyRegex || /^[a-z]/
        return jQuery.mapObjectToObject(
            jQuery.mapToCollectionsObjectWithObjectKeys(array, keyFunc, valueFunc, null, objectType),
            function(key, value) {
                return [key, value.values];
            },
            objectType,
            keyRegex);
    },
    /***
     * Maps an array of items to dict key and value, where values are grouped as arrays
     * in case they have the same key
     *
     * @param array
     * @param func
     */
    mapToCollectionsObjectOneFunc: function(array, func, objectType, target) {
        return $.mapToDictionary(array, func, objectType, target, true);
    },

    /**
     * Like map but sends the previous result to func as a second argument, and the current index as the third.
     * This is a like an accumulator or reducer, but just intended for chaining values together
     * Returns the mapped items.
     * @param array
     * @param func: Takes each item, the previous func result or null, and the current index
     */
    mapWithPreviousResult: function(array, func) {
        var results = [],
            previous = null;
        jQuery.each(array, function(i, item) {
            previous = func(item, previous, i);
            results.push(previous);
        });
        return results;
    },
    /***
     * Accumulate results.
     * @param array
     * @param func. The function expects the current item, the previous accumulation (or null if i==0), and the third argument is the index i
     * The function should accumulate using the current item and previous accumulation. The return value becomes the previous accumulation
     * argument for the next iteration
     * @returns {*}. The last accumulation result
     */
    accumulate: function(array, func) {
        return this.mapWithPreviousResult(array, func).slice(-1)[0];
    },

    /***
     * Calls the value on the given function if not null. Otherwise returns undefined
     * @param value
     * @param func function that takes value as its argument
     */
    ifNotNull: function(value, func) {
       if (value)
           return func(value);
    },

    /***
     * Returns an array or a default if not an array
     * @param array
     * @param defaultArray
     * @returns {*}
     */
    arrayOrIfEmpty: function(array, defaultArray) {
        return Array.isArray(array) ? array : defaultArray;
    },

    arrayOrSingleItemArray: function(array) {
        return Array.isArray(array) ? array : [array]
    },

// **************************************************************************
// Copyright 2007 - 2009 Tavs Dokkedahl
// Contact: http://www.jslab.dk/contact.php
//
// This file is part of the JSLab Standard Library (JSL) Program.
//
// JSL is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// any later version.
//
// JSL is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.
// ***************************************************************************

// Return new array with duplicate values removed
// Modified to extend jQuery instead of Array
    uniqueItems: function(array) {
        return jQuery.uniqueBy(array)
    },
    lastItem: function(array) {
        return array[array.length-1];
    },
    /***
     * Filter by unique item by mapping each value to something else, like an id, that can be checked for uniqueness
     * @param array
     * @param uniqueMap
     */
    uniqueBy: function(array, uniqueMap) {
        uniqueMap = uniqueMap || function(x){return x;};
        var a = [];
        var l = array.length;
        for(var i=0; i<l; i++) {
            for(var j=i+1; j<l; j++) {
                // If this[i] is found later in the array
                if (uniqueMap(array[i]) === uniqueMap(array[j]))
                    j = ++i;
            }
            a.push(array[i]);
        }
        return a;
    },
    /**
     *  Prepends prepend to the given string if it doens't already begin with prepend. Useful for adding a # to a color string
     * @param string
     * @param prepend
     * @return {*}
     */
    prependIfNeeded: function(string, prepend) {
        return string.indexOf(prepend)==0 ? string : prepend+string;
    },
    /**
     * Rounds a float to the given number of decimals by multiplying-dividing it
     * @param floaty
     * @param decimals
     * @return {Number}
     */
    roundFloat: function(floaty, decimals) {
        return Math.round(floaty*Math.pow(10,decimals))/Math.pow(10,decimals);
    },
    /**
     * Returns the first and last elements of the given array as a two element array
     * @param array
     * @return {Array}
     */
    extremes: function(array) {
        return [array[0], array[array.length-1]];
    },
    /**
     * Shallow flatten an array of arrays and/or single items.
     * @param array
     */
    shallowFlatten: function(array) {
        var results = [];
        array.forEach(function(a) {
            a && a.isEnumerable ?
                results.pushObjects(a) :
                results.pushObject(a);
        });
        return results;
    },
    /***
     * Shallow flatten the array and map the results
     * @param array
     * @param func
     * @param target
     * @returns {*|Array}
     */
    flatMap: function(array, func, target) {
        return jQuery.shallowFlatten(array.map(func, target));
    },
    deepEquals: function(a, b) {
        var result = true;

        function typeTest(a, b) {return (typeof a == typeof b)}

        function test(a, b) {
            if (!typeTest(a, b)) return false;
            if (typeof a == 'function' || typeof a == 'object') {
                for (var p in a) {
                    result = test(a[p], b[p]);
                    if (!result) return false;
                }
                return result;
            }
            return (a == b);
        }
        return test(a, b);
    },

    has: function(array, v) {
        for (i=0;i<array.length;i++){
            if (array[i]==v) return i;
        }
        return false;
    },
    addDeep: function(hash, dimensions) {
        current = hash;
        last_key = null;
        $.each(dimensions, function(i, dimension) {
           if (i==dimensions.length-1) {
                current[last_key] = dimension
           }
           else if (!current[dimension]) {
               current[dimension] = {};
               current = current[dimension];
               last_key = dimension;
           }
        });
    },
    put: function(url, data, callback, type) {
        return _ajax_request(url, data, callback, type, 'PUT');
    },
    deleteRequest: function(url, data, callback, type) {
        return _ajax_request(url, data, callback, type, 'DELETE');
    }
});


String.prototype.capitalize = function() {
    return this.replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
};
Array.prototype.clear = function() {
    this.splice(0, this.length);
};

$.fn.extend ({
    /**
     * Calls the given getter function (e.g. 'width') indicated by a string on each parent until the value isn't null
     * @param item
     * @param getter
     */
    ancestorNonZeroValue: function(getter) {
       var value = this[getter]();
       return (value != 0) ? value : this.parent().ancestorNonZeroValue(getter);
    }
});
$.fn.htmlClean = function() {
    this.contents().filter(function() {
        if (this.nodeType != 3) {
            $(this).htmlClean();
            return false;
        }
        else {
            return !/\S/.test(this.nodeValue);
        }
    }).remove();
}

/* Extend jQuery with functions for PUT and DELETE requests. (http://homework.nwsnet.de/news/9132_put-and-delete-with-jquery */

function _ajax_request(url, data, callback, type, method) {
    if (jQuery.isFunction(data)) {
        callback = data;
        data = {};
    }
    return jQuery.ajax({
        type: method,
        url: url,
        data: data,
        success: callback,
        dataType: type
    });
}
