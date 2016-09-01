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
sc_require('models/deletable_mixin');


Footprint.AnalysisModule = Footprint.Record.extend(Footprint.Key, Footprint.Deletable, {
    deleted: SC.Record.attr(Boolean),

    config_entity: SC.Record.toOne("Footprint.ConfigEntity", {
        isMaster: YES
    }),
    // The base class version of the tools. Subclass versions are resolved by the AnalysisModule states
    analysis_tools: SC.Record.toMany("Footprint.AnalysisTool"),

    configuration: SC.Record.attr(Object),
    // Defines an undo manager for this instance
    undoManager: null
});
