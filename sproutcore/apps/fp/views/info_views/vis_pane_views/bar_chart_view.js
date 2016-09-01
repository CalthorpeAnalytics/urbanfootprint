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


Footprint.BarChartView = SC.View.extend({
    layout: { top: 0.06, left: 0.35, right: 0.05, height: 0.20},
    classNames: ['barChart'],
    displayProperties: ['content'],

    content: null,

    color: null,
    colorBinding: SC.Binding.oneWay('.parentView.color'),

    backgroundColor: null,
    backgroundColorBinding: SC.Binding.oneWay('.parentView.color'),

    classNameBindings: ['hasLightBackground'],

    //this class is assigned when the background color is light enough that the text on top should be black
    // isLightColor uses the color code to make the light/dark determination
    hasLightBackground: function(){

        if (this.get('color')) {
            return isLightColor(this.get('color'));
        }

    }.property('color').cacheable(),

    pt_score: function() {
        return this.getPath('content.pt_score');
    }.property('content').cacheable(),

    // one piece of data for each of the bars in graph
    barData: function() {
        return barData = [
            { "title": "Density",
                "score" : this.getPath('content.pt_density') },
            { "title" : "Connectivity",
                "score" : this.getPath('content.pt_connectivity') },
            { "title" : "Mix of Use",
                "score" : this.getPath('content.pt_land_use_mix') }
        ];
    }.property('content').cacheable(),

    render: function(context) {
        sc_super();
    },

    update: function(context) {

        if (this.getPath('content.status') & SC.Record.READY) {

            var _data = this.get('barData');

            var svgWidth = this.getPath('frame.width'),
                svgHeight = this.getPath('frame.height'),
                chartW = svgWidth*0.6,
                chartH = svgHeight*0.6,
                labelWidth = chartW*3/10;

            // Expects that the placetype score will be a value between 0 and 10
            var xScale = d3.scale.linear()
                .domain([0, 10])
                .range([0, chartW]);

            var yScale = d3.scale.ordinal()
                .domain(_data.map(function (d) {return d.title; }))
                .rangeRoundBands([0, chartH]);

            var xAxis = d3.svg.axis()
                .scale(xScale)
                .orient("bottom");

            var yAxis = d3.svg.axis()
                .scale(yScale)
                .orient("left");

            var svg = d3.selectAll(context)
                .selectAll("svg")
                .data([_data]);

            var container = svg.enter().append("svg")
                .attr("width", svgWidth)
                .attr("height", svgHeight)
                .append("g").classed("container-group", true);

            container.append("g").attr("class", "chart-background");
            container.append("g").attr("class", "chart-group");
            container.append("g").attr("class", "y-axis");
            container.append("g").attr("class", "x-axis");
            container.append("g").attr("id","score");

            var barGradient = container.append("linearGradient")
                .attr("x1", 0)
                .attr("x2", xScale(10))
                .attr("id", "barGradient")
                .attr("gradientUnits", "userSpaceOnUse");

            barGradient.append("stop")
                .attr("offset", "0")
                .attr("stop-color", "#4169E1");

            barGradient.append("stop")
                .attr("offset", "0.5")
                .attr("stop-color", "#162252");

            var backgroundGradient = container.append("linearGradient")
                .attr("x1", 0)
                .attr("x2", xScale(10))
                .attr("id", "backgroundGradient")
                .attr("gradientUnits", "userSpaceOnUse");

            backgroundGradient
                .append("stop")
                .attr("offset", "0")
                .attr("stop-opacity", "0.5")
                .attr("stop-color", "#FFFFFF");

            backgroundGradient
                .append("stop")
                .attr("offset", "0.5")
                .attr("stop-color", "#FFFFFF")
                .attr("stop-opacity", "0");

            container.select(".chart-background")
                .append("rect")
                .attr('width', xScale(10))
                .attr('height', chartH)
                .attr('fill', "url(#backgroundGradient)");

            var bars = svg.select(".chart-group")
                .selectAll(".bar")
                .data(_data);
            bars.enter().append("g");
            bars.attr("class","bar");

            bars.each(function(d, i) {
                var barRects = d3.select(this).selectAll('rect')
                    .data([d]);

                barRects.transition()
                    .duration(500)
                    .ease("linear")
                    .attr('y', function(d) { return yScale(d.title); })
                    .attr('x', 0)
                    .attr('width', function(d) { return xScale(d.score); })
                    .attr('height', yScale.rangeBand())
                    .attr('fill', "url(#barGradient)");


                barRects.enter().append('rect')
                .attr('y', function(d) { return yScale(d.title); })
                .attr('x', 0)
                .attr('width', function(d) { return xScale(d.score); })
                .attr('height', yScale.rangeBand())
                .attr('fill', "url(#barGradient)");

//            barRects.transition()
//                .duration(500)
//                .ease("linear")
//                .attr('y', function(d) { return yScale(d.title); })
//                .attr('x', 0)
//                .attr('width', function(d) { return xScale(d.score); })
//                .attr('height', yScale.rangeBand())
//                .attr('fill', "url(#barGradient)");

                var barNumber = d3.select(this).selectAll('text')
                    .data([d]);
                barNumber.enter().append('text');

                barNumber.attr('y', function(d) { return yScale(d.title) + yScale.rangeBand()/2; })
                    .attr('x', function(d) { return xScale(d.score); })
                    .attr('dy', "0.35em") //vertical-align middle
                    .attr('dx', "-1em")
                    .attr('text-anchor', 'end')
                    .style('fill', 'white');
                barNumber.text(function(d) {
                    if (d.score != 0) {
                        return d.score;
                    }else return "";});
            });

            container.select(".x-axis")
                .attr("stroke-width", 1)
                .attr("transform", "translate(0," + chartH + ")")
                .call(xAxis);

            container.select(".x-axis path")
                .attr("display", "none");

            container.select(".y-axis")
                .attr("transform", "translate(0, 0)")
                .call(yAxis);

            container.select(".y-axis path")
                .attr("display", "none");

            var scoreBox = container.select("#score")

            var scoreBoxRect = d3.select("#score").selectAll("#scoreBoxRect")
                .data([0])
            scoreBoxRect.enter().append("rect")
                .attr("title", "Some info about PT score")
                .attr("id", "scoreBoxRect");
            scoreBoxRect.attr("x", xScale(10))
                .attr("y", 0)
                .attr("width", chartH)
                .attr("height", chartH)
                .attr("stroke-width", 3)
                .attr("fill-opacity", 0)
                .attr("stroke", function() {
                    return (context.hasClass('has-light-background'))  ? 'black' : 'white';
                });

            var scoreBoxNum = d3.select("#score").selectAll("#number")
                .data([0])
            scoreBoxNum.enter().append("text")
                .attr("id", "number");

            scoreBoxNum.text(this.get('pt_score'))
                .attr("fill", function() {
                    return (context.hasClass('has-light-background'))  ? 'black' : 'white';
                })
                .attr("dy", ".35em") //vertical-align middle
                .style("font-size", function() { return chartH*.75; })
                .attr("text-anchor", "middle")
                .attr("x", xScale(10) + chartH/2)
                .attr("y", chartH/2);

            var scoreBoxText = d3.select("#score").selectAll("#scoreBoxText")
                .data([0])
            scoreBoxText.enter().append("text")
                .attr("id", "scoreBoxText")
            scoreBoxText.text("PT SCORE")
                .attr("fill", function() {
                    return (context.hasClass('has-light-background'))  ? 'black' : 'white';
                })
                .attr("id", "scoreBoxText")
                .attr("text-anchor", "middle")
                .attr("x", xScale(10) + chartH/2)
                .attr("y", -3);

            //                var horizontalShift = labelWidth + ($(this).width() - )
            container.attr("transform", "translate(" + (labelWidth*1.1) + "," + chartH *0.2 + ")");
        }
    },
    sidewaysBarChart: function module() {

        function exports(_selection) {
            _selection.each(function(_data) {

            });
        }
        return exports;
    }
});
