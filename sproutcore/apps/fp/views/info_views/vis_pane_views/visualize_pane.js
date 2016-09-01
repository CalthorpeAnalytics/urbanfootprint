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


sc_require('resources/donutChartMaker');
sc_require('resources/builtFormVisUtils');
sc_require('views/info_views/vis_pane_views/examples_view');
sc_require('views/info_views/vis_pane_views/development_chars_view');
sc_require('views/info_views/vis_pane_views/donut_charts_view');
sc_require('views/info_views/vis_pane_views/bar_chart_view');
sc_require('views/info_views/built_form/built_form_scroll_view');

Footprint.VisualizePane = Footprint.PanelPane.extend(SC.ActionSupport, {

    layout: { height:630, width:1300, centerX: 0, centerY: 0 },

    contentView: SC.View.extend({
        classNames:['footprint-visualize-palette-pane'],
        childViews:'mainView listView'.w(),

        content:null,
        contentBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormActiveController.content'),

        flatBuiltFormContent: null,
        flatBuiltFormContentBinding:SC.Binding.oneWay('Footprint.flatBuiltFormActiveController.content'),

        mainView: SC.View.extend({

            layout: { left:.20 },

            classNames:['footprint-visualize-pane-content'],
            childViews:'headerView descriptionView examplesView barChartView donutChartsView rightOfBarChartView developmentCharsView footerView'.w(),

            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),

            flatBuiltFormContent: null,
            flatBuiltFormContentBinding:SC.Binding.oneWay('.parentView.flatBuiltFormContent'),

            color: null,
            colorBinding: SC.Binding.oneWay('*content.medium').transform(function(medium) {
             if (medium) {
                 return medium.getPath('content.fill.color');
             }
            }),

            headerView: SC.LabelView.extend({
                classNames: ['footprint-visualize-pane-header'],
                layout: { left: 0, right: 0, top: 0, height: 0.07 },
                displayProperties: ['content', 'color'],

                valueBinding: SC.Binding.oneWay('.parentView*content.name'),

                color: null,
                colorBinding: SC.Binding.oneWay('.parentView.color'),

                backgroundColor:null,
                backgroundColorBinding: SC.Binding.oneWay('.parentView.color'),
                classNameBindings: ['hasLightBackground'],

                hasLightBackground: function() {
                    if (this.get('color')) {
                        return isLightColor(this.get('color'));
                        }
                    }.property('color').cacheable(),

                render: function(context) {
                sc_super();
                }
            }),

            descriptionView: SC.View.design({
                layout: { top: 0.06, left: 0, right:.65, bottom: 0.70},
                classNames: ['descriptionBlock'],
                displayProperties: ['content'],

                content: null,
                contentBinding: SC.Binding.oneWay('.parentView.flatBuiltFormContent'),

                render: function(context) {
                 var description =this.getPath('content.description');
                 context = context.begin('div').push(description).end();

                 sc_super();
                }
            }),

            rightOfBarChartView: SC.View.design({
                layout: { top: 0.06, left: 0.95, bottom: 0.75},
                classNames: ['rightOfBarChart']
                // this is a hack to get the rounded edge below the header
            }),

            barChartView: Footprint.BarChartView.extend({
                contentBinding: SC.Binding.oneWay('.parentView.flatBuiltFormContent')
            }),

            donutChartsView: Footprint.DonutChartsView.extend({
                contentBinding: SC.Binding.oneWay('.parentView.flatBuiltFormContent')
            }),

            examplesView: Footprint.ExamplesView,

            developmentCharsView: Footprint.DevelopmentCharsView.extend({
                contentBinding: SC.Binding.oneWay('.parentView.flatBuiltFormContent')
            }),

            footerView: SC.View.extend({
                childViews: 'cancelButtonView'.w(),
                classNames: ['footprint-visualize-pane-footer'],
                layout: { left: 0, right: 0, top: 0.95 },
                displayProperties: ['content', 'color'],

                color: null,
                colorBinding: SC.Binding.oneWay('.parentView.color'),

                render: function(context) {
                 sc_super();
                 var color = this.get('color');
                 context.addStyle("background-color", color);
                },

                cancelButtonView: SC.ButtonView.design({
                 layout: {bottom: 5, right: 20, height:24, width:80},
                 title: 'Close',
                 action: 'doClose',
                 isCancel: YES
                })
            })
        }),

        listView: Footprint.BuiltFormScrollView.extend({
            layout: {right:.8},
            contentBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormCategoriesTreeController.arrangedObjects'),
            selectionBinding: SC.Binding.from('Footprint.urbanBuiltFormCategoriesTreeController.selection')
        })
    })
});
