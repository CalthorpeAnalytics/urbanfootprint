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


sc_require('models/config_entity_models');

Footprint.Scenario = Footprint.ConfigEntity.extend({
    year: SC.Record.attr(Number),
    // Override ConfigEntity's definition so that the API knows to look up a Project
    parent_config_entity:SC.Record.toOne('Footprint.Project'),
    // The scenario that was the clone source of this scenario, if any
    origin_instance:SC.Record.toOne('Footprint.Scenario'),
    // The parent_config_entity is always a Project, so we can provide this synonym property
    project:function() {
        return this.get('parent_config_entity');
    }.property('parent_config_entity'),

    _cloneProperties: function() {
        return sc_super();
    },

    _copyProperties: function() {
        return sc_super().concat(['behavior']);
    },

    core_analytic_result: SC.Record.toOne('Footprint.AnalyticResult', { isMaster: YES, inverse:'scenario'}),

    /***
     * Only allow deleting of Scenarios that are cloned and not in post-save progress
     */
    isDeletable: function() {
        return !!this.get('origin_instance') && (!this.get('progress') || this.get('progress')==1);
    }.property('origin_instance').cacheable(),

    behaviorStatus: null,
    behaviorStatusBinding: SC.Binding.oneWay('*behavior.status'),

    /***
     * Only allow cloning of future Scenarios
     */
    isCloneable: function() {
        if (this.getPath('behaviorStatus') & SC.Record.READY)
            return this.getPath('behavior.key') == 'behavior__future_scenario';
    }.property('behavior', 'behaviorStatus').cacheable()
});

Footprint.DwellingUnitDatum = Footprint.Record.extend({
    dwelling_unit_type: SC.Record.attr(String),
    value: SC.Record.attr(Number)
});

Footprint.ControlTotal = Footprint.Record.extend({
    value:SC.Record.attr(Number)
});

// TODO these are just used by the API for now
Footprint.FutureScenario = Footprint.Scenario.extend();
Footprint.BaseScenario = Footprint.Scenario.extend();
