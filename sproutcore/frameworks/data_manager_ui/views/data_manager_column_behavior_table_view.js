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


DataManagerUI.views.ColumnBehaviorTableView = Footprint.TableInfoView.extend({

    columns: function() {
        return [
            SC.Object.create(SCTable.Column, {
                _name: "DMUI.Column",
                name: function() {
                    return SC.String.loc(this.get('_name'));
                }.property('_name').cacheable(),
                valueKey: 'field',
                width: 450
            }),
            SC.Object.create(SCTable.Column, {
                _name: "DMUI.Type",
                name: function() {
                    return SC.String.loc(this.get('_name'));
                }.property('_name').cacheable(),
                valueKey: 'type',
                width: 100
            }),
            // The Behaviors to which the attribute contributes via the AttributeGroups of the Behaviors
            /*
            SC.Object.create(SCTable.Column, {
                _name: "DMUI.UsedByBehaviors",
                name: function() {
                    return SC.String.loc(this.get('_name'));
                }.property('_name').cacheable(),
                valueKey: 'behaviors',
                width: 300
            })
            */
        ]
    }.property().cacheable(),

    formattedContentBinding: SC.Binding.oneWay('.content'),

    /***
     * Extend the titleView to include Manage Behaviors button
     */
    titleView: SC.View.extend({
        childViews: ['textView'], //, 'buttonView'],
        layout: SC.Binding.oneWay('.parentView.titleViewLayout'),

        textView: Footprint.LabelView.extend({
            value: 'DMUI.ColumnsBehavior',
            layout: { left: 0 },
        }),

        buttonView: SC.ButtonView.extend({
            localize: YES,
            title: 'DMUI.ManageBehaviors',
            layout: { width: 120, height: 17, right: 0 },
            controlSize: SC.SMALL_CONTROL_SIZE,
        })
    })
});
