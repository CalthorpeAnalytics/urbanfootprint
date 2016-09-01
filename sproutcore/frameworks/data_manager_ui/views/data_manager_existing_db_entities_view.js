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
 * Left side of the panel. This holds the layer tree, search box, etc
**/
DataManagerUI.views.ExistingDbEntitiesView = SC.View.extend({
    childViewLayout: SC.View.VERTICAL_STACK,
    childViews: [
        'titleView',
        'dbEntitiesTreeView',
    ],
    childViewLayoutOptions: {
        resizeToFit: false,
    },
    layerId: 'dmui-existing-db-entities-view',
    content: null,
    selection: null,
    scenario: null,

    titleView: SC.View.extend({
        childViewLayout: SC.View.HORIZONTAL_STACK,
        childViews: ['layerNameView', 'scenarioVisibilityView'],
        layerId: 'dmui-db-entity-header-view',
        layout: { height: 20, left: 8, right: 8 },
        childViewLayoutOptions: {
            resizeToFit: false,
        },

        layerNameView: SC.LabelView.extend({
            value: 'Layer Name',
            layout: { height: 16 },
            fillRatio: 1,
            classNames: ['center-text'],
        }),

        scenarioVisibilityView: Footprint.LabelView.extend({
            value: 'DMUI.LayerVisibility', // "Visbility"
            layout: { height: 16 },
            fillRatio: 1,
            classNames: ['right-text'],
        }),
    }),

    /**
    * The layer list
    */
    dbEntitiesTreeView: SC.ScrollView.extend({
        layout: { height: 400 },
        layerId: 'dmui-db-entity-tree-view',
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        scenario: null,
        scenarioBinding: SC.Binding.oneWay('.parentView.scenario'),
        selection: null,
        selectionBinding: SC.Binding.from('.parentView.selection'),
        layerLibrary: null,
        layerLibraryBinding: SC.Binding.oneWay('.parentView.layerLibrary'),

        contentView: SC.SourceListView.extend({
            rowHeight: 18,
            actOnSelect: NO,
            canReorderContent: NO,
            showAlternatingRows: YES,
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.parentView.content'),
            selection: null,
            selectionBinding: SC.Binding.from('.parentView.parentView.selection'),
            scenario: null,
            scenarioBinding: SC.Binding.from('.parentView.parentView.scenario'),
            layerLibrary: null,
            layerLibraryBinding: SC.Binding.oneWay('.parentView.parentView.layerLibrary'),

            // Shows a DbEntity by binding the content
            exampleView: Footprint.DbEntityEditItemView.extend({
                scenarioBinding: SC.Binding.from('.parentView.scenario'),
            }),
            // Shows a DbEntity group item which is a Footprint.TreeItem
            groupExampleView: Footprint.DbEntityGroupItemView,
        }),
    }),
});
