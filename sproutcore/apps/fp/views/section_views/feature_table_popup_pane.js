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



Footprint.FeatureTablePopupPane = SC.PalettePane.extend({

    layout: { width: 400, height: 500 },
    classNames:'footprint-popup-pane'.w(),

    doClose: function() {
        this.remove();
    },

    contentView: SC.View.extend({
        childViews: ['titlebarView', 'tableView', 'overlayView'],

        titlebarView: SC.View.extend({
            layout: {top: 0, height: 40},
            childViews: ['titleLabelView', 'closeButtonView'],
            titleLabelView: SC.LabelView.extend({
                layout: { left: 10, centerY: 4, right: 50, height: 24},
                value: 'Selected Feature Properties'
            }),
            closeButtonView: SC.ImageButtonView.extend({
                layout: {right: 10, top: 10, width: 18, height: 18},
                classNames: 'footprint-close-panel-button-view'.w(),
                action: 'doClose',
                image: 'close-panel-icon',
                targetBinding: SC.Binding.oneWay('.pane')
            })
        }),

        /***
         * Shows the attributes of the single popup feature. The rows
         * of this are each attribute value. The columns are just two
         * columns, the name of the attribute and the value column.
         *
         * If the feature is already in the store we show it immediately.
         * Otherwise we show and status overlay view until it loads
         */
        tableView: SCTable.TableView.design({
            childViews: ['titlebarView', 'contentView'],
            layout: { top: 40, left: 10, right: 10, bottom: 10},
            classNames: ['footprint-feature-table-popup-table-view'],
            showAlternatingRows: YES,

            horizontalContent: null,
            horizontalContentBinding: SC.Binding.oneWay('Footprint.featurePopupTableController.content'),
            horizontalColumns: null,
            horizontalColumnsBinding: SC.Binding.oneWay('Footprint.featurePopupTableController.columns'),

            // Used to alter default column widths (join queries have longer attribute names)
            isJoinQuery: null,
            isJoinQueryBinding: SC.Binding.oneWay('Footprint.layerSelectionActiveController*joins.length').bool(),

            // Make the horizontal content vertical
            // For example: A normal table with like this
            // id | apn | ...
            //  0 | 123 | ...
            //  1 | 345 | ...
            // ...
            // Becomes:
            // Column | Value
            //   id   |   0
            //   apn  |  123
            // assuming we want to show the first row
            contentObserver: function () {
                // instance is set to lastObject due to joined layer properties
                // showing up as undefined on first time fetching
                // Footprint.featurePopupTableController.content sometimes has 1 or 2 items in it
                // if there are 2 items, the second item is the one that has the joined feature properties
                var instance = this.getPath('horizontalContent.lastObject');
                if (!instance) {
                    this.set('content', null);
                    this.set('columns', []);
                    return;
                }

                // Map each attribute to the name of the column and the value of the attribute
                this.set('content',
                         this.get('horizontalColumns').map(function (column) {
                             return SC.Object.create({
                                 // The pretty name of the column
                                 attributeTitle: column.get('name'),
                                 // Extract the attribtue based on the valueKey of the column
                                 attributeValue: instance.get(column.get('valueKey'))
                             });
                         }));
                // Columns names are constant
                // Change the widths based on whether or not this is a join query.
                // Join queries need more room for the attribute names, which are longer
                var isJoinQuery = this.get('isJoinQuery');
                this.set('columns', [
                    SC.Object.create(SCTable.Column, {
                        name: 'Column',
                        valueKey: 'attributeTitle',
                        width: isJoinQuery ? 150: 100
                    }),
                    SC.Object.create(SCTable.Column, {
                        name: 'Value',
                        valueKey: 'attributeValue',
                        width: isJoinQuery ? 150 : 280
                    })
                ]);
            }.observes('*horizontalContent.[]', '*horizontalColumns.[]', '.isJoinQuery')
        }),

        overlayView: Footprint.OverlayView.extend({
            layout: { top: 40, left: 10, right: 10, bottom: 10 },
            contentBinding: SC.Binding.oneWay('Footprint.featurePopupTableController.content'),
            statusBinding: SC.Binding.oneWay('Footprint.featurePopupTableController*content.status'),
        })
    })
});
