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

sc_require('views/section_views/section_view');
sc_require('views/overlay_view');
sc_require('views/upload_progress_overlay_view');


Footprint.LayerSectionView = Footprint.SectionView.extend({
    classNames: ['footprint-layer-section-view'],

    childViewLayout: SC.View.VERTICAL_STACK,
    childViews: ['toolbarView', 'listView', 'addDataView', 'uploadProgressView'],
    childViewLayoutOptions: {
        resizeToFit: NO
    },

    // The Layer TreeController content
    content: null,
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.layersAndDependenciesController.status'),
    selection: null,
    scenario: null,

    /***
     * The bar above the layer list
     */
    toolbarView: SC.ToolbarView.design({
        layout: { height: 24 },
        childViews: ['titleView', 'menuButtonView', 'expandButtonView'],

        titleView: SC.LabelView.extend({
            layout: { left: 8, height: 16, centerY: 0, right: 35 },
            valueBinding: SC.Binding.transform(function(name) {
                if (!name) return 'Layers';
                else return 'Layers for %@'.fmt(name);
            }).oneWay('.parentView*scenerio.name')
        }),

        menuButtonView: Footprint.EditButtonView.extend({
            layout: { centerY: 0, right: 38, width: 26, height: 18 },
            icon: sc_static('images/layers_icon.png'),
            toolTip: 'Layer Management',
            // Don't enabled this menu until layers and dependencies are ready
            isEnabledBinding: SC.Binding.oneWay('Footprint.layersAndDependenciesController.status').matchesStatus(SC.Record.READY),
            menuItems: [
                SC.Object.create({ title: 'Export Active Layer - to gdb', action: 'doExportRecord' }),
                SC.Object.create({ title: 'Layer Symbology', action: 'doViewLayer'}),
                SC.Object.create({ title: 'Manage Layers', action: 'doConfigureDbEntities'})
            ]
        }),

        expandButtonView: SC.ButtonView.extend({
            layout: { centerY: 0, right: 6, width: 26, height: 18 },
            classNames: ['theme-button-gray', 'theme-button', 'theme-button-shorter'],
            toolTip: 'Order Layers',
            icon: function() {
                if (this.get('value')) return sc_static('images/section_toolbars/pullleft.png');
                else return sc_static('images/section_toolbars/pullright.png');
            }.property('value').cacheable(),
            buttonBehavior: SC.TOGGLE_BEHAVIOR,
            valueBinding: 'Footprint.layersVisibleController.layersMenuSectionIsVisible'
        })
    }),

    /**
     * The layer list
     */
    listView: SC.View.design({
        layout: {},
        fillRatio: 5,
        childViews: ['overlayView', 'scrollView'],
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        status: null,
        statusBinding: SC.Binding.oneWay('.parentView.status'),
        selection: null,
        selectionBinding: SC.Binding.from('.parentView.selection'),

        /***
         * The overlay uses a custom controller to track status
         */
        overlayView: Footprint.LoadingSpinnerView.extend({
            contentBinding:SC.Binding.oneWay('Footprint.layersAndDependenciesController.content'),
            statusBinding:SC.Binding.oneWay('Footprint.layersAndDependenciesController.status')
        }),

        scrollView: SC.ScrollView.extend({
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            status: null,
            statusBinding: SC.Binding.oneWay('.parentView.status'),
            selection: null,
            selectionBinding: SC.Binding.from('.parentView.selection'),
            backgroundColor: '#d0dae3',
            isVisibleBinding: SC.Binding.oneWay('Footprint.layersAndDependenciesController.status').matchesStatus(SC.Record.READY),

            contentView: SC.SourceListView.extend({
                classNames: ['footprint-layer-source-list'],
                layout: {top: 0},
                rowHeight: 18,
                canReorderContent: NO,
                content: null,
                contentBinding: SC.Binding.oneWay('.parentView.parentView.content'),
                status: null,
                statusBinding: SC.Binding.oneWay('.parentView.parentView.status'),
                selection: null,
                selectionBinding: SC.Binding.from('.parentView.parentView.selection'),
                // Shows a Layer by binding the content to a Footprint.Layer
                exampleView: Footprint.LayerItemView,
                // Shows a Layer group item which is a Footprint.TreeItem
                groupExampleView: SC.ListItemView.extend(SC.ContentDisplay, {
                    backgroundColor: 'whitesmoke',
                    contentValueKey: 'name'
                })
            })
        })
    }),

    addDataView: SC.View.design({
        layout: { height: 70, bottom: 0 }, // TODO bottom shouldn't be needed

        // TODO: add back connectToArcGISLayerView when the feature is ready.
        childViews: ['titleView',
                     'uploadView',
                     /* 'connectToArcGISLayerView', */
                    ],
        classNames: ['footprint-layer-section-add-data-view'],
        layoutId: 'footprint-layer-section-add-data-view',
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        status: null,
        statusBinding: SC.Binding.oneWay('.parentView.status'),
        isEnabledBinding: SC.Binding.oneWay('.status').matchesStatus(SC.Record.READY),

        /***
        * The simple title explaining the layer list
        */
        titleView: Footprint.LabelView.extend({
            layout: { top: 8, height: 24, left: 8, right: 0 },
            classNames: ['add-data-title-view'],
            layoutId: 'add-data-title-view',
            localize: true,
            value: 'DMUI.AddData'
        }),

        /***
         * The UploadView initiates an upload, which causes a FileDataset record to be created
         * and updated by the sockedIO state. Whenever an upload happens the uuid is updated
         * to a new id. This in turn causes the FileDataset with the corresponding id to be
         * selected from the Footprint.fileSourcesController as soon as that FileDataset is created
         */
        uploadView: Footprint.UploadItemView.extend({
            layout: { top: 24 + 8, height: 24, left: 8, width: 100},
            classNames: ['add-data_upload-item-view'],
            layerId: 'add-data-upload-item-view',
            // We pass the ConfigEntity that we want to be the target of the upload
            contextBinding: SC.Binding.oneWay('Footprint.featureClassUploadController.content'),
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            uuidBinding: SC.Binding.oneWay('.uploadButtonView.form.uuid'),
            // Set the controller's latestUuid property whenever it changes here
            uuidDidChange: function () {
                if (this.get('uuid'))
                    Footprint.fileSourcesController.setIfChanged('latestUuid', this.get('uuid'));
            }.observes('uuid'),
            fileSourcesController: null
        }),

        // TODO No longer used.
        chooseLayerFromUFView: SC.ButtonView.extend({
            layout: { top: 24+8, height: 24, left: 100+8+8, width: 100},
            contentBinding: SC.Binding.oneWay('.parentView*content'),
            localize: YES,
            title: 'DMUI.ChooseLayerFromUF',
            action: 'doViewDbEntity',
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
        }),

        // TODO Not wired up
        connectToArcGISLayerView: SC.ButtonView.extend({
            layout: { top: 24+8, height: 24, left: (100+8) * 2 + 8, width: 100},
            contentBinding: SC.Binding.oneWay('.parentView*content'),
            localize: YES,
            title: 'DMUI.ConnectToArcGISLayer',
            action: 'doOpenArcGisLayers',
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
        })
    }),

    uploadProgressView: Footprint.UploadProgressListView.design({
        fillRatio: 1,
        layout: { height: 100 },
        classNames: ['upload-progress-view'],

        contentBinding: SC.Binding.oneWay('Footprint.fileSourcesAndDatasetsController.arrangedObjects'),
        isVisibleBinding: SC.Binding.oneWay('*content.length'),
        exampleView: Footprint.ProgressBarView.extend({
            layout: {height: 25, left: 0, width: 100},
            classNames: ['upload-progress-example-view'],
            titleLayout: {left: 0, top: 0, right: 145},
            progressBarLayout: {top: 0, left: 150},
            // Always visible if it exists
            isRunning: YES,
            minimum: 0,
            maximum: 100
        })
    })
});
