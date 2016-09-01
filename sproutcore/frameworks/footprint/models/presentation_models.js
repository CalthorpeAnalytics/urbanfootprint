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
sc_require('models/key_mixin');
sc_require('models/name_mixin');
sc_require('models/name_mixin');
sc_require('models/db_entity_models');
sc_require('models/medium_models');

Footprint.Presentation = Footprint.Record.extend(
    Footprint.Key,
    Footprint.Name,
    Footprint.Deletable, {

    isPolymorphic: YES,
    config_entity: SC.Record.toOne("Footprint.ConfigEntity", {
        isMaster: NO,
        inverse: 'presentations'
    }),

    _mapAttributes: {
        key: function (record, key) {
            return key + 'New';
        },
        name: function (record, name) {
            return name + 'New';
        }
    },
    solos:null,
    // TODO The controller's keys property is causing a recordDidChange for some reason.
    // I'm thus putting this here to prevent that. It serves no purpose here
    keys: null
});
