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


/**
 * Like ItemView but adds the knowledge of the item's status with contentStatus.
 * If the status is new or dirty, the view adds CSS classes new-record or dirty-record, respectively
 * User: andy
 * Date: 7/30/15
 */

Footprint.EditItemView = SC.View.extend(SC.ContentDisplay, {
    classNameBindings: ['isNew: new-record', 'isDirty: dirty-record'],
    content: null,
    /***
     * This defaults to content.status, but can be overridden to access a status elsewhere
     */
    contentStatus: null,
    contentStatusBinding: SC.Binding.oneWay('*content.status'),
    isNew: null,
    isNewBinding: SC.Binding.oneWay('.contentStatus').equalsStatus(SC.Record.READY_NEW),
    isDirty: null,
    isDirtyBinding: SC.Binding.oneWay('.contentStatus').equalsStatus(SC.Record.READY_DIRTY)
});
