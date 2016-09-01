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



SC.mixin(SC.Binding, {
    /**
     Creates one or more one way bindings to the parentView

     @param {Array} [properties] The properties of the parent to bind.
     These should be specified as simple strings, (e.g. 'content').
     The property need not already exist on to the child.
     @returns [SC.Binding] Returns the bindings. These are processed
     by Footprint.View (or any other view implementing the same functionality),
     which adds a property to the view if needed, and then calls
        binding.to(property, this).connect()
     where property is extracted from the fromPath (.parentView.property)
     */
    parentOneWayBindings: function (properties) {
        return properties.map(function(property) {
            var fromPath = '.parentView.%@'.fmt(property);
            // beget if needed.
            var binding = this.from(fromPath);
            if (binding === SC.Binding) binding = binding.beget();
            binding._oneWay = YES;
            return binding;
        }, this);
    }
});

SC.Binding.oneWaySelectionSetSingleFilter = function() {
    return this.transform(function(value, isForward) {
        if (isForward) {
            // The selection has changed, get the first item
            // The _objects property doesn't exist until there is a selection.
            if (value)
                return value._objects ? value._objects[0] : null;
            else
                return value;
        }
    })
};

SC.Binding.singleFilter = function() {
    return this.transform(function(value, isForward) {
        if (isForward) {
            // The selection has changed, get the first item
            // The _objects property doesn't exist until there is a selection.
            if (value)
                return value.firstObject ? value.firstObject() : value[0];
            else
                return value;
        }
    })
};

/***
 * Returns the (status & value) == status, meaning value is a sub-status of status,
 * like READY_CLEAN to READY
 * @param status
 * @returns {SC.Binding}
 */
SC.Binding.matchesStatus = function(status) {
    return this.transform(function(value, isForward) {
        return !!(value && (value & status) == status);
    });
};

SC.Binding.equalsStatus = function(status) {
    return this.transform(function(value, isForward) {
        return value && (value === status);
    });
};

SC.Binding.newOrDirtyStatus = function() {
    return this.transform(function(value, isForward) {
        return !!(value && [SC.Record.READY_NEW, SC.Record.READY_DIRTY].contains(value));
    });
};
/***
 * Just test for equality with the given value. This can match on null or undefined if desired,
 * although it's probably better to use not() or something for that
 * @param someValue: A static value to test against the current bound value
 * @returns {*|SC.Binding}
 */
SC.Binding.equalsValue = function(someValue) {
    return this.transform(function(value, isForward) {
        return value === someValue;
    });
};

/***
 * Binding that returns true if any of the status are matched by value
 * @param all arguments are used as status
 * @returns {*|SC.Binding}
 */
SC.Binding.equalsStatuses = function() {
    var statuses = Array.prototype.slice.call(arguments);
    return this.transform(function(value, isForward) {
        return !!(value && statuses.contains(value));
    });
};


SC.Binding.allMatchStatus = function(status) {
    return this.transform(function(content, isForward) {
        return (content || []).filter(function(item) {
            return (!(item && (item.get('status') & status)))
        }).get('length') == 0
    });
};

SC.Binding.lengthOf = function() {
    return this.transform(function(value, binding) {
        return value ? arrayOrItemToArray(value).length : 0;
    });
};

SC.Binding.isGreaterThan = function (minValue) {
    return this.transform(function (value, binding) {
        return (SC.typeOf(value) === SC.T_NUMBER) && (value > minValue);
    });
};

SC.Binding.allowIfKindOf = function(type) {
    /***
     * Returns the value if it matches type. Otherwise returns null or undefined
     */
    return this.transform(function(value, binding) {
        return value && value.kindOf && value.kindOf(type) ? value : (value === undefined ? value:  null);
    });
};

SC.Binding.isKindOf = function(type) {
    /***
     * Returns true if the value is kindOf type
     */
    return this.transform(function(value, binding) {
        return value && value.kindOf(type);
    });
};

SC.Binding.notContentKind = function(type) {
    /***
     * Returns true if the value is not a kindOf the type
     */
    return this.transform(function(value, binding) {
        return !(value && value.kindOf(type));
    });
};

SC.Binding.notZero = function (fromPath, placeholder) {
    if (placeholder === undefined) placeholder = SC.EMPTY_PLACEHOLDER;
    return this.from(fromPath).transform(function (value, isForward) {
        if (!value || value==0) {
            value = placeholder;
        }
        return value;
    });
};

/***
 * Compensates for ManyArray's absent status by converting the ManyArray to a RecordArray by querying on the storeKeys.
 * The recordType is induced from the first item of value.
 * @returns The RecordArray matching the ManyArray items.
 */
SC.Binding.convertToRecordArray = function() {
    return this.transform(function(value, binding) {
        if (!value)
            return value;

        var recordType = Footprint.store.recordTypeFor(value.getPath('firstObject.storeKey'));

        return Footprint.store.find(SC.Query.local(
            recordType || SC.Record, {
                conditions: '{storeKeys} CONTAINS storeKey',
                storeKeys:value.mapProperty('storeKey')
            }));
    });
};

SC.Binding.defaultValue = function(defaultValue) {
    return this.transform(function(value, binding) {
        return value || defaultValue;
    });
};

/*** Transforms a Footprint.BuildingUsePercent array to the BuildingUsePercent property value whose BuildingUseDefinition name matches the given category ***/
SC.Binding.propertyTransform = function(property) {
    return this.transform(function(obj) {
        return obj && obj.getPath(property);
    });
};
/*** Transforms the given list to true if it contains the given value ***/
SC.Binding.contains = function(value) {
    return this.transform(function(list) {
        return list && list.contains(value)
    })
};
/*** Transforms the given value to true if it equals this value ***/
SC.Binding.valueEquals = function(value) {
    return this.transform(function(boundValue) {
        return boundValue == value;
    })
};
/*** Transforms the given value by multiplying by the given fraction ***/
SC.Binding.percentage = function(fraction) {
    return this.transform(function(boundValue) {
        return (boundValue || 0) * fraction;
    })
};

/***
 * Transforms the given current value false if it is equal to the value specified here. Otherwise tranforms to true
 * @param value
 * @returns {SC.Binding}
 */
SC.Binding.notEqual = function(value) {
    return this.transform(function(val) {
        return val && val !== value
    })
}

/***
 * Calls dump on all bindings of the given SC.Object
 * @param obj
 * @param valueTypeOnly. Default true. If a bound value exists, just show the type, not the toString
 * @returns {string}
 */
SC.Binding.dumpAll = function(obj, valueTypeOnly) {
    return (obj.bindings || []).map(function(b) {
        return SC.Binding.dump(b, valueTypeOnly, 1);
    }, this).join('\n\n');
}

/***
 * Recursively dump the binding source as long as the source's property also has a binding to a higher source
 * @param b: The Binding
 * @param _level: For internal use only
 * @returns {string}
 */
SC.Binding.dump = function(b, valueTypeOnly, _level) {
    if (!b) {
        SC.warn("binding is null or undefined");
        return;
    }
    valueTypeOnly = (valueTypeOnly === undefined || !valueTypeOnly) ? true : valueTypeOnly;
    _level = _level || 1;
    if (!b._fromTarget)
        return ['Error, from target with path %@ is undefined'.fmt(
            b._fromObserverData ? b._fromObserverData[0] : 'N/A')];
    var fromBinding = b._fromTarget['%@Binding'.fmt(b._fromPropertyKey)];
    var recursiveResults = fromBinding ? this.dump(fromBinding, valueTypeOnly, _level+1) : [];
    var results = recursiveResults.concat([
        '%@: %@ values:%@->%@'.fmt(
            b._fromTarget.get('layerId'),
            b.toString(),
            ifExternalCond(
                valueTypeOnly,
                b._fromTarget.get(b._fromPropertyKey),
                function(obj) { return obj ? obj.constructor.toString() : 'null'},
                identityFunction),
            ifExternalCond(
                valueTypeOnly,
                b._toTarget.getPath(b._toPropertyPath),
                function(obj) { return obj ? obj.constructor.toString(): 'null'},
                identityFunction)
        )
    ]);
    if (_level==1) {
        // Dump all the results, starting with the deepest one. Add a new line and increasing tabs
        // This makes
        // DeepestSourceBinding value: x
        //      ⤷ DeeperSourceBinding value: x
        //          ⤷ SourceBinding value: x
        return results.map(function(result, index) {
            return '%@%@'.fmt(
                index > 0 ? '\n%@\u2937 '.fmt(Array(index+2).join('\t')) : '',
                result
            );
        })
    }
    return results;
}
