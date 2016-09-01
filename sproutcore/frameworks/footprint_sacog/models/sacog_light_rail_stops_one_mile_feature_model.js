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



FootprintSacog.SacogLightRailStopsOneMileFeature = Footprint.Feature.extend({
    name: SC.Record.attr(String),
    node: SC.Record.attr(Number),
    color: SC.Record.attr(Number),
    stop_name: SC.Record.attr(String),
    active: SC.Record.attr(String)
});
