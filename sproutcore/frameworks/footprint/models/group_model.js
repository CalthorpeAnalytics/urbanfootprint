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


Footprint.Group = Footprint.Record.extend(Footprint.Key, {
    name: SC.Record.attr(String),
    alwaysUpdateName: YES,
    superiors: SC.Record.toMany('Footprint.Group'),
    users: SC.Record.toMany('Footprint.User', {sMaster: NO, inverse: 'groups'}),
    config_entity: SC.Record.toOne('Footprint.ConfigEntity', {isMaster: YES, inverse: 'group'})
});
