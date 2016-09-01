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


/***
 * Edits a Record that has a Footprint.Style associated with it
 */
Footprint.RecordItemWithStyleView = SC.View.extend(SC.Control, SC.ContentDisplay, Footprint.StyleRenderMixin, {
    classNames: ['footprint-item-with-color'],

    displayProperties:['style'],
    contentDisplayProperties: ['name', 'status'],

    /**
     * Required. The record to edit
     */
    content: null,

    /**
     * Required. A Footprint.Style property returning a record. this could be the same as content or different
     */
    style: null,

    /***
     * The style to apply to the label div. This is also searched when updating, so something is required
     */
    labelStyleClass: 'footprint-item-with-color-label-view',
    /***
     * The name to display. Defaults to 'name'. Always relative to content
     */
    contentNamePropertyPath: 'name',

    /***
     * Efficient render method to render the record name and the associated color
     * @param context
     */
    render: function(context) {
        if (!this.get('content'))
            return;
        var status = this.getPath('content.status'),
            isNew = status === SC.Record.READY_NEW,
            isDirty = status === SC.Record.READY_DIRTY;
        context.setClass({ 'new-record': isNew, 'dirty-record': isDirty });
        // Style swab
        this.renderStyle(context);
        // Label
        context.begin()
            .addClass(this.getPath('theme.classNames'))
            .addClass(['sc-view', 'sc-label-view', this.get('labelStyleClass')])
            .push(this.get('content').getPath(this.get('contentNamePropertyPath')))
            .end();
    },

    update: function ($context) {
        if (!this.get('content'))
            return;
        var status = this.getPath('content.status'),
            isNew = status === SC.Record.READY_NEW,
            isDirty = status === SC.Record.READY_DIRTY;
        $context.setClass({ 'new-record': isNew, 'dirty-record': isDirty });
        this.updateStyle($context);
        // Label
        $context.find('.%@'.fmt(this.get('labelStyleClass'))).text(this.get('content').getPath(this.get('contentNamePropertyPath')));
    }
});
