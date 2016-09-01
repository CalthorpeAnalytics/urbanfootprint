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

// ==========================================================================
// Project:   QueryUI
// ==========================================================================
/*globals QueryUI */
sc_require('views/query_item_view');


/*
    Constants used to adjust the UI quickly.
*/
var QUERIES_PANE_WIDTH = 200;
var QUERIES_PANE_HEIGHT = 340;
var QUERIES_PANE_MARGIN = 15;
var SUMMARY_PANE_HEIGHT = 420;
var SUMMARY_PANE_WIDTH = 480;
var SUMMARY_PANE_MARGIN = 20;
var SUMMARY_COLUMN_SPACING = 15;
var SUMMARY_COLUMN_WIDTH = (SUMMARY_PANE_WIDTH - SUMMARY_PANE_MARGIN * 2 - SUMMARY_COLUMN_SPACING * 2) / 3;

/*
  This container (SC.Page instance) contains all of the pre-configured views that this framework
  provides.

  The reason we use an SC.Page, is so that the views, which are singletons, don't need to be
  initialized as the application code is initially loaded. Initializing a view (by calling create
  on it) takes some cost that we don't want to pay on initial load. SC.Page will handle this for
  us automatically when the property is first accessed via `QueryUI.views.get('viewName')`.

  Likewise, SC.Page will replace the original un-instantiated property with the new singleton, which
  slightly reduces the memory load of the system. Having the pre-configured view in a separate file
  would mean that the un-necessary class would still exist in memory after the singleton is created
  from it.
*/
QueryUI.views = SC.Page.create({

    optionsMenu: SC.MenuPane.extend({
        layout: { width: 160 },
        items: [{
            title: 'QUI.ManageQueryMenuItem',
            action: 'showManageQueries',
            target: QueryUI
        }, {
            title: 'QUI.SharingSettingsMenuItem',
            action: 'showSharingSettings',
            target: QueryUI
        }]
    }),

    panel: SC.View.extend({
        childViews: ['panelTitle', 'helpButton', 'optionsButton', 'primaryDropZone', 'primaryQueryBox', 'buttonRow'],
        childViewLayout: SC.View.VERTICAL_STACK,
        childViewLayoutOptions: { paddingBefore: 10, paddingAfter: 10, spacing: 15 },
        layerId: 'qui-panel',

        panelTitle: SC.LabelView.extend({
          layerId: 'qui-title',
          layout: { height: 30, left: 10, right: 10 },
          localize: true,
          value: 'QUI.QueryTitle'
        }),

        helpButton: SC.ImageButtonView.extend({
          action: 'showQueryHelp',
          image: 'qui-help-button',
          layout: { top: 11, height: 24, width: 36, right: 46, border: 1 },
          target: QueryUI,
          useAbsoluteLayout: true // Don't include this in the automatic child view layout.
        }),

        optionsButton: SC.ImageButtonView.extend({
          action: 'showOptionsMenu',
          image: 'qui-options-button',
          layout: { top: 11, height: 24, width: 36, right: 5, border: 1 },
          target: QueryUI,
          useAbsoluteLayout: true // Don't include this in the automatic child view layout.
        }),

        // The primary drop zone.
        primaryDropZone: SC.View.extend({
            childViews: ['emptyLabel'],
            classNames: ['qui-drop-zone', 'qui-dashed-border'],

            // Visual indication of accepting drops.
            classNameBindings: ['readyForDrop'],
            readyForDrop: false,

            isVisibleBinding: SC.Binding.oneWay('QueryUI.queryController.content').not(),

            layout: { left: 10, right: 10, height: 300, border: 1 },

            emptyLabel: SC.LabelView.extend({
                classNames: ['qui-drop-zone-label'],
                layout: { height: 20, left: 10, right: 10, centerY: 0 },
                localize: true,
                value: 'QUI.PrimaryDropZoneLabel'
            }),

            /** SC.DropTarget.prototype */
            isDropTarget: true,

            /** @private SC.DropTarget protocol. */
            acceptDragOperation: function (drag, op) {
                // console.log('%@ - acceptDragOperation(%@, %@):  dragView: %@'.fmt(this, drag, op, drag.dragView));
                return true;
            },

            /** SC.DropTarget.prototype */
            dragStarted: function(drag, evt) {
                // console.log('%@ - dragStarted(%@, evt):  dragView: %@'.fmt(this, drag, drag.dragView));
                this.set('readyForDrop', true);
            },

            /** SC.DropTarget.prototype */
            dragEnded: function(drag, evt) {
                // console.log('%@ - dragEnded(%@, evt):  dragView: %@'.fmt(this, drag, drag.dragView));
                this.set('readyForDrop', false);
            },

            /** SC.DropTarget.prototype */
            computeDragOperations: function(drag, evt, op) {
                // console.log('%@ - computeDragOperations(%@, evt, %@):  dragView: %@'.fmt(this, drag, op, drag.dragView));
                return SC.DRAG_LINK;
            },

            /** SC.DropTarget.prototype */
            performDragOperation: function(drag, op) {
                // console.log('%@ - performDragOperation(%@, %@):  dragView: %@'.fmt(this, drag, op, drag.dragView));

                // This seems like an extremely convoluted way of accessing the data of the drag. Should it
                // not be preset on the drag itself? Perhaps as an Array (since more than one item can be
                // selected and dragged as a group)?
                var dataSource = drag.dataSource,
                    dataMap = drag.dataForType(dataSource.get('reorderDataType')),
                    layer = dataMap.content.objectAt(dataMap.indexes.get('min'));

                // Create a new unsaved query.
                QueryUI.createQuery(layer);

                return SC.DRAG_LINK;
            }
        }),

        primaryQueryBox: SC.View.extend({
            childViews: ['queryTitle', 'removeButton', 'layerNameRow', 'selectRow', 'addFieldRow', 'whereClauseRow', 'secondaryDropZone', 'secondaryQueryBox', 'summariesBox', 'joinTypeIndicator'],
            childViewLayout: SC.View.VERTICAL_STACK,
            childViewLayoutOptions: { paddingBefore: 10, paddingAfter: 10, spacing: 10 },

            classNames: ['qui-box'],
            isVisibleBinding: SC.Binding.oneWay('QueryUI.queryController.content').bool(),
            transitionShow: SC.View.FADE_IN,

            didShowInDocument: function () {
                // Make the SELECT field first responder.
                this.getPath('selectRow.field').becomeFirstResponder();
            },

            layout: { left: 10, right: 10, height: 300, border: 1 },

            queryTitle: SC.LabelView.extend({
                classNames: ['qui-subtitle'],
                isEditable: true,
                layout: { height: 20, left: 10, right: 10 },
                valueBinding: SC.Binding.from('QueryUI.queryController.name')
            }),

            removeButton: SC.ImageButtonView.extend({
                action: 'closeQuery',
                image: 'qui-remove-button',
                layout: { top: 6, height: 24, right: 4, width: 24 },
                target: QueryUI,
                useAbsoluteLayout: true // Don't include this in the automatic child view layout.
            }),

            // A vertical line and icon to indicate the join type.
            joinTypeIndicator: SC.View.extend({
                layerId: 'qui-join-type-indicator',
                isVisibleBinding: SC.Binding.oneWay('QueryUI.queryController.hasJoinLayer'),
                useAbsoluteLayout: true,

                secondaryQueryBoxLayoutBinding: SC.Binding.oneWay('.parentView.secondaryQueryBox.layout'),
                secondaryLayerNameRowLayoutBinding: SC.Binding.oneWay('.parentView.secondaryQueryBox.layerNameRow.layout'),

                layout: function () {
                  var secondaryQueryBoxLayout = this.get('secondaryQueryBoxLayout'), // dynamic
                    secondaryLayerNameRowLayout = this.get('secondaryLayerNameRowLayout'), // dynamic
                    layerNameRowLayout = this.getPath('parentView.layerNameRow.layout'), // static

                    margin = 3,
                    ret = { left: 5, top: layerNameRowLayout.top + layerNameRowLayout.height + margin, height: 0, width: 18 };

                  if (secondaryQueryBoxLayout && secondaryLayerNameRowLayout) {
                    ret.height = secondaryQueryBoxLayout.top + secondaryLayerNameRowLayout.top - ret.top - margin;
                  }

                  return ret;
                }.property('secondaryQueryBoxLayout', 'layerNameRowLayout')
            }),

            layerNameRow: SC.View.extend({
                childViews: ['layerIcon', 'layerName'],
                layout: { left: 2, height: 20, right: 30 }, // Keep this 30 from the right so it doesn't cover the 'X'.

                layerIcon: SC.View.extend({
                    classNames: ['qui-layer-icon'],
                    layout: { centerY: 0, height: 25, width: 26 }
                }),

                layerName: SC.LabelView.extend({
                    classNames: ['qui-layer-title'],
                    layout: { height: 20, left: 26 },
                    valueBinding: 'QueryUI.queryController*layer.name'
                })
            }),

            selectRow: SC.View.extend({
                childViews: ['label', 'field'],
                layout: { left: 20, height: 20 },

                label: SC.LabelView.extend({
                    classNames: ['qui-field-label'],
                    layout: { height: 20, width: 75 },
                    localize: true,
                    value: 'QUI.SelectLabel'
                }),

                field: SC.TextFieldView.extend({
                    hint: 'QUI.SelectFieldHint',
                    layout: { height: 20, left: 80, right: 10 },
                    localize: true,
                    valueBinding: 'QueryUI.queryController.selectString'
                })

                // field: QAC.QueryFieldView.extend({
                //     hint: "QUI.SelectFieldHint",
                //     layout: { height: 20, left: 85, right: 10 },
                //     localize: true,
                //     valueBinding: 'QueryUI.queryController.selectString'
                // })
            }),

            addFieldRow: SC.View.extend({
                childViews: ['label', 'field'],
                layout: { left: 20, height: 20 },

                label: SC.LabelView.extend({
                    classNames: ['qui-field-label'],
                    layout: { height: 20, width: 75 },
                    localize: true,
                    value: 'QUI.AddFieldLabel'
                }),

                field: SC.TextFieldView.extend({
                    hint: 'QUI.AddFieldFieldHint',
                    layout: { height: 20, left: 80, right: 10 },
                    localize: true,
                    valueBinding: 'QueryUI.queryController.addFieldString'
                })

            }),

            whereClauseRow: SC.View.extend({
                childViews: ['label', 'field'],
                layout: { left: 20, height: 80 },

                label: SC.LabelView.extend({
                    classNames: ['qui-field-label'],
                    layout: { height: 20, width: 75 },
                    localize: true,
                    value: 'QUI.WhereLabel'
                }),

                field: SC.TextFieldView.extend({
                    hint: 'QUI.WhereFieldHint',
                    isTextArea: true,
                    layout: { height: 80, left: 80, right: 10 },
                    localize: true,
                    valueBinding: 'QueryUI.queryController*queryStrings.filter_string'
                })

            }),

            secondaryDropZone: SC.View.extend({
                childViews: ['emptyLabel'],
                classNames: ['qui-drop-zone', 'qui-dashed-border'],

                // Visual indication of accepting drops.
                classNameBindings: ['readyForDrop'],
                readyForDrop: false,

                isVisibleBinding: SC.Binding.oneWay('QueryUI.queryController.hasJoinLayer').not(),
                layout: { left: 10, right: 10, height: 140, border: 1 },
                marginBefore: 15,

                emptyLabel: SC.LabelView.extend({
                    classNames: ['qui-drop-zone-label'],
                    layout: { height: 40, left: 10, right: 10, centerY: 0 },
                    localize: true,
                    value: 'QUI.SecondaryDropZoneLabel'
                }),

                /** SC.DropTarget.prototype */
                isDropTarget: true,

                /** @private SC.DropTarget protocol. */
                acceptDragOperation: function (drag, op) {
                    // console.log('%@ - acceptDragOperation(%@, %@):  dragView: %@'.fmt(this, drag, op, drag.dragView));

                    // This seems like an extremely convoluted way of accessing the data of the drag. Should it
                    // not be set on the drag itself? Perhaps as an Array (since more than one item can be
                    // selected and dragged as a group)?
                    var dataSource = drag.dataSource,
                        dataMap = drag.dataForType(dataSource.get('reorderDataType')),
                        layer = dataMap.content.objectAt(dataMap.indexes.get('min'));

                    // Don't accept the same layer twice.
                    return layer && layer !== QueryUI.queryController.get('layer');
                },

                /** SC.DropTarget.prototype */
                dragStarted: function(drag, evt) {
                    // console.log('%@ - dragStarted(%@, evt):  dragView: %@'.fmt(this, drag, drag.dragView));

                    var dataSource = drag.dataSource,
                        dataMap = drag.dataForType(dataSource.get('reorderDataType')),
                        layer = dataMap.content.objectAt(dataMap.indexes.get('min'));

                    // Don't accept the same layer twice.
                    this.set('readyForDrop', layer && layer !== QueryUI.queryController.get('layer'));
                },

                /** SC.DropTarget.prototype */
                dragEnded: function(drag, evt) {
                    // console.log('%@ - dragEnded(%@, evt):  dragView: %@'.fmt(this, drag, drag.dragView));
                    this.set('readyForDrop', false);
                },

                /** SC.DropTarget.prototype */
                computeDragOperations: function(drag, evt, op) {
                    // console.log('%@ - computeDragOperations(%@, evt, %@):  dragView: %@'.fmt(this, drag, op, drag.dragView));
                    return SC.DRAG_LINK;
                },

                /** SC.DropTarget.prototype */
                performDragOperation: function(drag, op) {
                    // console.log('%@ - performDragOperation(%@, %@):  dragView: %@'.fmt(this, drag, op, drag.dragView));

                    // This seems like an extremely convoluted way of accessing the data of the drag. Should it
                    // not be set on the drag itself? Perhaps as an Array (since more than one item can be
                    // selected and dragged as a group)?
                    var dataSource = drag.dataSource,
                        dataMap = drag.dataForType(dataSource.get('reorderDataType')),
                        layer = dataMap.content.objectAt(dataMap.indexes.get('min'));

                    // Connect the layer to the query.
                    QueryUI.queryController.set('joinLayer', layer);

                    return SC.DRAG_LINK;
                }
            }),

            secondaryQueryBox: SC.View.extend({
                childViews: ['relationshipBox', 'layerNameRow', 'selectRow', 'addFieldRow', 'whereClauseRow'],
                childViewLayout: SC.View.VERTICAL_STACK,
                childViewLayoutOptions: { paddingBefore: 10, paddingAfter: 10, spacing: 8 },
                isVisibleBinding: SC.Binding.oneWay('QueryUI.queryController.hasJoinLayer'),
                transitionShow: SC.View.FADE_IN,

                relationshipBox: SC.View.extend({
                    layerId: 'qui-relationship-box',
                    layout: { left: 26, right: 5, height: 130, border: 1 },
                    childViews: ['typeSelect', 'whereClauseRow'],

                    typeSelect: SC.SelectView.extend({
                        layout: { left: 10, height: 24, top: 5, right: 10 },
                        items: [{
                            value: 'primary-geography',
                            title: 'QUI.PrimaryGeographyOption'
                        },{
                            value: 'attribute-join',
                            title: 'QUI.AttributeJoinOption'
                        },{
                            value: 'spatial-join',
                            title: 'QUI.SpatialJoinOption'
                        },{
                            value: 'spatial-select',
                            title: 'QUI.SpatialSelectOption'
                        }],
                        itemValueKey: 'value',
                        itemTitleKey: 'title',
                        localize: true,
                        valueBinding: 'QueryUI.queryController.joinType'
                    }),

                    whereClauseRow: SC.View.extend({
                        childViews: ['label', 'field'],
                        layout: { left: 10, height: 80, top: 40 },

                        label: SC.LabelView.extend({
                            classNames: ['qui-field-label'],
                            layout: { height: 20, width: 75 },
                            localize: true,
                            value: 'QUI.WhereLabel'
                        }),

                        field: SC.TextFieldView.extend({
                            hint: 'QUI.WhereFieldHint',
                            isTextArea: true,
                            layout: { height: 80, left: 85, right: 10 },
                            localize: true,
                            valueBinding: 'QueryUI.queryController.joinClause'
                        })
                    })

                }),

                layerNameRow: SC.View.extend({
                    childViews: ['layerIcon', 'layerName'],
                    layout: { left: 2, height: 20, right: 30 }, // Keep this 30 from the right so it doesn't cover the 'X'.

                    layerIcon: SC.View.extend({
                        classNames: ['qui-layer-icon'],
                        layout: { centerY: 0, height: 25, width: 26 }
                    }),

                    layerName: SC.LabelView.extend({
                        classNames: ['qui-layer-title'],
                        layout: { height: 20, left: 26 },
                        valueBinding: 'QueryUI.queryController*joinLayer.name'
                    }),
                }),

                selectRow: SC.View.extend({
                    childViews: ['label', 'field'],
                    layout: { left: 20, height: 20 },

                    label: SC.LabelView.extend({
                        classNames: ['qui-field-label'],
                        layout: { height: 20, width: 75 },
                        localize: true,
                        value: 'QUI.SelectLabel'
                    }),

                    field: SC.TextFieldView.extend({
                        hint: 'QUI.SelectFieldHint',
                        layout: { height: 20, left: 80, right: 10 },
                        localize: true,
                        valueBinding: 'QueryUI.queryController.joinSelectString'
                    })

                }),

                addFieldRow: SC.View.extend({
                    childViews: ['label', 'field'],
                    layout: { left: 20, height: 20 },

                    label: SC.LabelView.extend({
                        classNames: ['qui-field-label'],
                        layout: { height: 20, width: 75 },
                        localize: true,
                        value: 'QUI.AddFieldLabel'
                    }),

                    field: SC.TextFieldView.extend({
                        hint: 'QUI.AddFieldFieldHint',
                        layout: { height: 20, left: 80, right: 10 },
                        localize: true,
                        valueBinding: 'QueryUI.queryController.joinAddFieldString'
                    })

                }),

                whereClauseRow: SC.View.extend({
                    childViews: ['label', 'field'],
                    layout: { left: 20, height: 80 },

                    label: SC.LabelView.extend({
                        classNames: ['qui-field-label'],
                        layout: { height: 20, width: 75 },
                        localize: true,
                        value: 'QUI.WhereLabel'
                    }),

                    field: SC.TextFieldView.extend({
                        hint: 'QUI.WhereFieldHint',
                        isTextArea: true,
                        layout: { height: 80, left: 80, right: 10 },
                        localize: true,
                        valueBinding: 'QueryUI.queryController*joinQueryStrings.filter_string'
                    })
                })
            }),

            summariesBox: SC.View.extend({
                childViews: ['summariesTitle', 'summariesList', 'firstSummaryButton'],
                classNames: ['qui-box'],
                layout: { height: 110, borderTop: 1 },

                summariesTitle: SC.LabelView.extend({
                    classNames: ['qui-subtitle'],
                    layout: { height: 20, left: 10, right: 10, top: 10 },
                    localize: true,
                    value: 'QUI.SummariesTitle'
                }),

                firstSummaryButton: SC.ButtonView.extend({
                    action: 'addSummary',
                    classNames: ['qui-text-button', 'qui-dashed-border'],
                    layout: { centerY: 15, height: 30, left: 35, right: 35, border: 1 },
                    localize: true,
                    target: QueryUI,
                    title: 'QUI.AddSummaryTitle'
                }),

                summariesList: SC.ScrollView.extend({
                    layout: { top: 40, height: 60, left: 10, right: 10 },

                    contentView: SC.ListView.extend({

                        // Content and selection.
                        contentBinding: SC.Binding.oneWay('summariesController.summariesController.arrangedObjects'),
                        selectionBinding: 'summariesController.summariesController.selection',

                        // SC.CollectionRowDelegate
                        rowSize: 30, // Each row is 30px high.
                        rowSpacing: 0, // Add 0px to each row offset for CSS borders.

                        // Example view.
                        // exampleView: SC.ListItemView
                    })
                })
            })

        }),

        buttonRow: SC.View.extend({
            childViews: ['previewButton', 'runButton'],
            layout: { height: 30 },
            marginBefore: 32,
            // transitionAdjust: SC.View.SMOOTH_ADJUST,
            // transitionAdjustOptions: { timing: 'linear' },

            previewButton: SC.ButtonView.extend({
                action: 'previewQuery',
                controlSize: SC.HUGE_CONTROL_SIZE,
                isEnabledBinding: SC.Binding.oneWay('QueryUI.queryController.isValidQuery'),
                layout: { width: 80, centerX: -45 },
                localize: true,
                target: QueryUI,
                title: 'QUI.PreviewTitle'
            }),

            runButton: SC.ButtonView.extend({
                action: 'runQuery',
                controlSize: SC.HUGE_CONTROL_SIZE,
                isEnabledBinding: SC.Binding.oneWay('QueryUI.queryController.isValidQuery'),
                layout: { width: 80, centerX: 45 },
                localize: true,
                target: QueryUI,
                title: 'QUI.RunTitle'
            })
        })

    }),

    queriesPane: Footprint.PanelPane.extend(SC.DraggablePaneSupport, {
        isModal: false,
        layout: { centerX: 0, centerY: 0, width: QUERIES_PANE_WIDTH, height: QUERIES_PANE_HEIGHT },
        contentView: SC.View.extend({
            childViews: ['queriesTitle', 'removeButton', 'queriesList', 'itemPlaceholder'],

            queriesTitle: SC.LabelView.extend({
                classNames: ['qui-subtitle'],
                layout: { height: 20, left: 20, right: 10, top: 10 },
                localize: true,
                value: 'QUI.QueriesTitle'
            }),

            removeButton: SC.ImageButtonView.extend({
                action: 'closeQueriesPane',
                image: 'qui-remove-button',
                layout: { top: 6, height: 24, right: 4, width: 24 },
                target: QueryUI
            }),

            queriesList: SC.ScrollView.extend({
                layout: { top: 38, bottom: QUERIES_PANE_MARGIN, left: QUERIES_PANE_MARGIN, right: QUERIES_PANE_MARGIN },

                contentView: SC.ListView.extend({
                    contentBinding: SC.Binding.oneWay('QueryUI.allQueriesController.arrangedObjects'),
                    exampleView: QueryUI.QueryItemView
                })
            }),

            itemPlaceholder: SC.LabelView.extend({
                classNames: ['qui-item-placeholder'],
                isVisibleBinding: SC.Binding.oneWay('QueryUI.allQueriesController.length').not(),
                layout: { height: 25, left: QUERIES_PANE_MARGIN, right: QUERIES_PANE_MARGIN, top: 38 },
                localize: true,
                value: 'QUI.EmptyQueriesHolder'
            })
        })
    }),

    summaryPane: Footprint.PanelPane.extend({
        layout: { centerX: 0, centerY: 0, width: SUMMARY_PANE_WIDTH, height: SUMMARY_PANE_HEIGHT },

        contentView: SC.View.extend({
            childViews: ['summaryTitle', 'removeButton', 'chooseLayerTitle', 'summarizeByTitle', 'groupByTitle', 'chooseLayersList', 'summarizeField', 'groupByField', 'runButton', 'resultsTable', 'histogram'],

            summaryTitle: SC.LabelView.extend({
                classNames: ['qui-subtitle'],
                isEditable: true,
                layout: { height: 20, left: 20, right: 10, top: 10 },
                valueBinding: SC.Binding.from('QueryUI.summaryController.name')
            }),

            removeButton: SC.ImageButtonView.extend({
                action: 'closeSummary',
                image: 'qui-remove-button',
                layout: { top: 6, height: 24, right: 4, width: 24 },
                target: QueryUI
            }),

            chooseLayerTitle: SC.LabelView.extend({
              classNames: ['qui-field-heading'],
              layout: { height: 20, left: SUMMARY_PANE_MARGIN, width: SUMMARY_COLUMN_WIDTH, top: 38 },
              localize: true,
              value: 'QUI.ChooseLayerTitle'
            }),

            summarizeByTitle: SC.LabelView.extend({
              classNames: ['qui-field-heading'],
              layout: { height: 30, left: SUMMARY_PANE_MARGIN + SUMMARY_COLUMN_WIDTH + SUMMARY_COLUMN_SPACING, width: SUMMARY_COLUMN_WIDTH, top: 38 },
              localize: true,
              value: 'QUI.SummarizeByTitle'
            }),

            groupByTitle: SC.LabelView.extend({
              classNames: ['qui-field-heading'],
              layout: { height: 30, right: SUMMARY_PANE_MARGIN, width: SUMMARY_COLUMN_WIDTH, top: 38 },
              localize: true,
              value: 'QUI.GroupByTitle'
            }),

            chooseLayersList: SC.ScrollView.extend({
              classNames: [],
              layout: { height: 90, left: SUMMARY_PANE_MARGIN, width: SUMMARY_COLUMN_WIDTH, top: 62 },
              contentView: SC.ListView.extend({

                // Content and selection.
                contentBinding: SC.Binding.oneWay('QueryUI.summaryLayersController.arrangedObjects'),
                // selectionBinding: 'MyApp.myArrayController.selection',

                // SC.CollectionRowDelegate
                rowSize: 30, // Each row is 30px high.
                rowSpacing: 0, // Add 0px to each row offset for CSS borders.

                // Example view.
                // exampleView: SC.ListItemView

              })
            }),

            summarizeField: SC.TextFieldView.extend({
                classNames: [],
                hint: 'QUI.SummarizeFieldHint',
                isTextArea: true,
                layout: { height: 90, left: SUMMARY_PANE_MARGIN + SUMMARY_COLUMN_WIDTH + SUMMARY_COLUMN_SPACING, width: SUMMARY_COLUMN_WIDTH, top: 62 },
                localize: true,
                valueBinding: SC.Binding.from('QueryUI.summaryController.summarizeByStatement')
            }),

            groupByField: SC.TextFieldView.extend({
                classNames: [],
                hint: 'QUI.GroupByFieldHint',
                isTextArea: true,
                layout: { height: 90, right: SUMMARY_PANE_MARGIN, width: SUMMARY_COLUMN_WIDTH, top: 62 },
                localize: true,
                valueBinding: SC.Binding.from('QueryUI.summaryController.groupByStatement')
            }),

            runButton: SC.ButtonView.extend({
                action: 'runSummary',
                controlSize: SC.HUGE_CONTROL_SIZE,
                isEnabledBinding: SC.Binding.oneWay('QueryUI.summaryController.isValidSummary'),
                layout: { top: 168, width: 110, right: SUMMARY_PANE_MARGIN, height: 30 },
                localize: true,
                target: QueryUI,
                title: 'QUI.RunSummaryTitle'
            }),

            resultsTable: SC.View.extend({
              classNames: [],
              layout: { height: 30, left: 10, right: 10, top: 100 }
            }),

            histogram: SC.View.extend({
              classNames: [],
              layout: { height: 30, left: 10, right: 10, top: 100 }
            })
        })
    })

});
