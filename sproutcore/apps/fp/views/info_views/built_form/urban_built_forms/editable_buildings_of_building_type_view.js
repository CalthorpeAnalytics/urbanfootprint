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
sc_require('views/info_views/built_form/editable_built_form_source_list_view');
sc_require('views/info_views/built_form/editable_built_form_select_view');
sc_require('views/action_views/normalize_percents_button_view');

Footprint.EditableBuildingsOfBuildingTypeView = SC.View.extend({

    classNames: ['footprint-editable-building-type-attributes-view'],
    childViews:'titleView duAcreTitleView empAcreTitleView usePctTitleView buildingPercentScrollView'.w(),
    content: null,

    titleView: SC.LabelView.extend({
        value: 'Included Buildings in Building Type',
        layout: {left: 30, width: 250, height: 24, top: 0}
    }),

    duAcreTitleView: SC.LabelView.extend({
        classNames: ['footprint-editable-building-type-attributes-du-label'],
        layout: {width: 50, height: 22, left: 458, top: 10},
        value: 'Du/Acre'
    }),

    empAcreTitleView: SC.LabelView.extend({
        classNames: ['footprint-editable-building-type-attributes-emp-label'],
        layout: {width: 50, height: 22, left: 500, top: 10},
        value: 'Emp/Acre'
    }),

    usePctTitleView: SC.LabelView.extend({
        classNames: ['footprint-editable-building-type-attributes-use-pct-label'],
        layout: {width: 50, height: 22, left: 575, top: 10},
        value: 'Use Pct'
    }),

    buildingPercentScrollView: SC.ScrollView.extend({
        classNames: ['footprint-building-type-percent-scroll-view'],
        layout: {left: 40, width: 600, top: 25, bottom: 70},

        contentView: SC.SourceListView.extend({
            isEnabledBinding: SC.Binding.oneWay('.content').bool(),
            rowHeight: 20,
            isEditable: YES,
            actOnSelect: NO,
            canEditContent: YES,
            canDeleteContent: YES,
            canReorderContent: YES,

            contentBinding: SC.Binding.oneWay('.parentView.parentView.parentView.content'),

            exampleView: Footprint.EditableBuiltFormSourceListView.extend({
                subclassedContentBinding:SC.Binding.oneWay('*content.subclassedComponent')
            })
        })
    }),

    builtFormsLabelSelectView: Footprint.LabelSelectView.extend({
        layout: {left: 38, width: 500, bottom: 30, height: 24},
        contentBinding: SC.Binding.oneWay('Footprint.buildingsEditController.arrangedObjects'),
        itemTitleKey: 'name',
        selectionAction: 'doPickComponentPercent',
        nullTitle: 'Add a Building to the mix'
    }),

    // BuiltForm Editing disabled
    /*
    normalizePercentsView: Footprint.NormalizePercentsButtonView.extend({
        layout: {left: 575, width: 50, bottom:30, height: 24},
        // This is here to sent to the action handler
        contentBinding: SC.Binding.oneWay('.parentView*content'),
    })
    */
});
