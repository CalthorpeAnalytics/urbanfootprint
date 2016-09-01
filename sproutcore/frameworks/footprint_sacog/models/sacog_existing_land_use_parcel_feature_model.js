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


FootprintSacog.SacogExistingLandUseParcelFeature = Footprint.PrimaryParcelFeature.extend({
    census_blockgroup: SC.Record.attr(Number),
    census_block: SC.Record.attr(Number),
    land_use: SC.Record.attr(String),
    acres: SC.Record.attr(Number),
    du: SC.Record.attr(Number),
    jurisdiction: SC.Record.attr(String),
    notes: SC.Record.attr(String),
    emp: SC.Record.attr(Number),
    ret: SC.Record.attr(Number),
    off: SC.Record.attr(Number),
    pub: SC.Record.attr(Number),
    ind: SC.Record.attr(Number),
    other: SC.Record.attr(Number),
    assessor: SC.Record.attr(String),
    gp: SC.Record.attr(String),
    gluc: SC.Record.attr(String)
});
