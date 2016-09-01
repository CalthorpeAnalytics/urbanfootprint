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




Footprint.ChartLegendView = SC.View.extend({

    classNames: ['result-legend-view'],

    keys: null,
    columnToLabel: null,

    didCreateLayer: function () {
        this.notifyPropertyChange('data');
    },

    displayProperties:['data','keys','columnToLabel'],
    /***
     * Create a legend for the graph
     */
    update: function (context) {
        if (!this.get('keys') || !this.get('columnToLabel'))
          return;

        // sets legend margins
        var legendWidth = 78,
            legendSquare = 10,
            legendRowHeight = 15;

        //formats the input data - maps column names to the readable legend names
        var data = this.get('keys').map(function(key) {
                return this.get('columnToLabel')[key];
            }, this).slice();

        // draws legend box
        var legendSvg = d3.selectAll(context).append("svg")
            .attr("width", legendWidth)
            .attr("height", legendRowHeight * data.length)
            .append("g");

        var legend = legendSvg.selectAll("legend")
            .data(data)
            .enter().append("g");

        // draws swatches
        var colorScale = this.getPath('parentView.colorScale');
        legend.append("rect")
            .data(this.getPath('parentView.data'))
            .attr("x", 2)
            .attr("y", function(d, i){ return i *  12;})
            .attr("width", legendSquare)
            .attr("height", legendSquare)
            .style("fill", function(d, i) { return colorScale(i); })
            .style("stroke","#d0dae3")
            .style("stroke-width", "1");

        // writes key names
        legend.append("text")
            .attr("x", legendSquare + 5)
            .attr("y", function(d, i){ return i *  12 + 9;})
            .style("text-anchor", "start")
            .text(function(d) { return d; });
    }
});
