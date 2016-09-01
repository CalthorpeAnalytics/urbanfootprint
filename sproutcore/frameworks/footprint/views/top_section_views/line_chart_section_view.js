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


sc_require('views/section_views/section_view');
sc_require('views/top_section_views/line_chart_view');

Footprint.LineChartSectionView = Footprint.SectionView.extend({

    layout: {left:220},

    childViews: ['listView', 'overlayView'],

    autoResizeStyle: SC.RESIZE_AUTOMATIC,

    content: null,
    contentBinding: SC.Binding.oneWay('Footprint.resultsController.content'),

    overlayView: Footprint.OverlayView.extend({
        // activated when the content is busy loading
        contentBinding: SC.Binding.from('.parentView.content'),
        // status is updated when we get new content
        statusBinding:SC.Binding.oneWay('*content.status')
    }),

    listView: SC.ScrollView.extend({
        horizontalAlign: 'left',

        contentView: SC.View.extend({
            classNames: ['result-view'],
            allResults: null,
            allResultsBinding: SC.Binding.oneWay('Footprint.resultsController.content'),
            allResultsStatus: null,
            allResultsStatusBinding: SC.Binding.oneWay('Footprint.resultsController.status'),
            content: function () {
                if (this.get('allResultsStatus') & SC.Record.READY) {
                    return this.get('allResults').filter(function (result) {
                        return result.getPath('configuration.result_type') == 'line_chart';
                    });
                }
            }.property('allResults', 'allResultsStatus').cacheable(),

            // Child views. Match to content & stack.
            childViewLayout: SC.View.HORIZONTAL_STACK,
            contentDidChange: function() {
                // Get the current childViews if any, and destroy them
                var content = this.get('content') || [],
                    previousChildViews = SC.clone(this.get('childViews') || []),
                    childViews = [],
                    exampleView = this.get('exampleView');

                // define variables
                var childContent, child, foundChild, i, j,
                    contentLength = content.get('length'),
                    prevChildViewLength = previousChildViews.get('length');

                // remove and destroy any previous childViews
                for (j=0; j < prevChildViewLength; j++) {
                    child = previousChildViews.objectAt(j);
                    this.removeChild(child);
                    child.destroy();
                }

                // create new child views for each chart
                for (i = 0; i < contentLength; i++) {
                    childContent = content.objectAt(i);
                    foundChild = exampleView.create({ content: childContent });
                    childViews.pushObject(foundChild);
                }

                // Append childViews
                for (i = 0; i < contentLength; i++) {
                    child = childViews.objectAt(i);
                    this.appendChild(child);
                }
            }.observes('content', 'allResultsStatus', 'allResults'),


            /***
             * A 2 Dimensional Bar Chart
             * The 'samples' of the chart are Scenarios
             * The 'series' of the chart are an accumulated result for each Scenario (e.g. dwelling_units, employment, and population)
             * The content of the Example is the Result of the active Scenario. It is used to find the Result of the same key of all Scenarios in the scenarios property
             *
             * Naming conventions:
             * One query column in the series, which has a datapoint per sample, is a 'group'
             * The default presentation is to put the group samples side by side.
             * The alternative presentation is to stack the series of each sample, which is only enabled when the each series result is related (e.g. a series different types of dwelling_units)
             *
             * Example
             * Query columns: du_house__sum, du_apt__sum, du_condo__sum, i.e. the aggregate dwelling units of each housing type
             * Samples: 'smart (a)','trend (b)','dumb (c)'
             * Series: 'sum du house (x)','sum du apt (y)','sum du condo (z)',
             *
             * Grouped Presentation (Default):
             *   x  y
             *   xx y
             *  xxx yyy zzz
             *  ___________
             *  abc abc abc
             *
             *  Note that each series' items are separated and the common series datum of each sample grouped
             *
             * Stacked Presentation
             *
             *     z
             *  z  y  z
             *  y  x  y
             *  y  x  x
             *  x  x  x
             * ________
             *  a  b  c
             *
             *   Note that the series' items are together and the series of each sample are stacked.
             */

            exampleView: SC.View.extend({
                layout: { width: 350, borderRight: 1 },
                classNames: ['results-chart-example-container'],
                childViews: ['labelView', 'chartView'],

                // The Chart title View
                labelView: SC.LabelView.extend({
                    layout: { height: 25 },
                    classNames: ['results-chart-title'],
                    valueBinding: SC.Binding.oneWay('.parentView*content.name')
                }),

                chartView: Footprint.LineChartView.extend({
                    contentBinding: SC.Binding.oneWay('.parentView.content'),
                    resultLibraryKeyBinding: SC.Binding.oneWay('Footprint.resultLibraryActiveController.key'),

                    isStackableBinding:SC.Binding.oneWay('.parentView.isStackable'),
                    isStackedBinding: SC.Binding.from('.parentView.isStacked'),

                    // Used to compare multiple scenarios
                    // TODO this should come from the multiple selected scenarios in the future
                    scenariosBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content').transform(function(value) {
                        return [value];
                    })
                })
            })
        })
    })

});
