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
 * Displays a list of titlebars above the scenarios and the various analytic columns.
 * Clicking on the titlebars themselves changes the state of the application. The default state is the general view, achieved by clicking on the Scenarios bar. Clicking on an analytical changes to the detail state of that analytical category.
 * @type {Class}
 */


Footprint.ScenarioToolbarView = SC.ToolbarView.extend({
    classNames: "footprint-scenario-toolbar-view".w(),
    childViews: ['titleView', 'scenarioMenuView'],
    contentBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),
    // Make the title Scenarios for [property name]
    contentNameProperty: 'parent_config_entity.name',
    title: 'Scenarios',
    titleView: SC.LabelView.extend({
        layout: { height: 20, right: 35, centerY: 0 },
        valueBinding: SC.Binding.transform(function(name) {
            if (!name)
                return 'Scenarios';
            else
                return name;
        }).oneWay('Footprint.scenarioActiveController.name')
    }),
    scenarioMenuView: Footprint.EditButtonView.extend({
        layout: { right: 5, width: 26, height: 18, centerY: 0 },
        toolTip: 'Manage Scenarios',
        controlSize: SC.SMALL_CONTROL_SIZE,

        icon: sc_static('images/section_toolbars/pulldown.png'),
        contentBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),

        recordType: Footprint.Scenario,
        activeRecordBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),

        menuItems: [
            SC.Object.create({ title: 'Manage Scenarios', keyEquivalent: 'ctrl_i', action: 'doManageScenarios'})
        ]
    })
//
//    stats1View: SC.ToolbarView.extend({
//        childViews: ['label'],
//        layout: {right:180, width: 90, height: 18},
//        anchorLocation: SC.ANCHOR_TOP,
//        label: SC.LabelView.extend({
//            valueBinding: SC.Binding.oneWay(parentViewPath(2, '.titles.stats1View'))
//        })
//    }),
//    stats2View: SC.ToolbarView.extend({
//        childViews: ['label'],
//        layout: {right:90, width: 90, height: 18},
//        anchorLocation: SC.ANCHOR_TOP,
//        label: SC.LabelView.extend({
//            valueBinding: SC.Binding.oneWay(parentViewPath(2, '.titles.stats2View'))
//        })
//    }),
//    stats3View: SC.ToolbarView.extend({
//        childViews: ['label'],
//        layout: {right:0, width: 90, height: 18},
//        anchorLocation: SC.ANCHOR_TOP,
//        layoutBinding: SC.Binding.oneWay(parentViewPath(1, '.layouts.stats3View')),
//        label: SC.LabelView.extend({
//            valueBinding: SC.Binding.oneWay(parentViewPath(2, '.titles.stats3View'))
//        })
//    })
});
