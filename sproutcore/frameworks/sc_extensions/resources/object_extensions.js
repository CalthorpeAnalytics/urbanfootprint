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

/*
SC.clone = SC.copy = function(object, deep, calls) {

    if (calls)
        SC.Logger.debug('Calls %@'.fmt(calls));
    if (object && object._touched_by_clone)
        SC.Logger.debug('Duplicate! %@'.fmt(object));
    if (object)
        object._touched_by_clone = YES;
    if (calls > 100)
        throw Er
    calls = calls || 0
    var ret = object, idx ;

    // fast paths
    if ( object ) {
      if ( object.isCopyable ) return object.copy( deep );
      if ( object.clone )      return object.clone();
    }

    switch ( jQuery.type(object) ) {
    case "array":
      ret = object.slice();

      if ( deep ) {
        idx = ret.length;
        while ( idx-- ) { ret[idx] = SC.copy( ret[idx], true, calls+1 ); }
      }
      break ;

    case "object":
      ret = {} ;
      for(var key in object) {
          if (calls > 10)
              SC.Logger.debug(key);
          ret[key] = deep ? SC.copy(object[key], true, calls+1) : object[key] ;
      }
    }

    return ret ;
}
*/

SC.Object.reopen({
   /**
    * Flat maps chained property paths by calling get on each segment and flat mapping the results of each get and recursing
     * @param propertyPath
    */
   flatMapPropertyPath: function(propertyPath)  {

       var parts = propertyPath.split('.');
       if (parts.length == 0) {
           throw Error("Bad propertyPath: %@ called on object: %@".fmt(propertyPath, this.toString()))
       }
       if (parts.length == 1) {
           return this.get(parts[0])
       }
       else {
           // Turn this into an array
           var objects = this.toArray ? this.toArray() : $.arrayOrSingleItemArray(this);
           return $.map(objects, function(obj) {
               // Get the property of the item
               var item = obj.get(parts[0]);
               var items = item.toArray ? item.toArray() : $.arrayOrSingleItemArray(item);
               return $.map(items, function(item) {
                   return item ? item.flatMapPropertyPath(parts.slice(1).join('')) : null;
               });
           });
       }
   },

   /**
    * Given a Sproutcore object and list of its attributes, returns a dict keyed by attribute and valued by a toString of the attribute value
    * Useful for debugging
    * @param obj
    * @param attributes
    */
    toStringAttributes: function(attributes, attributeMapping) {
        return attributes.map(function(attribute) {
            // Get the attribute primitive to avoid infinite recursion
            var value = this.get('attributes') ? this.get('attributes')[attribute] : this.getPath(attribute);
            var resolvedValue = (typeof(value) == 'function' && !value.prototype) ? value.apply(this) : value;
            // Map the value if a mapping is defined
            var mappedValue = attributeMapping && attributeMapping[attribute] ? attributeMapping[attribute](resolvedValue) : resolvedValue;
            return "--->%@: %@".fmt(attribute, mappedValue ? (mappedValue.toString ? mappedValue.toString() : mappedValue) : null);
        }, this).join("\n");
    },

    validateAttributes: function(attributes) {
        attributes.forEach(function(attribute) {
            var value = this.getPath(attribute);
            var resolvedValue = typeof(value) == 'function' ? value.apply(this) : value;
            if (!resolvedValue) {
                throw "attribute %@ is null or undefined for %@".fmt(attribute, this.toString())
            }
        }, this);
    }
});

Array.prototype.flatMapPropertyPath = function(propertyPath) {
    // If the item that enters is an array, recurse on each item
    return $.map(this, function(item) {
        return item.flatMapPropertyPath(propertyPath)
    });
};

Array.prototype.sortPropertyPath = function(keys, reverse_dict) {

    var len  = keys.length,
        reverse = reverse_dict || {},
        src;

    // get the src array to sortGk
    if (this instanceof Array) src = this;
    else {
      src = [];
      this.forEach(function(i) { src.push(i); });
    }

    if (!src) return [];
    return src.sort(function(a,b) {
      var idx, key, aValue, bValue, ret = 0;

      for(idx=0;ret===0 && idx<len;idx++) {
        key = keys[idx];

        aValue = a ? (a.getPath ? a.getPath(key) : a[key]) : null;
        bValue = b ? (b.getPath ? b.getPath(key) : b[key]) : null;
        ret = reverse[key] ? SC.compare(bValue, aValue) : SC.compare(aValue, bValue);
      }
      return ret ;
    });
};

// Round a number to the nearest number for the given base
Number.prototype.toNearest = function(base) {
    return Math.round(this/base)*base;
};
Number.prototype.toNearestFloor = function(base) {
    return Math.floor(this*base)/base;
};
Number.prototype.toNearestCeiling = function(base) {
    return Math.ceil(this*base)/base;
};
