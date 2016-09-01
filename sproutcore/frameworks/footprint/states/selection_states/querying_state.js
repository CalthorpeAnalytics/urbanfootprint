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

Footprint.QueryingState = SC.State.extend({

    initialSubstate:'readyState',

    queryDidValidate: function(context) {
        // Never send this stuff
        if (Footprint.layerSelectionEditController.getPath('query_strings.group_by_string') ^
            Footprint.layerSelectionEditController.getPath('group_by')) {
            Footprint.logError('Out of sync state of groupby for layerSelection: %@'.fmt(Footprint.layerSelectionEditController.get('content').toString()));
        }

        if (Footprint.layerSelectionEditController.getPath('query_strings.aggregates_string') ^
            Footprint.layerSelectionEditController.getPath('aggregates')
            )
            Footprint.logError('Out of sync state of aggregates for layerSelection: %@'.fmt(Footprint.layerSelectionEditController.get('content').toString()));
        Footprint.statechart.sendAction('doUpdateLayerSelection', SC.ObjectController.create(context));
    },

    queryDidFail: function(context) {
    },
    readyState: SC.State.extend({
        enterState: function(context) {
            if (this.parseQuery(Footprint.layerSelectionEditController)) {
                Footprint.statechart.sendEvent('queryDidValidate', Footprint.layerSelectionEditController);
            } else {
                Footprint.statechart.sendEvent('queryDidFail', Footprint.layerSelectionEditController);
            }
        },

        parseQuery: function(context) {

            // Parse the filter string using our enhanced SCQL
            // TODO prevent empty string weirdness
            if (!context.getPath('query_strings.filter_string'))
                context.setPath('query_strings.filter_string', null);
            var filterString = context.getPath('query_strings.filter_string');
            var filter = null;
            if (filterString) {
                filter = Footprint.processQuery(filterString, 'equation');
                if (filter.error) {
                    SC.AlertPane.warn({
                        message: 'Could not parse query',
                        description: 'Only basic operators are currently available: \'>, <, =\'. You can refer to properties by name. Example: built_form.name = \'Agriculture\'',
                    });
                    return NO;
                }
            }
            Footprint.layerSelectionEditController.set('filter', filter);

            // Parse each comma-separated aggregate in the aggregatesString using our enhanced SCQL
            // TODO prevent empty string weirdness
            if (!context.getPath('query_strings.aggregates_string'))
                context.setPath('query_strings.aggregates_string', null);
            var aggregatesString = context.getPath('query_strings.aggregates_string');
            try {
                Footprint.layerSelectionEditController.set('aggregates', aggregatesString ? aggregatesString.split(',').map(function(aggregate) {
                    // Parse each separate for now, since SCQL can't handle selection strings
                    var aggregateQuery = Footprint.processQuery(aggregate, 'aggregate');
                    if (aggregateQuery.error) {
                        SC.AlertPane.warn({
                            message: 'Could not parse aggregate field',
                            description: 'Only SUM(field), AVG(field), COUNT(field), MAX(field), MIN(field) are currently supported. Multiples may be separated by commas, such as SUM(du), AVG(emp)',
                        });
                        Footprint.statechart.gotoState(this.get('fullPath'), context);
                        throw 'give up';
                    }
                    return aggregateQuery;
                }) : null);

            } catch(e) {
                return NO;
            }

            // Parse the single groupBy string in groupByString using our enhanced SCQL
            if (!context.getPath('query_strings.group_by_string'))
                context.setPath('query_strings.group_by_string', null);
            var groupByString = context.getPath('content.query_strings.group_by_string');
            try {
                Footprint.layerSelectionEditController.set('group_bys', groupByString ? groupByString.split(',').map(function(groupBy) {
                    var groupByQuery = Footprint.processQuery(groupBy);
                    if (groupByQuery.error ) {
                        SC.AlertPane.warn({
                            message: 'Could not parse group by text',
                            description: 'This should be comma-separated properties of the main feature table or that specified by join. Example, land_use_code or built_form.id',
                        });
                        Footprint.statechart.gotoState(this.get('fullPath'), context);
                        throw 'give up';
                    }
                    return groupByQuery;
                }): null);
            } catch(e) {
                return NO;
            }
            return YES;
        },
    }),
});
