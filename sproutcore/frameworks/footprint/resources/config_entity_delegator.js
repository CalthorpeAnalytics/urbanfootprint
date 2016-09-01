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
 * This mixin is the interface to main-config.
 * It resolves the delegate of the configEntity stored in the content property
 */
Footprint.ConfigEntityDelegator = {

    parentConfigEntityDelegator: null,
    /***
     * Resolves the delegate for the current configEntity. This climbs the parent_config_entity tree
     * until it finds a defined delegate. If none are found it returns the default delegate
     */
    configEntityDelegate: function() {
        if (!(this.get('content') && this.get('status') & SC.Record.READY))
            return;
        if (this.getPath('content.schema')) {
            var regionSchema = this.getPath('content.schema').split('__')[0].camelize().capitalize();
            var cls = SC.objectForPropertyPath('Footprint%@.%@Delegate'.fmt(
                regionSchema,
                regionSchema).classify());
            if (cls)
                return cls.create();
        }
        // We didn't find a module for the given schema. Try the parent schema or default if we are already at region scope
        return this.get('parentDelegate');
    }.property('content', 'status').cacheable(),

    parentDelegate: function () {
        var parentConfigEntityDelegator = this.get('parentConfigEntityDelegator');
        // Find the configEntity's parent delegate or the default if none exists
        var delegate = parentConfigEntityDelegator ? parentConfigEntityDelegator.get('configEntityDelegate') : this.get('defaultDelegate');
        if (!delegate)
            throw Error("Delegate in null. This should never happen");
        return delegate;
    }.property('content').cacheable(),

    defaultDelegate: function() {
        return SC.objectForPropertyPath('Footprint.DefaultDelegate').create();
    }.property('content').cacheable()

};
