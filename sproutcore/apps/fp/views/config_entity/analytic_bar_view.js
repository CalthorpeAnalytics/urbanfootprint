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


Footprint.AnalyticBarView = SC.View.extend({
    childViews:'barView labelView'.w(),
    layout: { height:20 }, // Sensible default
    classNames: "footprint-analytic-bar-view".w(),

    /**
     * The specific Result to use for this bar. If not specified the first result with configuration.result_type=='analytic_bars' will be used
     */
    dbEntityKey:null,

    /**
     * The specific query attribute key of the Result to show
     */
    queryAttributeKey:null,

    /***
     * The configEntity from which we get the results
     */
    configEntity:null,
    configEntityStatus:null,
    configEntityStatusBinding: SC.Binding.oneWay('*configEntity.status'),
    presentations:null,
    presentationsBinding:SC.Binding.oneWay('*configEntity.presentations.results'),
    presentationsStatus:null,
    presentationsStatusBinding:SC.Binding.oneWay('*presentations.status'),
    /**
     * The Results of a LayerLibrary instance. This is bound to the resultsController content
     */
    content:function() {
        if (this.get('presentations') && (this.getPath('presentationsStatus') & SC.Record.READY)) {
            var libraries =  this.get('presentations').filter(function(presentation, i) {
                return presentation.get('key') == 'result_library__default';
            }, this);
            if (libraries.get('length') > 0) {
                return libraries[0].get('results');
            }
            else {
                // A bad clone or something means the config_entity doesn't have the default result library
                logWarning("No default result library found for config_entity: %@".fmt(this.getPath('config_entity.name')))
            }
        }
    }.property('presentations', 'presentationsStatus').cacheable(),
    contentStatus: null,
    contentStatusBinding: SC.Binding.oneWay('*content.status'),

    /***
     * The result matching the dbEntityKey
     */
    result: function() {
        // Find the Result matching dbEntityKey or the first result of result_type 'analytic_bars'
        if (this.get('content') && this.get('contentStatus') & SC.Record.READY)
            return this.get('content').filter(function(result) {
                return this.get('dbEntityKey') ?
                    result.getPath('db_entity.key') == this.get('dbEntityKey') :
                    result.getPath('configuration.result_type') == 'analytic_bars';

            }, this)[0];
    }.property('content', 'contentStatus', 'dbEntityKey').cacheable(),
    resultStatus:null,
    resultStatusBinding:SC.Binding.oneWay('*result.status'),

    overallMinimum:null,
    overallMaximum:null,

    /***
     * The minimum value of the bar
     */
    minimum:function() {
        if (this.get('value')) {
            var num = Math.round(this.get('value') || 0);
            var digits = num.toString().length-1;
            return Math.pow(10,digits);
        }
        if (this.getPath('result.status') & SC.Record.READY)
            return this.getPath('result.configuration.extent_lookup.%@.min'.fmt(this.get('queryAttributeKey')));
    }.property('result', 'resultStatus', 'queryAttributeKey', 'value').cacheable(),

    /***
     * The maximum value of the bar
     */
    maximum:function() {
        if (this.get('value')) {
            var num = Math.round(this.get('value') || 0);
            var digits = num.toString().length-1;
            return Math.pow(10,digits+1);
        }
        if (this.getPath('result.status') & SC.Record.READY)
            return this.getPath('result.configuration.extent_lookup.%@.max'.fmt(this.get('queryAttributeKey')));
    }.property('result', 'resultStatus', 'queryAttributeKey', 'value').cacheable(),

    /***
     * Returns a dict that maps result query column names to generalized attributes. This allows the table columns
     * to have non-standard names, but our SC attributes/properties can be standardized
     * (e.g. dwelling_units:households__sum)
     * @returns {*}
     * @private
    */
    attributeToColumn: function() {
        if (this.get('resultStatus') & SC.Record.READY)
            return this.getPath('result.configuration.attribute_to_column');
    }.property('result', 'resultStatus').cacheable(),

    dbColumn:function() {
        if (this.get('attributeToColumn') && this.get('queryAttributeKey'))
            return this.get('attributeToColumn')[this.get('queryAttributeKey')]
    }.property('attributeToColumn', 'queryAttributeKey').cacheable(),

    queryLookup:function() {
        if (this.get('result') && (this.get('resultStatus') & SC.Record.READY))
            return $.mapObjectToObject(
                this.getPath('result.query'),
                function(key, value) {
                    // Remove the __sum or part so we match our attribute
                    return [key.split('__')[0], value]
                });
    }.property('result', 'resultStatus').cacheable(),

    /***
     * The value of the query attribute based on the queryAttributeKey
     */
    value: function() {
        if (this.get('queryLookup') && this.get('dbColumn'))
            var num = this.get('queryLookup')[this.get('dbColumn')];
            try {
                return Number(num);
            }
            catch(Error) {
                return null;
            }
    }.property('queryLookup', 'dbColumn').cacheable(),

    barView: SC.ProgressView.extend({
        // Normalizing this because setting maximum and minimum doesn't seem to work
        min:null,
        minBinding:SC.Binding.oneWay('.parentView.minimum'),
        max:null,
        maxBinding:SC.Binding.oneWay('.parentView.maximum'),
        val:null,
        valBinding:SC.Binding.oneWay('.parentView.value'),
        value: function() {
            return this.get('val') ? this.get('val') / (this.get('max') - this.get('min')) : 0;
        }.property('minimum', 'maximum', 'val').cacheable()
    }),

    labelView: SC.LabelView.extend({
        displayValue:null,
        displayValueBinding:SC.Binding.oneWay('.parentView.value'),
        value: function() {
            var value = this.get('displayValue');
            return value ? d3.format(',f')(value) : 'N/A';
        }.property('displayValue').cacheable()
    }),

    toString: function() {
        return this.toStringAttributes('minimum maximum configEntity content dbEntityKey queryAttributeKey result value attributeToColumn'.w());
    }
});
