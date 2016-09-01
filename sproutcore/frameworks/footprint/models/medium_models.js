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
sc_require('models/name_mixin');

Footprint.Medium = Footprint.Record.extend({
    // name has limited use on Medium. It might be removed in the future. Thus name is not linked to key like it
    // is for Scenario and other record types
    name: SC.Record.attr(String),
    description: SC.Record.attr(String),
    // The unique key of the Medium. Usually this is prefixed to help define to what the medium belongs (e.g. a BuiltForm)
    key: SC.Record.attr(String),
    url: SC.Record.attr(String),
    content_type: SC.Record.attr(String),
    content: SC.Record.attr(Object),
    /**
     * Since keys need to be unique when cloning, we generate unique key
     */
    _mapAttributes: {
        key:function(record, key, random) {
            return '%@__%@'.fmt(key, random);
        }
    }
});
