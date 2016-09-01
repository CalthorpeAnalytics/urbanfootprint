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

sc_require('states/loading_state');

Footprint.LoadingConfigEntityState = Footprint.LoadingState.extend({

    parentController: null,
    parentConfigEntity: null,
    parentConfigEntities: null,

    /**
     * Queries for all the scenarios of the ConfigEntity
     * @returns {*}
     */
    recordArray:function() {
        return Footprint.store.find(
            SC.Query.create({
                recordType: this.get('recordType'),
                location:SC.Query.REMOTE,
                parameters: $.extend(
                    {},
                    this.get('parentConfigEntity') ?
                        { parent_config_entity: this.get('parentConfigEntity') } :
                        {},
                    this.get('parentConfigEntities') ?
                        { parent_config_entities: this.get('parentConfigEntities') } :
                        {},
                    this.get('limit') ?
                        { offset: 0, limit: this.get('limit') } :
                        {}
                )
        }));
    }
});
