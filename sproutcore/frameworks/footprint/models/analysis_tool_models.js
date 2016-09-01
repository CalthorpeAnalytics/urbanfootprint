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


sc_require('models/key_mixin');

// Just a base class for more interesting subclasses
Footprint.AnalysisTool = Footprint.Record.extend(Footprint.Key, {
    config_entity: SC.Record.toOne('Footprint.ConfigEntity', {}),
    behavior: SC.Record.toOne('Footprint.Behavior', {})
});

Footprint.EnvironmentalConstraintUpdaterTool = Footprint.AnalysisTool.extend({
    primaryKey: 'unique_id',
    config_entity: SC.Record.toOne('Footprint.ConfigEntity'),
    environmental_constraint_percents: SC.Record.toMany('Footprint.EnvironmentalConstraintPercent', {nested: YES})
});

Footprint.EnvironmentalConstraintPercent = Footprint.Record.extend({
    db_entity: SC.Record.toOne('Footprint.DbEntity', {nested: YES}),
    analysis_tool: SC.Record.toOne('Footprint.EnvironmentalConstraintUpdaterTool'),
    percent: SC.Record.attr(Number),
    priority: SC.Record.attr(Number)
});

Footprint.MergeUpdaterTool = Footprint.AnalysisTool.extend({
    config_entity: SC.Record.toOne('Footprint.ConfigEntity'),
    db_entity_key: SC.Record.attr(String),
    target_config_entity: SC.Record.toOne('Footprint.Region')
});
