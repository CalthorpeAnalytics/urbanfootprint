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
 * Mixin to MapView to apply view controls
 */
Footprint.MapControls = {

    /***
     * Adds a switcher to the map to switch between parcels
     */
    addSwitcher: function() {
        d3.select('#map').insert('div',':first-child').attr('id','layerswitcher');
        po.switcher(map, layers, {title: 'parcel layers'}).container(document.getElementById('layerswitcher'));
    },

    removeBrush: function() {
        d3.selectAll('.brush').remove();
    },

    infoBoxCreate: function() {
        d3.select('#map')
            .insert('div', ':first-child')
            .attr('id', 'identify-popup')
            .style('margin', d3.select('#map').node().clientWidth/2 - 100)
            .append('p')
            .text('ESC')
            .on('click', infoBoxRemove);
    },

    infoBoxRemove: function() {
        d3.selectAll('#identify-popup')
            .remove();
    },

    addToolSelector: function(text, onclick, x)  {
        d3.select('#map')
            .insert('div', ':first-child')
            .classed('tool-selector', true)
            .on('click', onclick)
            .style('margin-left', x)
            .append('p')
            .text(text);
    },

    makePallete: function() {
        d3.select('#map')
            .insert('div', ':first-child')
            .classed('pallete', true);
        for (var bf in builtForms) {
            d3.select('.pallete')
                .append('div')
                .classed('builtformbutton', true)
                .attr('id', bf)
                .style('background-color', builtForms[bf].color)
                .style('margin-left', function() {return w - 100;})
                .on('click', updateBuiltFormWithSelection)
                .append('p')
                .text(bf);
        }
    },

    dblClickFeature: function(f, evt, fields) {
        infoBoxRemove();
        d3.select(f.element).classed('selected', true);
        infoBoxCreate();

        var d = f.data.properties;
        for (var i = 0; i < fields.length; i++) {
            popupText(fields[i], d[fields[i]]);}
    },

    // steps through the items that a user may want to remove, in a sensible order, and removes them one at a time
    clearAll: function() {
        var identifyBox = d3.selectAll('#identify-popup');
        var brushes = d3.selectAll('.brush');
        if (identifyBox[0].length > 0) {identifyBox.remove(); }
        else if (brushes[0].length > 0) { brushes.remove(); }
        else {unselect();}
    }

};
