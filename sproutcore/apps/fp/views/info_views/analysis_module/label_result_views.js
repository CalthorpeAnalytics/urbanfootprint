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


Footprint.TopLabeledResultView = SC.View.extend({
    classNames: "footprint-top-labeled-result-view".w(),
    childViews: ['titleSpaceView', 'valueSpaceView'],
    result: null,
    title: null,
    columnName: null,

    columnValue: function() {
        var content = this.get('result')
        var column_name = this.get('columnName')
        if (!content)
            return '--';
        var value = parseFloat(content[column_name]).toFixed(0)

        return value ? d3.format(',f')(value) : '--';
    }.property('result', 'columnName').cacheable(),

    titleSpaceView: SC.View.extend({
        classNames: "footprint-top-labeled-result-title-view".w(),
        childViews: ['titleView'],
        title:null,
        titleBinding: SC.Binding.oneWay('.parentView.title'),
        layout: {height: 0.5},

        titleView: SC.LabelView.extend({
            classNames: "footprint-top-labeled-result-title-space-view".w(),
            layout: {top:2, bottom: 2, left:5},
            valueBinding: SC.Binding.oneWay('.parentView.title')
        })
    }),

    valueSpaceView: SC.View.extend({
        classNames: "footprint-top-labeled-result-value-space-view".w(),
        childViews: ['valueView'],
        layout: {top: 0.5},
        columnValue: null,
        columnValueBinding: SC.Binding.oneWay('.parentView.columnValue'),
        valueView: SC.LabelView.extend({
            classNames: "footprint-top-labeled-result-value-view".w(),
            valueBinding: SC.Binding.oneWay('.parentView.columnValue'),
            textAlign: SC.ALIGN_CENTER
        })
    })
});



Footprint.TwoValueLabeledResultView = SC.View.extend({
    classNames: "footprint-two-value-labeled-result-view".w(),
    childViews: ['contentView'],

    result: null,
    subTitle1: null,
    subTitle2: null,
    title: null,
    column1Name: null,
    column2Name: null,

    column1Value: function() {
        var content = this.get('result');
        var column_name = this.get('column1Name');
        if (!content)
            return '--';
        var value = parseFloat(content[column_name]).toFixed(0)

        return value ? d3.format(',f')(value) : '--';
    }.property('result', 'column1Name').cacheable(),

    column2Value: function() {
        var content = this.get('result');
        var column_name = this.get('column2Name');
        if (!content)
            return '--';
        var value = parseFloat(content[column_name]).toFixed(0)

        return value ? d3.format(',f')(value) : '--';
    }.property('result', 'column2Name').cacheable(),

    contentView: SC.View.extend({
        classNames: "footprint-split-bottom-label-view".w(),
        childViews: ['titleView', 'subtitle1View', 'value1View', 'subtitle2View', 'value2View'],

        title: null,
        column1Value: null,
        subtitle1: null,
        column2Value: null,
        subtitle2: null,

        titleBinding: SC.Binding.oneWay('.parentView.title'),
        column1ValueBinding: SC.Binding.oneWay('.parentView.column1Value'),
        subtitle1Binding: SC.Binding.oneWay('.parentView.subTitle1'),
        column2ValueBinding: SC.Binding.oneWay('.parentView.column2Value'),
        subtitle2Binding: SC.Binding.oneWay('.parentView.subTitle2'),

        titleView: SC.LabelView.extend({
            classNames: "footprint-top-labeled-result-title-space-view".w(),
            layout: {top:0, height: 0.34, centerY: 0},
            valueBinding: SC.Binding.oneWay('.parentView.title'),
            textAlign: SC.ALIGN_CENTER
        }),

        subtitle1View: SC.LabelView.extend({
            classNames: "footprint-top-labeled-result-subtitle-space-view".w(),
            layout: {top:.69, height:.31, width: 0.5, left: 0, centerY: 0},
            valueBinding: SC.Binding.oneWay('.parentView.subtitle1'),
            textAlign: SC.ALIGN_CENTER
        }),

        value1View: SC.LabelView.extend({
            classNames: "footprint-top-labeled-result-value-view".w(),
            layout: {top: 0.34, height: 0.33, width: 0.5, left: 0, centerY: 0},
            valueBinding: SC.Binding.oneWay('.parentView.column1Value'),
            textAlign: SC.ALIGN_CENTER
        }),

        subtitle2View: SC.LabelView.extend({
            classNames: "footprint-top-labeled-result-subtitle-space-view".w(),
            layout: {top:.69, height:.31, width: 0.5, left: 0.5, centerY: 0},
            valueBinding: SC.Binding.oneWay('.parentView.subtitle2'),
            textAlign: SC.ALIGN_CENTER
        }),

        value2View: SC.LabelView.extend({
            classNames: "footprint-top-labeled-result-value-view".w(),
            layout: {top: 0.34, height: 0.33, width: 0.49, left: 0.5, centerY: 0},
            valueBinding: SC.Binding.oneWay('.parentView.column2Value'),
            textAlign: SC.ALIGN_CENTER
        })
    })
});
