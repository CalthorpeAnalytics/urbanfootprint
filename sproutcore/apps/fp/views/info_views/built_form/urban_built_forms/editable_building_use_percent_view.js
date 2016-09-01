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


sc_require('views/info_views/built_form/editable_input_field_view');
sc_require('views/info_views/built_form/editable_use_percent_field_view');

Footprint.EditableBuildingUsePercentView = SC.View.extend({
    classNames: ['footprint-editable-building-use-percents-view'],
    childViews: ['nameTitleView', 'titlesView', 'buildingUsePercentScrollView'],

    // The editable BuildingUsePercents of a BuiltForm
    content: null,
    allContent: null,

    nameTitleView: SC.LabelView.extend({
        classNames: ['footprint-bold-title-view'],
        value: 'Building Uses',
        layout: {left: 0, height: 24}
    }),

    titlesView: SC.View.extend({
        layout: {height: 24, top: 25},
        backgroundColor: '#E0E0E0',
        childViews:'sqftTitleView efficiencyTitleView percentTitleView'.w(),

        sqftTitleView: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            textAlign: SC.ALIGN_CENTER,
            value: 'Square Feet Per Unit',
            layout: {left: .2, width: 60}
        }),
        efficiencyTitleView: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            textAlign: SC.ALIGN_CENTER,
            value: 'Efficiency (%)',
            layout: {left: .5, width: 60}
        }),
        percentTitleView: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            value: 'Use Percent',
            textAlign: SC.ALIGN_CENTER,
            layout: {right: 0, width: 60}
        })
    }),

    buildingUsePercentScrollView: SC.ScrollView.extend({
        classNames: ['footprint-building-use-percent-scroll-view'],
        layout: {top: 49, bottom: 30},
        contentBinding: SC.Binding.oneWay('Footprint.buildingUseDefinitionsEditController.arrangedObjects'),

        contentView: SC.ListView.extend({
            classNames: ['footprint-building-use-percent-source-list-view'],
            rowHeight: 40,
            isEditable: NO,
            actOnSelect: NO,
            content:null,
            contentBinding: SC.Binding.oneWay('.parentView.parentView.parentView.content'),

            exampleView: Footprint.EditableUsePercentFieldView
        })
    }),

    // Editing of BuiltForms is disabled
    /*
    buildingUseLabelSelectView: Footprint.LabelSelectView.extend({
        layout: {left: 10, bottom: 0, height: 24, right: 10},
        contentBinding: SC.Binding.oneWay('Footprint.buildingUseDefinitionsController.arrangedObjects'),
        itemTitleKey: 'name',
        selectionAction: 'doPickComponentPercent',
        nullTitle: 'Add New Building Use'
    })
    */
});
