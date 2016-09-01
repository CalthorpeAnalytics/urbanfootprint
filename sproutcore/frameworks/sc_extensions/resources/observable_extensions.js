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
 * Static methods to add functionality to observable.
 */
SC.ObservableExtensions = SC.Object.create({

    /***
     * Adds an observer to every item of the list of the given propertyPath of observable, in addition
     * to the status of the property value and the property value as a whole. The method can be
     * called if the propertyPath changes which will result in previous observers being removed.
     * You must pass label that the previous propertyPath name is cached at _label. onChangeFuncName
     * is the name of the func on observable to call
     * @param label: A unique label to identify the observations, in case the propertyPath updates
     * @param observable: An observable instance whose propertyPath lead to a collection that needs observing.
     * if propertyPath is not a collection then just the single value and status is observed
     * @param propertyPath: a simple or chained path of the observer to a single or list value. Use * syntax
     * if you need to observe multiple parts of the path. If you use '*[propertyA]@each.[propertyB]'
     * then observers will observe *propertyA.propertyB.[] and *propertyA.@each.propertyB
     * @param target: the instance that contains onChangeFuncName. Normally the same as observable
     * @param onChangeFuncName: the name of the function on target to call if anything changes
     * @param removeOnly: Default false, set true to only remove observers. Use observable when iterating through
     * different observables that are changing
     */
    propertyItemsAndStatusObservation: function(label, observable, propertyPath, target, onChangeFuncName, removeOnly) {
        var previousPropertyPath = observable['_%@'.fmt(label)];
        if (previousPropertyPath) {
            var property = '%@%@'.fmt(previousPropertyPath, previousPropertyPath.indexOf('.')>=0 ? '*': '');
            observable.removeObserver(property, target, onChangeFuncName);
            // TODO shouldn't call for toOne relationships
            // Note that no star is allowed for [] observation of simple properties
            observable.removeObserver('%@.[]'.fmt(property), target, onChangeFuncName);
            // TODO shouldn't call for toOne relationships
            observable.removeObserver('*%@.@each.status'.fmt(propertyPath), target, onChangeFuncName);
            observable.removeObserver('*%@.status'.fmt(propertyPath), target, onChangeFuncName);
        }
        observable['_%@'.fmt(label)] = propertyPath;
        if (removeOnly)
            return;
        if (propertyPath) {
            var property = '%@%@'.fmt(propertyPath, propertyPath.indexOf('.')>=0 ? '*': '');
            observable.addObserver(property, target, onChangeFuncName);
            // TODO shouldn't call for toOne relationships
            // Note that no star is allowed for [] observation of simple properties
            observable.addObserver('%@.[]'.fmt(property), target, onChangeFuncName);
            // TODO shouldn't call for toOne relationships
            observable.addObserver('*%@.@each.status'.fmt(propertyPath), target, onChangeFuncName);
            //observable.addObserver('%@.@each.%@'.fmt(propertyPath), target, onChangeFuncName, some_attr);
            observable.addObserver('*%@.status'.fmt(propertyPath), target, onChangeFuncName);
        }
    },

    /***
     * Just do the remove observer part of propertyItemsAndStatusObservation
     * @param label
     * @param observable
     * @param propertyPath
     * @param target
     * @param onChangeFuncName
     * @param removeOnly
     */
    removePropertyItemsAndStatusObservation: function(label, observable, propertyPath, target, onChangeFuncName, removeOnly) {
        SC.ObservableExtensions.propertyItemsAndStatusObservation(label, observable, propertyPath, target, onChangeFuncName, removeOnly);
    },

    /***
     * Like the propertyItemsAndStatusObservation but takes an array of observables an observes a single
     * item property on each
     * @param label
     * @param observable
     * @param propertyPath
     * @param target
     * @param onChangeFuncName
     * @param removeOnly
     */
    observablesPropertyAndStatusObservation: function(label, observables, propertyPath, target, onChangeFuncName, removeOnly) {
        observables.forEach(function (observable) {
            var previousPropertyPath = observable['_%@'.fmt(label)];
            if (previousPropertyPath) {
                var property = '%@%@'.fmt(previousPropertyPath, previousPropertyPath.indexOf('.') >= 0 ? '*' : '');
                observable.removeObserver(property, target, onChangeFuncName);
                observable.removeObserver('status', target, onChangeFuncName);
            }
            observable['_%@'.fmt(label)] = propertyPath;
            if (removeOnly)
                return;
            if (propertyPath) {
                var property = '%@%@'.fmt(propertyPath, propertyPath.indexOf('.') >= 0 ? '*' : '');
                observable.addObserver(property, target, onChangeFuncName);
                observable.addObserver('status', target, onChangeFuncName);
            }
        });
        // Add check of array membership
        observables.removeObserver('[]', target, onChangeFuncName);
        observables.addObserver('[]', target, onChangeFuncName);
        // Add check of array status
        observables.removeObserver('status', target, onChangeFuncName);
        observables.addObserver('status', target, onChangeFuncName);
    },

    /***
     * Tracks changes in membership to a list and the status of each item and the overall status
     * @param label: Label to make observers unique for removing/adding
     * @param list: The list to track
     * @param target: The target of onChangeFuncName
     * @param onChangeFuncName: The function for all of the observers to call
     * @param removeOnly: Just remove observers, don't add
     */
    itemsAndStatusObservation: function(label, list, target, onChangeFuncName, removeOnly) {
        if (!list)
            return;
        var previousObservers = list['_%@'.fmt(label)];
        if (previousObservers) {
            // Note that no star is allowed for [] observation of simple properties
            list.removeObserver('[]', target, onChangeFuncName);
            list.removeObserver('@each.status', target, onChangeFuncName);
            list.removeObserver('status', target, onChangeFuncName);
        }
        list['_%@'.fmt(label)] = YES;
        if (removeOnly)
            return;
        // Note that no star is allowed for [] observation of simple properties
        list.addObserver('[]', target, onChangeFuncName);
        list.addObserver('@each.status', target, onChangeFuncName);
        list.addObserver('status', target, onChangeFuncName);
    },
});
