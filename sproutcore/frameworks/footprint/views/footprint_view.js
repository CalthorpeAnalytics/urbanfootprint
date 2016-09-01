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
 *  Adds useful view inheritance properties, such as parentOneWayBindings and parentFromBindings,
 *  so that the user doesn't have declare and bind every property needed from the parentView.
 *  Example:
 *      parentOneWayBindings: ['content', 'recordType'],
 *      parentFromBindings: ['selection']
 *
 *  Properties listed will be created if they don't exist and a binding to the parentiew
 *  will be created on init.
 */
Footprint.View = SC.View.extend({

    /***
     * List of properties of the parentView that should be created (if needed) and bound in this view
     * to the parent oneWay. If a property is undefined on the parentView, an exception is raised.
     */
    parentOneWayBindings: null,
    /***
     * List of properties of the parentView that should be created (if needed) and bound in this view
     * to the parent two-way. If a property is undefined on the parentView, an exception is raised.
     */
    parentFromBindings: null,

    /***
     * Applies the parent bindings upon instantiation of the view instance.
     * TODO It should be possible to this on creation of the view class instead (i.e. on extend)
     */
    init: function () {
        // This has to happen before the super init because createChildViews is called by super,
        // which calls their init
        this.applyParentBindings();
        sc_super();
    },

    /***
     * Applies the bindings specified in parentOneWayBindings and parentFromBindings.
     * Properties on this view are first created if needed. If the parent property
     * is undefined, an exception is thrown
     */
    applyParentBindings: function() {
        var errors = [];
        if (this.parentOneWayBindings) {
            this.parentOneWayBindings.forEach(function(bindingProperty) {
                var path = 'parentView.%@'.fmt(bindingProperty);
                var dottedPath = '.%@'.fmt(path);
                if (this.getPath(path) === undefined)
                    errors.push("Cannot one-way bind view to undefined property path: %@".fmt(dottedPath));
                else {
                    // Create the property if this view doesn't define it
                    if (this.get(bindingProperty) === undefined)
                        this[bindingProperty] = null;
                    SC.Binding.oneWay(dottedPath)
                        .to(bindingProperty, this)
                        .connect();
                }
            }, this);
        }

        if (this.parentFromBindings) {
            this.parentFromBindings.forEach(function(bindingProperty) {
                var path = 'parentView.%@'.fmt(bindingProperty);
                var dottedPath = '.%@'.fmt(path);
                if (this.getPath(path) === undefined)
                    errors.push("Cannot two-way bind view to undefined property path: %@".fmt(dottedPath));
                else {
                    // Create the property if this view doesn't define it
                    if (this.get(bindingProperty) === undefined)
                        this[bindingProperty] = null;
                    SC.Binding.from(dottedPath)
                        .to(bindingProperty, this)
                        .connect();
                }
            }, this);
        }

        if (errors.get('length')) {
            throw Error("The following binding error(s) occurred for view %@ of view hierarchy %@:\n%@".fmt(
                this.constructor,
                dumpParentViews(this),
                errors.join('\n')))
        }
    }
});
