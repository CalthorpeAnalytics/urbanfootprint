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


Footprint.DevelopmentCharsView = SC.View.extend({
    layout: { top: 0.70,  bottom: 0.05, left: 0.30, right: 0},
    childViews: ['devCharsTableView', 'devCharsTitleView'],
    displayProperties: ['content'],
    classNames: ['devChars'],

    content: null,

    devCharsTitleView: SC.LabelView.design({
        layout: { centerX: 0, width: 250, height: 20 },
        classNames: ['sectionTitle'],
        textAlign: SC.ALIGN_CENTER,
        tagName: "h1",
        value: "Development Characteristics"
    }),

    devCharsTableView: SC.View.design({
        layout: { top: 20, bottom: 0, width: 0.95, left: 0.025, right: 0.025},
        classNames: ['devCharsTable'],

        displayProperties: ['content'],
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),

        tableData: function() {

            var gross_residential_density = parseFloat(this.getPath('content.dwelling_unit_density')).toFixed(2),
                net_residential_density = (parseFloat(this.getPath('content.dwelling_unit_density'))/parseFloat(this.getPath('content.net_developable_land'))).toFixed(2),
                gross_pop_density = parseFloat(this.getPath('content.population_density')).toFixed(2),
                net_pop_density = (parseFloat(this.getPath('content.population_density'))/parseFloat(this.getPath('content.net_developable_land'))).toFixed(2),
                gross_jobs_density = parseFloat(this.getPath('content.employment_density')).toFixed(2),
                net_jobs_density = (parseFloat(this.getPath('content.employment_density'))/(this.getPath('content.net_developable_land'))).toFixed(2),
                street_pattern = this.getPath('content.street_pattern'),
                intersection_density = parseInt(this.getPath('content.intersections_sqmi')),
//                block_size_avg_acres = parseFloat(this.getPath('content.block_size_avg_acres')).toFixed(2),
                jobs_pop_ratio = (parseFloat(this.getPath('content.employment_density'))/parseFloat(this.getPath('content.population_density'))).toFixed(2);

            return developmentCharacteristics = [
                {
                    key: "built_form",
                    label: "Built form",

                    values: [
                        {
                            key: 'street_pattern',
                            label: "Street Pattern",
                            value: street_pattern
                        },
                        {
                            key: 'intersection_density',
                            label: "Intersection Density",
                            value: intersection_density + "/sq mile"
                        },
                        {
                            key : 'avg_block_size',
                            label: "Average Block Size",
                            value: "xxac"
                        },
                        {
                            key : 'avg_building_height',
                            label: "Average Building Height",
                            value: "xxx"
                        }
                    ]
                },
                {
                    key: "residential",
                    label: "Residential",

                    values: [
                        {
                            key: 'gross_res_density',
                            label: 'Gross Residential Density',
                            value: gross_residential_density + ' du/ac'
                        },
                        {
                            key: 'net_res_density',
                            label: 'Net Residential Density',
                            value: net_residential_density + ' du/ac'
                        },
                        {
                            key: 'gross_res_FAR',
                            label: 'Gross Residential FAR',
                            value: 'xx'
                        },
                        {
                            key: 'net_res_FAR',
                            label: 'Net Residential FAR',
                            value: 'xx'
                        },
                        {
                            key: 'gross_pop_density',
                            label: 'Gross Population Density',
                            value: gross_pop_density + ' du/ac'
                        },
                        {
                            key: 'net_pop_density',
                            label: 'Net Population Density',
                            value: net_pop_density + ' du/ac'
                        }
                    ]
                },
                {
                    key: 'employment',
                    label: 'Employment',

                    values: [
                        {
                            key: 'gross_jobs_density',
                            label: 'Gross Jobs Density',
                            value: gross_jobs_density + ' du/ac'
                        },
                        {
                            key: 'net_jobs_density',
                            label: 'Net Jobs Density',
                            value: net_jobs_density + ' du/ac'
                        },
                        {
                            key: 'gross_comm_FAR',
                            label: 'Gross Commercial FAR',
                            value: 'xx'
                        },
                        {
                            key: 'net_comm_FAR',
                            label: 'Net Commercial FAR',
                            value: 'xx'
                        },
                        {
                            key: 'job_pop_ratio',
                            label: 'Jobs/Population Ratio',
                            value: jobs_pop_ratio
                        }
                    ]
                }
            ];
        }.property('content').cacheable(),

        render: function(context) {
            sc_super();
        },


        update: function(context) {

            if (this.getPath('content.status') & SC.Record.READY) {
                var developmentCharacteristics = this.get('tableData');


                // Very important to always do a selectAll, data, enter, and append for the first element you add to the dom
                // this way, each time you update, you aren't appending a new element, but rather you are replacing the data in the existing one
                var table = d3.selectAll(context)
                    .selectAll(".outerTable")
                    .data([0]);
                // Container is only added in the first pass, when enter() contains data
                var container = table.enter().append("table")
                    .attr("class", "outerTable");

                container
                    .append("tbody")
                    .append("tr")
                    .attr("class","rowForInnerTables");

                var rowForInnerTables = table.select(".rowForInnerTables");
                rowForInnerTables
                    .selectAll(".tdForInnerTable")
                    .data(developmentCharacteristics)
                    .enter().append("td")
                    .attr("class", "tdForInnerTable")
                    .attr("valign","top");


                var tdForInnerTables = table.selectAll(".tdForInnerTable");

                tdForInnerTables.each(function(d) {
                    d3.select(this).selectAll("table")
                        .data([0])
                        .enter().append("table")
                        .attr("class","innerTable");

                    var innerTable = d3.select(this).selectAll(".innerTable");

                    var innerHead = innerTable.selectAll("thead")
                        .data([0]).enter().append("thead");
                    innerHead.append("tr")
                        .append("th")
                        .text(d.label);

                    innerTable.selectAll("tbody")
                        .data([0])
                        .enter().append("tbody")
                        .attr("class", "innerBody");

                    var innerBody = innerTable.selectAll(".innerBody");

                    innerBody.selectAll("tr")
                        .data(d.values)
                        .enter().append("tr")
                        .attr("class", "innerRow");

                    var innerRows = innerBody.selectAll(".innerRow");

                    innerRows.each(function(d, i){
                        var label = d3.select(this).selectAll(".label")
                            .data([d]);
                        label.enter().append("td")
                            .attr("class", "label")
                            .attr("title", d.value);
                        label.text(d.label);

                        var value = d3.select(this).selectAll(".value")
                            .data([d]);
                        value.enter().append("td")
                            .attr("class", "value");
                        value.text(d.value);
                    });
                })
            }
        }
    })
});
