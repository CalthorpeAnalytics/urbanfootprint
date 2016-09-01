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

sc_require('views/info_views/edit_record_view');

Footprint.EditRecordsSelectView = SC.ScrollView.extend({

    content: null,
    selection: null,
    copyIsVisible: null,
    /***
     * A property path relative to each item's content used for the name. Defaults to 'name'
    */
    contentNameProperty: 'name',
    /***
     * Uses the following record property or property path to determine if the record can be deleted
     */
    deletableNameProperty: null,

    contentView: SC.SourceListView.extend({
        isEnabledBinding: SC.Binding.oneWay('.content').bool(),
        rowHeight: 24,
        actOnSelect: NO,
        canReorderContent: NO,
        copyIsVisible: null,
        copyIsVisibleBinding: SC.Binding.oneWay('.parentView.parentView.copyIsVisible'),
        contentBinding: SC.Binding.oneWay('.parentView.parentView.content'),
        selectionBinding: SC.Binding.from('.parentView.parentView.selection'),
        contentNamePropertyBinding: SC.Binding.from('.parentView.parentView.contentNameProperty'),

        // Show the selection so the user has any idea where they are.
        selectionDidChange: function() {
            this.invokeNext(this._selectionDidChange);
        }.observes('selection'),

        _selectionDidChange: function() {
            var sel = this.get('selection'),
                content = this.get('content'),
                selIndexes, scrollTo;
            if (sel && content) {
                selIndexes = sel.indexSetForSource(content);
                scrollTo = selIndexes ? selIndexes.get('min') : 0;
                this.scrollToContentIndex(scrollTo);
            }
        },

        exampleView: Footprint.EditRecordView.extend({
            contentNamePropertyBinding: SC.Binding.oneWay('.parentView.contentNameProperty')
        })
    })
});
