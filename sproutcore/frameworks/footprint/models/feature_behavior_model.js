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


Footprint.FeatureBehavior = Footprint.Record.extend({

    // When FeatureBehavior dirties we want its DbEntity to dirty, hence the aggregate: YES
    db_entity: SC.Record.toOne('Footprint.DbEntity', {isMaster: NO, inverse:'feature_behavior', aggregate:YES}),
    behavior: SC.Record.toOne('Footprint.Behavior', {isMaster: YES}),
    intersection: SC.Record.toOne('Footprint.Intersection', {isMaster: YES, inverse:'feature_behavior'}),
    readonly: SC.Record.attr(Boolean),

    _copyProperties: function () {
        return ['behavior'];
    },

    _cloneProperties: function () {
        return ['intersection'];
    },

    /***
     * Defaults the Behavior to 'reference' if nothing is specified in the sourceTemplate
     * @param sourceTemplate: Matches the structure of a FeatureBehavior record or is one.
     * Select values are copied over to create a minimum configuration
     * @private
     */
    _createSetup: function(sourceTemplate) {
        sc_super()
        this.set('behavior', sourceTemplate.get('behavior') || this.get('store').find(SC.Query.local(
                Footprint.Behavior,
                {
                    conditions: "key = 'behavior__reference"
                })).get('firstObject')
        );
    },

    /***
     * Save intersection first since FeatureBehavior references Intersection
     * @returns {string[]}
     * @private
     */
    _saveBeforeProperties: function() {
        return ['intersection']
    },
});
