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

sc_require('views/top_section_views/line_chart_section_view');
sc_require('views/section_toolbars/scenario_toolbar_view');

Footprint.DataManagementTopSectionView =  SC.View.extend({

    layoutDirection: SC.LAYOUT_HORIZONTAL,
    childViews: ['scenarioInformationView'],
    content: null,
    selection: null,

    scenarioInformationView: Footprint.View.extend({
        childViews: ['metadataView', 'chartView'],
        content: null,
        selection: null,
        parentOneWayBindings: ['content'],
        parentFromBindings: ['selection'],

        metadataView: SC.View.extend({
            childViews: ['iconView', 'titleView', 'descriptionView'],
            layout: { left: 0, top: 8, width: 320 },

            iconView: SC.ImageView.extend({
                // This is hardcoded for the SCAG "Scenario Planning Tool" logo right now.
                layout: { left: 0, height: 34, width: 114 },
                scale: SC.BEST_FIT,
                useCanvas: NO,
                client: null,
                clientBinding: SC.Binding.oneWay('Footprint.regionActiveController*content.client'),
                clientPath: null,
                clientPathBinding: SC.Binding.oneWay('Footprint.regionActiveController.clientPath'),
                // This gets it directly from the client configuration.
                // valueBinding: SC.Binding.oneWay('Footprint.regionActiveController*clientPath.logoPath')
                // But temporarily, here is the SPM logo
                value: function() {
                    var client = this.get('client');
                    var client_path = this.get('clientPath');
                    if (client && client_path) {
                        var image_path = 'images/%@_model_logo.png'.fmt(client).toLowerCase();
                        return client_path.STATIC.fmt(image_path);
                    }
                    return null;
                }.property('client', 'clientPath').cacheable()

            }),

            titleView: SC.LabelView.extend({
                layout: { top: 0, left: 114 + 8, height: 34, right: 0 },
                classNames: ['footprint-editable-12font-bold-title-view'],
                value: 'UrbanFootprint Data Manager',
            }),

            descriptionView: SC.LabelView.extend({
                layout: { top: 34 + 8, bottom: 10, width: 310 },
                escapeHTML: NO,
                value: 'The SPM Data Manager  provides local and regional data sets to jurisdictions ' +
                    'across Southern California. It is used to view, edit, and comment upon data and ' +
                    'serves as a common data bridge across SCAG and the cities and counties in the ' +
                    'region. For help, see the ' +
                    '<a target="_blank" href="https://scag-spm-documentation.readthedocs.io/">' +
                    'SPM Data Manager user guide</a>.'
            })
        }),
        chartView: Footprint.LineChartSectionView.extend({
            layout: { left: 320 }
        })
    })
});
