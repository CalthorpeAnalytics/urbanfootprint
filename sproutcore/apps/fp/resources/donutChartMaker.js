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

d3.edge = {};

d3.edge.donutChart = function module() {

    var colors = {
        "emplAndOffice" : "#72587F",
        "mixedUse" : "#BE1E2D",
        "res" : "#FFA824",
        "civic" : "#1C75BC",
        "parks" : "#009444",
        "streets" : "#E0E0E0",
        "multiFam" : "#C88B3F",
        "townhome" : "#EDBF77",
        "sfSmallLot" : "#FDEE2C",
        "sfLargeLot" : "#FEFAE1",
        "retail" : "#B73771",
        "industrial" : "#EFEAF3"
    }

    // this function is used to determine whether text should be black or white, depending on whether the color of the
    // element it is overlayed upon 'isDark'

    function isDark(color) {
        var rVal = color.substring(1,3);
        var gVal = color.substring(3,5);
        var bVal = color.substring(5,7);

        var grayscale = (parseInt(rVal,16) + parseInt(gVal,16) + parseInt(bVal,16))/3;
        return (grayscale < 150) ? true : false;
    }

    /***
     * @param _selection This is a div (or multiple divs) that will hold the donutChart; this div must be pre-bound with the data
     *  for the chart. Data should be an array of objects, each of which will make up one piece of the "donut"
     *
     *  These objects should be of the form:
     *
        {
           "category" : "Parks",
           "percentage" : 0.90
        }

        the function d3.edge.dataManager is helpful for creating these objects
     */

    function exports(_selection) {
        _selection.each(function(_data){


            var chartWidth = Math.min($(this).height(), $(this).width());
                chartHeight = chartWidth,
                radius = chartHeight / 2,
                outerRadiusPct = .85,
                innerRadiusPct = .65;

            var arcColors = d3.scale.ordinal()
                .domain(
                    ["Mixed-Use", "Residential", "Employment", "Civic", "Parks", "Streets",
                        "Multifamily", "Townhome", "Single Family Small Lot", "Single Family Large Lot",
                        "Retail", "Office", "Industrial"])
                .range([colors.mixedUse, colors.res, colors.emplAndOffice, colors.civic, colors.parks, colors.streets,
                        colors.multiFam, colors.townhome, colors.sfSmallLot, colors.sfLargeLot,
                        colors.retail, colors.emplAndOffice, colors.industrial]);

            var arc = d3.svg.arc()
                .outerRadius(radius*outerRadiusPct)
                .innerRadius(radius*innerRadiusPct);

            // Used to transition the donut chart from one set of data to the next
            function arcTween(a) {
                var i = d3.interpolate(this._current, a);
                this._current = i(0);
                return function(t) {
                    return arc(i(t));
                };
            }
            var pie = d3.layout.pie()
                .value(function(d) { return d.percentage; });

            // If any of the percentages are 0 (or invalid) they should not be used in the construction of the chart, as
            // this will cause errors with the d3 arc
            var nonEmptyData = _data.filter(function(d) {
                if (!isNaN(d.percentage) && d.percentage != 0) {
                    return d;
                }
            });

            var svg = d3.select(this)
                .selectAll("svg")
                .data([nonEmptyData]);

            // By using the "container" for newly entered elements, we don't have to worry about appending new elements to
            // the dom each time we refresh; container is only created on the first time through
            var container = svg.enter().append("svg");

            svg.attr("width",chartWidth)
                .attr("height",chartHeight)
                .classed("chart", true);

            container.append("g").attr("class", "chart_and_legend");
//            svg.selectAll('.chart_and_legend')
//                .data([_data]).enter().append('g');

            var arcs = svg.select(".chart_and_legend")
                .selectAll(".arc")
                .data(pie(nonEmptyData));

            arcs.enter().append("g");
            arcs.attr("class", "arc");

            var chart_and_legend = svg.select(".chart_and_legend");
                chart_and_legend.attr("transform", "translate(" + $(this).width() / 2 + "," + ($(this).height() / 2) + ")");


            arcs.exit().remove();

            arcs.each(function(d, i) {
                var arcPaths = d3.select(this).selectAll("path")
                    .data([d]);
                arcPaths.transition().duration(750).attrTween("d", arcTween);

                arcPaths.enter().append('path')
                    .attr("d", arc)
                    .each(function(d) { this._current = d; });

                arcPaths.style("fill", arcColors(d.data.category));

                // If the percentage is less than two, the sliver of the pie is really too small to label
                // You'll still be able to see the value in the tooltip
                if (d.data.percentage > 0.02 ) {

                    var arcText = d3.select(this).selectAll("text")
                        .data([d]);

                    arcText.enter().append('text');
                    arcText.exit().remove();
                    arcText.attr("transform", function() {
                        var translation = arc.centroid(d);
                        var rotation = (d.endAngle + d.startAngle)/2 * (180/Math.PI);
                        if ((90 < rotation) && (rotation < 270)) {
                            rotation += 180;
                        }
                        return "translate(" + translation + ")" + "rotate(" + rotation + ")";
                    })
                        .attr("dy", ".35em")
                        .style("text-anchor", "middle")
                        .text(function() {
                            perct= d.data.percentage*100;
                            if (perct != 0) {
                                formattedPerct = perct.toFixed(0) + "%";
                            }else {formattedPerct = ""}
                            return formattedPerct; })
                        .style("fill", function() {
                            var arcColor = arcColors(d.data.category);
                            return (isDark(arcColor)) ? "white" : "black";
                        });
                } else {

                    var arcText = d3.select(this).selectAll("text")
                        .remove();

                }

                var arcTooltip = d3.select(this).selectAll("title")
                    .data([d]);

                arcTooltip.enter().append('svg:title');
                arcTooltip
                    .text(function() {
                        perct= d.data.percentage*100;
                        if (perct != 0) {
                            formattedPerct = perct.toFixed(0) + "%";
                        }else {formattedPerct = ""}
                        return d.data.category + ", " + formattedPerct; });

            });

            var lineHeight = chartHeight*.06,
                keyRectSize = lineHeight*.90,
                fontSize = chartHeight*0.05,
                keyRectOffset = keyRectSize/5;

            var maxLegendItemLength = 0,
                numLegendItems = 0;

            var legend = chart_and_legend.selectAll('.legend')
                .data([0]);
            legend.enter().append("g");
            legend.attr("class", "legend");

            var legendItems = legend.selectAll(".legendItems")
                .data(nonEmptyData);

            legendItems.enter().append("g");
            legendItems.exit().remove();
            legendItems.attr("class", "legendItems");

            var doubleLineLabels = 0;

            legendItems.each(function(d, i) {


                $(this).attr("transform", "translate(0, " + (i*lineHeight + doubleLineLabels*lineHeight) + ")");

                var label = d.category;
                var label_length = d.category.length;

                // If the name of the category is longer than 15 characters and is made up of more than 2 words
                // split it into two lines

                var legendText = d3.select(this).selectAll('text')
                    .data([d]);
                legendText.enter().append('text');
                legendText.exit().remove();
                legendText
                    .attr("y",keyRectSize/2)
                    .attr("dy", ".35em")
                    .style("text-anchor","end")
                    .style("font-size", fontSize)
                    .attr("transform, translate(0," + i*lineHeight + ")");


                if (label_length > 15 && label.split(" ").length > 2) {
                    var label_first_half, label_second_half;

                    label_first_half = label.split(" ").slice(0,2).join(" ");
                    label_second_half = label.split(" ").slice(2).join(" ");

                    legendText.text(label_first_half);

                    if(label_first_half.length > maxLegendItemLength) {
                        maxLegendItemLength = label_first_half.length;
                    }

                    var legendTextLine2 = d3.select(this).selectAll('.line2')
                        .data([d]);
                    legendTextLine2.enter().append('text');
                    legendTextLine2
                        .attr("y", keyRectSize*3/2)
                        .attr("dy", ".35em")
                        .style("text-anchor","end")
                        .style("font-size", fontSize)
                        .text(label_second_half);

                    numLegendItems +=2;
                    doubleLineLabels += 1;


                } else {

                    legendText.text(label);

                    if(label_length > maxLegendItemLength) {
                        maxLegendItemLength = label_length;
                    }
                    numLegendItems++;
                }

                var legendKeyRect = d3.select(this).selectAll('rect')
                    .data([d]);
                legendKeyRect.enter().append('rect');
                legendKeyRect
                    .attr("width", keyRectSize)
                    .attr("height", keyRectSize)
                    .attr("x", keyRectOffset)
                    .style("fill",function (d) {
                        return arcColors(d.category);
                    });

                var legendItemTooltip = d3.select(this).selectAll("title")
                    .data([d]);

                legendItemTooltip.enter().append('svg:title');
                legendItemTooltip
                    .text(function() {
                        perct= d.percentage*100;
                        if (perct != 0) {
                            formattedPerct = perct.toFixed(0) + "%";
                        }else {formattedPerct = ""}
                        return d.category + ", " + formattedPerct; });
            });


            var legendHeight = numLegendItems*keyRectSize,
                legendWidth = maxLegendItemLength*5 + keyRectSize;

            legend.attr("transform", "translate(" + (legendWidth - 2*(keyRectSize + keyRectOffset)) / 2 + "," + (-legendHeight / 2) + ")");

        });
    }
    return exports;

};
d3.edge.dataManager = function module() {

    var exports = {};
    exports.createDataObject = function(_category, _percentage) {
        var dataObject = {
           "category" : _category,
           "percentage" : parseFloat(_percentage)
        }
        return dataObject;
    }
    return exports;
};
