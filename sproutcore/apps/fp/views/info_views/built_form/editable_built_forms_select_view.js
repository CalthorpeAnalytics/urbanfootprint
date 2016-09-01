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


sc_require('views/info_views/record_item_with_style_view');

Footprint.EditableBuiltFormsSelectView = SC.View.extend({

    childViews: ['scrollView'],

    media: null,
    content: null,
    selection: null,
    // recordType is used for cloning
    recordType: null,

    scrollView: SC.ScrollView.extend({
        classNames: ['footprint-built-form-scroll-view'],

        media: null,
        mediaBinding: SC.Binding.oneWay('.parentView.media'),

        content: null,
        contentBinding:SC.Binding.oneWay('.parentView.content'),

        selection: null,
        selectionBinding: SC.Binding.from('.parentView.selection'),

        contentView: SC.SourceListView.extend({
            isEnabledBinding: SC.Binding.oneWay('.content').bool(),
            rowHeight: 20,
            actOnSelect: NO,
            contentIconKey: 'medium',
            contentValueKey: 'name',
            contentBinding: SC.Binding.oneWay('.parentView.parentView.content'),
            selectionBinding: SC.Binding.from('.parentView.parentView.selection'),

            /***
             * Displays a BuiltForm name with the medium fill color
             */
            exampleView: Footprint.RecordItemWithStyleView.extend({
                classNames: ['footprint-built-form-item'],
                styleClass: 'footprint-medium-color',
                labelStyleClass: 'footprint-built-form-item-label-view',
                // The BuiltForm has a convenient computed property to access the id Style
                styleBinding: SC.Binding.oneWay('*content.idStyle')
            })
        })
    })
});

Footprint.EditableBuiltFormsFullListView = SC.View.extend({
    childViews: ['editableBuiltFormsSelectView'],
    status: null,
    content: null,
    selection: null,
    // recordType is used for cloning
    recordType: null,

    // Cloning and deleting is disabled
    /*
    copyButtonView: Footprint.AddButtonView.extend({
        layout: { left: 0, width: 16, top: 0, height: 16 },
        action: 'doCloneRecord',
        // We want to clone the selected item
        contentBinding: SC.Binding.oneWay('.parentView*selection.firstObject'),
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        isVisibleBinding: SC.Binding.oneWay('.content').bool()
    }),

    deleteButtonView: Footprint.DeleteButtonView.extend({
        layout: { left: 24, width: 16, top: 0, height: 16},
        action: 'doPromptDeleteRecord',
        // We want to delete the selected item
        contentBinding: SC.Binding.oneWay('.parentView*selection.firstObject'),
        isVisibleBinding: SC.Binding.oneWay('.content').bool()
    }),
    */

    editableBuiltFormsSelectView: Footprint.EditableBuiltFormsSelectView.extend({
        layout: { top:20 },
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        selectionBinding: SC.Binding.from('.parentView.selection')
    })
});
