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

sc_require('views/data_manager_column_behavior_table_view');
sc_require('views/data_manager_join_view');

/***
 * TODO this has been permanently replaced by the view in the data_manager_view_container
 */
DataManagerUI.views.DetailView = SC.View.extend({
    childViews: ['dataView', 'columnBehaviorTableView', 'cancelRevertSaveButtonView'],
    layerId: 'dmui-detail-view',

    // All of the DbEntities. Used for the cancel and saveAll button
    allContent: null,
    // Status of the DbEntities. Only used for the cancel and saveAll button
    allContentStatus: null,
    // The DbEntity being edited
    content: null,
    // The Scenario of the DbEntity
    scenario: null,
    // The layer
    theLayer: null,

    // The top view showing all the simple fields above the Behavior table
    dataView: SC.View.extend({
        childViews: ['leftColumnView', 'rightColumnView'],
        layout: { top: 30, height: 200, left: 10, right: 10 },
        layerId: 'dmui-data-view',
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        theLayer: null,
        theLayerBinding: SC.Binding.oneWay('.parentView.theLayer'),
        scenario: null,
        scenarioBinding: SC.Binding.oneWay('.parentView.scenario'),

        leftColumnView: SC.View.extend({
            layerId: 'dmui-left-column-view',
            childViews: ['nameView', 'descriptionView', 'categoryView'],
            layout: { top: 0, width: 260},
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),

            nameView: Footprint.NameInfoView.extend({
                layout: { top: 0, height: 44 },
                contentLayout: { left:0, top: 20, height: 25 },

                layerId: 'dmui-name-view',
                title: 'DMUI.Name',
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                contentValueKey: 'name'
            }),

            descriptionView: Footprint.DescriptionInfoView.extend({
                layout: { top: 54, height: 64 },
                contentLayout: {top: 18},
                layerId: 'dmui-description-view',
                title: 'DMUI.Description',
                contentValueKey: 'description'
            }),

            // TODO I can't find any use for this view. It is excluded
            sourceView: Footprint.ReadonlyDescriptionView.extend({
                layout: { top: 54, height: 60 },
                layerId: 'dmui-source-view',
                title: 'DMUI.OriginalSource',

                parentContent: null,
                parentContentBinding: SC.Binding.oneWay('.parentView.content'),
                contentValueKey: null,
                value: function() {
                    var url = this.get('parentContent') && this.getPath('parentContent.url');
                    if (url) {
                        if (url.indexOf('file://')==0)
                            return url.split('/').slice(-1); // hide path
                        else if (url.indexOf('http://')==0)
                            return url.substring(0, url.indexOf('/', 8));
                        else
                            return url;
                    }
                }.property('parentContent').cacheable()
            }),

            /***
             * Adds existing or new DbEntity tags to the DbEntity's tag collection
             */
             categoryView: Footprint.SelectOrAddInfoView.extend({
                layout: { top: 126, height: 44 },
                contentLayout: { top: 20 },
                contentBinding: SC.Binding.oneWay('Footprint.dbEntityFilteredEditCategoriesController.arrangedObjects'),
                selectionBinding: 'Footprint.dbEntityFilteredEditCategoriesController.selection',
                // This shows if the selection is empty
                itemTitleKey: 'value',
                selectionAction: 'doPickCategory',
                addAction: 'doAddCategory',
                title: 'DMUI.SortCategory',
                menuWidth: 200
             })
        }),

        rightColumnView: SC.View.extend({
            childViews: ['joinView', 'tagsView', 'scenarioView'],
            layout: { top: 0, left: 270 },
            layerId: 'dmui-right-column-view',
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            theLayer: null,
            theLayerBinding: SC.Binding.oneWay('.parentView.theLayer'),
            scenario: null,
            scenarioBinding: SC.Binding.oneWay('.parentView.scenario'),

            /***
             * Controls how the DbEntity joins to the Primary Geography DbEntity
             */
            joinView: DataManagerUI.views.JoinView.extend({
                layout: { top: 0, height: 44},
                classNames: ['dmui-join-view'],
                contentBinding: SC.Binding.oneWay('Footprint.joinTypesEditController.content'),
                selectionBinding: 'Footprint.joinTypesEditController.selection'
            }),

            /***
             * Adds existing or new DbEntity tags to the DbEntity's tag collection
             */
            tagsView: Footprint.EditableTagsView.extend({
                layout: { top: 54, height: 114 },
                layerId: 'data-manager-right-column-tags-view',

                contentBinding: SC.Binding.oneWay('.parentView*content.tags'),
                availableItemsBinding: SC.Binding.oneWay('Footprint.dbEntityFilteredEditTagsController.arrangedObjects'),
                availableItemsSelectionBinding: SC.Binding.oneWay('Footprint.dbEntityFilteredEditTagsController.selection'),
                searchStringBinding: 'Footprint.dbEntityFilteredEditTagsController.searchString',
            }),

            layerVisibilityView: Footprint.LayerVisibilityView.extend({
                layout: { top: 124, height: 50, width: 100 },
                layerId: 'dmui-detail-view-layer-visibility-view',
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                theLayerBinding: SC.Binding.oneWay('.parentView.theLayer'),
                scenarioBinding: SC.Binding.oneWay('.parentView.scenario'),
                layerLibrariesApplicationEditBinding: SC.Binding.oneWay('.parentView.layerLibrariesApplicationEdit')
            })
        })
    }),

    columnBehaviorTableView: DataManagerUI.views.ColumnBehaviorTableView.extend({
        layout: { top: 240, bottom: 60 },
        titleViewLayout: { top: 0, height: 17, left: 0, right: 200 },
        tableViewLayout: { top: 18, bottom: 0 },
        classNames: ['dmui-column-behavior-table-view'],
        layerId: 'dmui-column-behavior-table-view',
        childViewLayoutOptions: { paddingBefore: 10, paddingAfter: 10 },
        contentBinding: SC.Binding.oneWay('Footprint.dbEntityFeatureSchemaEditController.content'),
        statusBinding: SC.Binding.oneWay('Footprint.dbEntityFeatureSchemaEditController.status'),
        overlayStatusBinding: SC.Binding.oneWay('.status')
    }),

    cancelRevertSaveButtonView: Footprint.CancelRevertSaveButtonsView.extend({
        layout: {bottom: 20, height: 24},
        contentBinding: SC.Binding.oneWay('.parentView.allContent'),
        status:null,
        statusBinding: SC.Binding.oneWay('.parentView.allContentStatus'),
        selectedItemBinding: SC.Binding.oneWay('.parentView.content')
    })
});
