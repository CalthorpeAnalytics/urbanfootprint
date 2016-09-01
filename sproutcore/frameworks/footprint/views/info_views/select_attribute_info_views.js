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

sc_require('views/info_views/query/join_columns_info_view');
sc_require('views/info_views/query/join_columns_info_view');

Footprint.AttributeJoinColumnsViewMixin = {
    /***
     * If we have no items show a loading message or a none available.
     * If we have items and nothing is selected show a select message
     */
    nullTitleIfEmpty: function() {
        // TODO nonlocalized because shared among apps.
        return (!this.get('status') || this.get('status') & SC.Record.READY) ?
            (this.getPath('content.length') ? 'Select' : 'None Available') :
            'Loading'
    }.property('content', 'content.[]', 'status').cacheable(),
};

/***
 * Shows available attributes of the current DbEntity without any join attributes
 */
Footprint.SelectAttributeInfoView = Footprint.JoinColumnsInfoView.extend(Footprint.AttributeJoinColumnsViewMixin, {
    classNames:['footprint-select-attribute-info-view'],
    status: null // Override computed status
});
