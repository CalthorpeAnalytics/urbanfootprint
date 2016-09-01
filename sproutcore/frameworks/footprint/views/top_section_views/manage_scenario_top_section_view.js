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


sc_require('views/top_section_views/result_section_view');
sc_require('views/section_toolbars/scenario_toolbar_view');

Footprint.ManageScenarioTopSectionView =  SC.SplitView.extend({

    sizeOffset:-2,
    canCollapse:YES,
    layoutDirection: SC.LAYOUT_HORIZONTAL,
    childViews: ['scenarioSectionView', 'scenarioInformationView'],

    content: null,
    contentBinding: SC.Binding.oneWay('Footprint.scenarioCategoriesTreeController.arrangedObjects'),

    selection: null,
    selectionBinding: SC.Binding.from('Footprint.scenarioCategoriesTreeController.selection'),

    scenarioSectionView: Footprint.View.extend(SC.SplitChild, {
        classNames: "footprint-scenario-section-view".w(),
        childViews: 'overlayView toolbarView listView'.w(),
        parentOneWayBindings: ['content'],
        parentFromBindings: ['selection'],
        size: 370,
        sizeOffset:-2,
        canCollapse:YES,

        overlayView: Footprint.OverlayView.extend({
            parentOneWayBindings: ['content'],
            parentWayBindings: ['selection']
        }),
        toolbarView: Footprint.ScenarioToolbarView.extend({
            layout: { top: 2, height: 20},
            controller: Footprint.projectsController
        }),
        listView: SC.ScrollView.extend({
            layout: { top: 23 },

            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            selection: null,
            selectionBinding: SC.Binding.from('.parentView.selection'),

            contentView: SC.SourceListView.extend({

                isEnabledBinding: SC.Binding.oneWay('.content').bool(),
                rowHeight: 30,
                isEditable: YES,
                actOnSelect: YES,
                canEditContent: YES,
                canDeleteContent: YES,
                canReorderContent: YES,
                contentBinding: SC.Binding.oneWay('.parentView.parentView.content'),
                selectionBinding: SC.Binding.from('.parentView.parentView.selection'),
                contentValueKey: 'name',

                contentIndexRowSize: function (view, content, contentIndex) {
                    var obj = content.objectAt(contentIndex);
                    return obj && obj.kindOf(Footprint.Scenario) ? 30 : 15;
                },
                customRowSizeIndexes: function() {
                    return SC.IndexSet.create(0, this.get('length'));
                }.property('length', 'customRowHeightIndexes').cacheable(),

                // This is used to show progress bar overlays after clone/create/update
                editControllerContent:null,
                editControllerContentBinding: SC.Binding.from('Footprint.scenariosEditController.content'),

                groupExampleView: SC.View.extend(SC.ContentDisplay, {
                    contentDisplayProperties: ['name'],
                    render: function(context) {
                        var title = this.getPath('content.name') || '';
                        title = title.titleize();
                        context.begin()
                               .addClass(this.getPath('theme.classNames'))
                               .addClass(['sc-view', 'footprint-scenario-group'])
                               .push(title)
                               .end();
                    },
                    update: function($context) {
                        var title = this.getPath('content.name') || '';
                        title = title.titleize();
                        $context.find('.footprint-scenario-group').text(title);
                    }
                }),

                exampleView: SC.View.extend(SC.Control, {
                    classNames: ['sc-list-item-view', 'footprint-scenario-item'],
                    childViews: 'progressOverlayView nameView'.w(),

                    // The view that can be edited by double-clicking
                    editableChildViewKey: 'nameView',
                    editControllerContent: null,
                    editControllerContentBinding: SC.Binding.oneWay('.parentView.editControllerContent'),

                    nameView: SC.LabelView.extend({
                        layout: {left: 10, right:100, top: 5, bottom: 5},
                        valueBinding: SC.Binding.oneWay('.parentView*content.name')
                    }),

                    progressOverlayView: Footprint.ProgressOverlayView.extend({
                        layout: { width:100, right: 5, centerY: 0, height: 16},
                        contentBinding: SC.Binding.oneWay('.parentView.content'),
                        progressBinding: SC.Binding.oneWay('*content.progress'),
                        isOverlayVisibleBinding:SC.Binding.oneWay('*content.saveInProgress')
                    })
                })
            })
        })
    }),

    scenarioInformationView: Footprint.View.extend(SC.SplitChild, {
        autoResizeStyle: SC.RESIZE_AUTOMATIC,
        positionOffset:2,
        sizeOffset:-2,
        canCollapse:YES,
        childViews: ['metadataView', 'chartView'],
        content: null,
        selection: null,
        parentOneWayBindings: ['content'],
        parentFromBindings: ['selection'],

        metadataView: SC.View.extend({
            classNames: ['footprint-meta-data-view'],
            childViews: ['nameView', 'creatorView', 'descriptionView'],
            layout: {width:200},
            content: null,
            selection: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            selectionBinding: SC.Binding.from('.parentView*selection.firstObject'),

            nameView: Footprint.InfoView.extend({
                childViews: 'titleView contentView'.w(),
                layout: {left: 10, top: 10, height: 24},
                title: 'Name: ',
                contentBinding: '.parentView.selection',

                titleView: SC.LabelView.extend({
                    classNames: "footprint-infoview-title-view".w(),
                    layout: {top: 0 , height: 16, width: 40},
                    valueBinding: '.parentView.title'
                }),
                contentView: SC.LabelView.extend({
                    classNames: ['footprint-editable-12font-bold-title-view'],
                    layout: {left: 44},
                    isEditable: NO,
                    contentBinding: '.parentView.content',
                    contentValueKey: 'name'
                })
            }),

            creatorView: Footprint.InfoView.extend({
                childViews: 'titleView contentView'.w(),
                layout: {left: 10, top: 40, height: 24},
                title: 'Created by: ',
                contentBinding: '.parentView*selection.creator',

                titleView: SC.LabelView.extend({
                    classNames: "footprint-infoview-title-view".w(),
                    layout: {width: 65, height: 16},
                    valueBinding: '.parentView.title'
                }),

                contentView: SC.LabelView.extend({
                    classNames: ['footprint-editable-12font-bold-title-view'],
                    layout: {left: 69},
                    isEditable: NO,
                    contentBinding: '.parentView.content',
                    contentValueKey: 'username'
                })
            }),
            descriptionView: Footprint.ReadonlyDescriptionView.extend({
                layout: {left: 10, top: 70, bottom: 10},
                title: 'Description: ',
                contentBinding: '.parentView.selection',
                contentValueKey: 'description'
            })
        }),
        chartView: Footprint.ResultSectionView.extend({
            layout: {left: 220}
        })
    })
});
