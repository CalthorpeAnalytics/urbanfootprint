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



Footprint.LineChartView = SC.View.extend({
    childViews: ['chartView'],
    classNames: ['footprint-line-chart-view'],
    content: null,
    scenarios: null,

    columnToLabel: function() {
        return this.getPath('content.configuration.column_to_label');
    }.property('content').cacheable(),

    /***
     * Returns the keys representing the result query columns (a.k.a the aggregate column name)
     * @returns {*}
     * @private
     */
    keys: function() {
        var attributes = this.getPath('content.configuration.attributes');
        var attributeToColumn = this.getPath('content.configuration.attribute_to_column');
        return SC.none(attributeToColumn) ?
            null :
            attributes.map(function (attribute) {
                return attributeToColumn[attribute];
            });

    }.property('content').cacheable(),

    /***
     * The content of this View is a Result. This property returns that Result for every Scenario of scenarios
     * The results include one matching content
     * Results returns a single record nested in an array: [ret]
     */
    results: function() {
        if (!this.get('scenarios')) {
            return null;
        }
        var results = this.get('scenarios').map(function(scenario, i) {

            // Match the ResultPage with the resultLibraryActiveController key.
            var resultPage = scenario.getPath('presentations.results').filter(function(resultPage) {
                return this.get('resultLibraryKey') == resultPage.get('key');
            }, this)[0];

            // Find the Result of the Scenario matching the key of the content Result
            if (!resultPage) {
                return null;
            } else {
                var pageResults = resultPage.get('results');
                var filteredResults = pageResults.filter(function (result) {
                    return result.getPath('dbEntityKey') == this.getPath('content.dbEntityKey');
                }, this);
                if (!filteredResults.length) {
                    return null;
                }
                return filteredResults[0];
            }
        }, this).compact();

        return results;
    }.property('scenarios', 'resultLibraryKey', 'content').cacheable(),

    /***
     * This property returns that data for every scenario
     * Data returns an array of objects, where each object has the data for a single data point on the chart
     * ie data = [ obj, obj, obj ]
     * ie data[1] =  {key: 'pop12', value: 100 ... }
     */
    data: function() {
        var keys = this.get('keys');
        if (!keys || this.getPath('results.length') == 0)
            return null;

        var results = this.get('results');

        if (results.get('length') != 1) {
            SC.warn('Data results > 1. Current chart data does not support this format.');
        }

        var resultRecord = results[0];

        if (!resultRecord) {
            SC.Logger.warn('Missing chart data: ' + results);
            return [];
        }

        // UF-620: For some reason 'query' can be stale or mis-matched
        // with the data that we're actually trying to show: The keys
        // in 'query' will be the wrong ones, like 'pop12__sum', etc,
        // and the keys in 'keys' will be the right ones, like 'hh12',
        // etc.
        var rawResult = resultRecord.get('query')[0];

        // simplify the column names and create a lookup dict to the
        // datum {du__sum:5, emp__sum:6} => {du:5, emp:6} result dict
        // for charts are returned as a single item array from the api
        var result_lookup = $.mapObjectToObject(rawResult,
            function(key, value) {
                // Remove the aggregate part of the column name (e.g. '__sum')
                // Zero out null values so d3 can process
                return  [key.split('__')[0],
                         parseFloat(value || 0)];
            });

        // Create the d3 series of data for the Result. Give each datum a unique id
        // by index in the series. I'm not sure if this can't just be i
        var data = keys.map(function(key, i) {
            return {
                id: i,
                key: key,
                label: this.get('columnToLabel')[key],
                value: result_lookup[key],
            };
        }, this);

        var sum = d3.sum(data, function(d) { return d.value; });

        data.forEach(function (datum) {
            datum.percent = parseFloat(datum.value) / parseFloat(sum);
            return datum;
        });

        return data;
    }.property('results', 'keys', 'columnToLabel').cacheable(),


    chartView: SC.View.extend({
        classNames: ['footprint-line-chart'],
        layout: {top: 20, width: 350, height: 180},
        topSectionIsVisible: null,
        topSectionIsVisibleBinding: SC.Binding.oneWay('Footprint.topSectionVisibleViewController.topSectionIsVisible'),
        displayProperties: ['topSectionIsVisible'],
        data: null,
        dataBinding: SC.Binding.oneWay('.parentView.data'),
        render: function(context) {
            var w = this.getPath('layout.width'),
                h = this.getPath('layout.height');

            // instantiate elements on render to call in update
            context = context.begin('svg')
                .addAttr('width', w)
                .addAttr('height', h)
                    .begin('g')
                    .addClass('main-line-chart-g')
                        .begin('g')
                        .addClass('line')
                            .begin('path')
                            .addClass('linegraph')
                            .end()
                        .end()
                        .begin('g')
                        .addClass('focus')
                            .begin('circle')
                            .addClass('tooltip-circle')
                            .end()
                            .begin('line')
                            .addClass('tooltip-x')
                            .end()
                            .begin('line')
                            .addClass('tooltip-y')
                            .end()
                            .begin('text')
                            .addClass('tooltip-y-shadow')
                            .end()
                            .begin('text')
                            .addClass('tooltip-y-text')
                            .end()
                            .begin('text')
                            .addClass('tooltip-x-shadow')
                            .end()
                            .begin('text')
                            .addClass('tooltip-x-text')
                            .end()
                        .end()
                        .begin('g')
                        .addClass('circles')
                        .end()
                        .begin('rect')
                        .addClass('mouseCapture')
                        .end()
                        .begin('g')
                        .addClass('x-axis')
                        .addClass('axis')
                        .end()
                        .begin('text')
                        .addClass('x-axis-label')
                        .end()
                        .begin('g')
                        .addClass('y-axis')
                        .addClass('axis')
                        .end()
                    .end()
                .end();

        },

        update: function(jqElement) {

            var data = this.get('data');

            if (!data || !data.length) {
                return;
            }

            // UF-620: Sometimes data comes in stale, and value is
            // undefined for all the datapoints.
            var badData = data.filter(function(d) {
                return d.value === undefined;
            });
            if (badData.length) {
                console.warn('Mismatched data for chart: ', data);
                return;
            }

            var transition_time = 1000;

            var yearFromKeyStr, regPatt;

            // add year to the data using regex on key
            for (var i =0; i< data.length; i++) {
                regPatt = /[0-9]{2}$/;
                yearFromKeyStr = regPatt.exec(data[i].key);
                data[i].year = +('20' + yearFromKeyStr);
            }

            var w = this.getPath('layout.width'),
                h = this.getPath('layout.height'),
                margin = {top: 20, bottom: 55, right: 55, left: 55};

            var key = function(d) {
                return d.key;
            };

            // define xscale
            var minYear = d3.min(data, function(d) { return d.year; });
            var maxYear = d3.max(data, function(d) { return d.year; });
            var xScale = d3.scale.linear()
                            .domain([minYear, maxYear])
                            .range([margin.left, w - margin.right]);

            // y axis should always be zero based
            var minValue = 0;
            var maxValue = d3.max(data, function(d) { return d.value; });

            // define yscale
            var yScale = d3.scale.linear()
                            .domain([minValue, maxValue])
                            .range([h - margin.bottom, margin.top]);

            // create main g that contains chart
            var svg = d3.select(jqElement.get(0)).select('g.main-line-chart-g');

            var lineSvg = svg.select('g.line');

            var focus = svg.select('g.focus')
                .style('display', 'none');

            // create line function
            var line = d3.svg.line()
                .x(function(d) { return xScale(d.year); })
                .y(function(d) { return yScale(d.value); });

            // create invisible line
            var path = lineSvg.select('path.linegraph')
                .attr({
                    'd': line(data),
                    'style': 'stroke: darkcyan; stroke-width: 2; fill: none;',
                });

            // get length of line after created
            var lineLen = path.node().getTotalLength();

            // redefine line strokes with line length for animation
            d3.selectAll('.linegraph')
                .attr({
                    'stroke-dasharray': lineLen + ' ' + lineLen,
                    'stroke-dashoffset': lineLen,
                });

            // create circles for datapoints
            var circleG = svg.select('g.circles');

            var circles = circleG.selectAll('.datanode-circle')
                .data(data, key);

            circles.exit().remove();

            circles
                .enter()
                .append('circle')
                .attr('r', 2.5)
                .style('stroke-width', 0)
                .style('fill', 'white');

            circles
                .attr('cx', function(d) {return xScale(d.year); })
                .attr('cy', function(d) {return yScale(d.value); })
                .attr('class', 'datanode-circle')
                .style('fill', 'white')
                .transition()
                // delaying datanode circles so they appear chronologically, not all at once
                // this only works the first time it loads
                .delay(function(d, i) {return i * transition_time / data.length; })
                .duration(transition_time)
                .style('fill', 'darkcyan');

            // create circle to move on mouseover later
            focus.select('circle.tooltip-circle')
                .style('fill', 'none')
                .style('stroke', 'black')
                .attr('r', 4);

            // append the mouseover x line
            focus.select('line.tooltip-x')
                .style('stroke', 'black')
                .style('stroke-dasharray', '3,3')
                .style('opacity', 0.5)
                .attr('y1', 0)
                .attr('y2', h - margin.bottom);

            // append the mouseover y line
            focus.select('line.tooltip-y')
                .style('stroke', 'black')
                .style('stroke-dasharray', '3,3')
                .style('opacity', 0.5)
                .attr('x1', w + margin.left)
                .attr('x2', w);

            // place the value at the intersection
            focus.select('text.tooltip-y-shadow')
                .style('stroke', 'white')
                .style('stroke-width', '3.5px')
                .style('opacity', 0.8)
                .attr('dx', 8)
                .attr('dy', '-.3em');
            focus.select('text.tooltip-y-text')
                .attr('dx', 8)
                .attr('dy', '-.3em');

            // place the year at the intersection
            focus.select('text.tooltip-x-shadow')
                .style('stroke', 'white')
                .style('stroke-width', '3.5px')
                .style('opacity', 0.8)
                .attr('dx', 8)
                .attr('dy', '1em');
            focus.select('text.tooltip-x-text')
                .attr('dx', 8)
                .attr('dy', '1em');

            // append rectangle to capture mouse
            svg.select('rect.mouseCapture')
                .attr('width', w - margin.right)
                .attr('height', h - margin.bottom)
                .style('fill', 'none')
                .style('pointer-events', 'all')
                .on('mouseover', function() { focus.style('display', null); })
                .on('mouseout', function() {focus.style('display', 'none'); })
                .on('mousemove', mousemove);


            // define x axis
            var xAxis = d3.svg.axis()
                .scale(xScale)
                .orient('bottom')
                .tickFormat(d3.format('g')) // format years as a general number
                .ticks(data.length * 2);

            // define y axis
            var yAxis = d3.svg.axis()
                .scale(yScale)
                .orient('left')
                .ticks(4);

            // create x axis
            svg.select('g.x-axis')
                .attr('transform', 'translate(0,' + (h-margin.bottom) + ')')
                .call(xAxis);

            // create x axis label
            svg.select('text.x-axis-label')
                .attr('x', w / 2 )
                .attr('y', h - 20)
                .style('text-anchor', 'middle')
                .text('Year');

            // create y axis
            svg.select('g.y-axis')
                .attr('transform', 'translate(' + margin.left + ',0)')
                .call(yAxis);

            // animate line with dasharray
            d3.selectAll('.linegraph')
                .transition()
                .duration(transition_time * 2)
                .attr('stroke-dashoffset', 0);

            // d3 tooltip tutorial http://www.d3noob.org/2014/07/my-favourite-tooltip-method-for-line.html

            // returns year when given x coordinate; used for tooltip
            var    bisectDate = d3.bisector(function(d) { return d.year; }).left;

            // mousemove tooltip
            function mousemove() {
                var x0 = xScale.invert(d3.mouse(this)[0]),
                    i = bisectDate(data, x0, 1),
                    d0 = data[i-1],
                    d1 = data[i],
                    d = x0 - d0.year > d1.year - x0 ? d1 : d0;


                //TODO re-write so that transform is done on the focus g element
                focus.select(".tooltip-circle")
                    .attr("transform",
                        "translate(" + xScale(d.year) + "," +
                                       yScale(d.value) + ")");

                focus.select(".tooltip-y-shadow")
                    .attr("transform",
                        "translate(" + xScale(d.year) + "," +
                                       yScale(d.value) + ")")
                    .text(d.value);

                focus.select(".tooltip-y-text")
                    .attr("transform",
                        "translate(" + xScale(d.year) + "," +
                                       yScale(d.value) + ")")
                    .style("fill", "#4d4d4d")
                    .text(d3.format(',')(d.value));

                focus.select(".tooltip-x-shadow")
                    .attr("transform",
                        "translate(" + xScale(d.year) + "," +
                                       yScale(d.value) + ")")
                    .text(d.year);

                focus.select(".tooltip-x-text")
                    .attr("transform",
                        "translate(" + xScale(d.year) + "," +
                                       yScale(d.value) + ")")
                    .style("fill", "#4d4d4d")
                    .text(d.year);

                focus.select(".tooltip-x")
                    .attr("transform",
                        "translate(" + xScale(d.year) + "," +
                                       yScale(d.value) + ")")
                    .attr("y2", h - yScale(d.value) - margin.bottom);

                focus.select(".tooltip-y")
                    .attr("transform",
                        "translate(" + w * -1 + "," +
                                       yScale(d.value) + ")")
                    .attr("x2", w + w - margin.right);

            }

            // add styles to line graph
            // for axis ticks
            $('.axis line').attr('style', 'stroke: black; stroke-width: 1; fill: none;');
            // for axis line
            $('.axis path').attr('style', 'stroke: black; stroke-width: 1; fill: none;');
        },
    }),
});
