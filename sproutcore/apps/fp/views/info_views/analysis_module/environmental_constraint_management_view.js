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


sc_require('views/info_views/analysis_module/label_result_views');
sc_require('views/editable_model_string_view');
sc_require('views/updating_overlay_view');
sc_require('views/info_views/built_form/editable_input_field_view');

Footprint.EditableConstraintPercentFieldView = SC.View.extend({
    childViews: ['nameView', 'priorityView', 'percentView'],
    nameValue:null,
    priorityValue: null,
    percentValue: null,

    nameView: SC.LabelView.extend({
        layout: {left: 0.01, width: 0.5, top: 4, bottom: 1},
        valueBinding: SC.Binding.oneWay('.parentView.nameValue'),
        textAlign: SC.ALIGN_LEFT,
        backgroundColor: '#f7f7f7'
    }),
    priorityView:  Footprint.EditableFloatFieldItemView.extend({
        classNames: ['footprint-editable-content-view', 'footprint-11font-title-view'],
        textAlign: SC.ALIGN_CENTER,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        layout: {left: 0.51, width: 0.24, top: 3},
        isPercent: NO,
        contentValueKey: 'priority'
    }),
    percentView:  Footprint.EditableFloatFieldItemView.extend({
        classNames: ['footprint-editable-content-view', 'footprint-11font-title-view'],
        textAlign: SC.ALIGN_CENTER,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        layout: {left: 0.76, width: 0.25, top: 3},
        isPercent: YES,
        contentValueKey: 'percent',
    })
});


Footprint.EnvironmentalConstraintModuleManagementView = SC.View.extend({

    classNames: "footprint-environmental-contraints-management-view".w(),
    childViews: ['titleContainerView', 'headerLabelView', 'environmentalConstraintsView', 'saveButtonView', 'updatingStatusView'],

    content: null,
    contentBinding: SC.Binding.oneWay('Footprint.environmentalConstraintUpdaterToolEditController.content'),

    recordsAreUpdating: null,
    recordsAreUpdatingBinding: SC.Binding.oneWay('Footprint.environmentalConstraintUpdaterToolEditController.recordsAreUpdating'),

    isOverlayVisible: function () {
        var recordsAreUpdating = this.get('recordsAreUpdating');
        if (recordsAreUpdating) {
            return recordsAreUpdating
        }
        return NO
    }.property('recordsAreUpdating').cacheable(),

    titleContainerView: SC.ContainerView.extend({
        classNames: "footprint-analytic-module-title-container-view ".w(),
        childViews: ['titleView'],
        layout: {top: 10, left: 10, height: 40, right: 30},
        backgroundColor: 'green',
        titleView: SC.LabelView.extend({
            classNames: "footprint-analytic-module-title-view footprint-header".w(),
            layout: {top: 2, left: 3, right: 3, bottom: 2},
            scenarioName: null,
            scenarioNameBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.name'),
            value: function() {
                return 'Manage  %@ \n Environmental Constraints'.fmt(this.get('scenarioName'));
            }.property('scenarioName'),
            textAlign: SC.ALIGN_LEFT
        })
    }),

    headerLabelView: SC.View.extend({
        layout: {top: 50, height: 20, left: 10, right: 30},
        childViews: ['nameTitle', 'priorityTitle', 'percentTitle'],
        backgroundColor: '#e1e1e1',
        nameTitle: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            layout: {width: 0.5, top: 3},
            value: 'Constraint Layer Name',
            textAlign: SC.ALIGN_CENTER
        }),
        priorityTitle: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            layout: {left: 0.5, width: 0.2, top: 3},
            value: 'Priority',
            textAlign: SC.ALIGN_CENTER
        }),
        percentTitle: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            layout: {left: 0.7, width: 0.3, top: 3},
            value: '% Constrained',
            textAlign: SC.ALIGN_CENTER,
        })
    }),

    environmentalConstraintsView: SC.ScrollView.extend(SC.ContentDisplay,{
        classNames: ['footprint-environmental-constraint-percent-scroll-view'],
        layout: {right: 30, left: 10, top: 70, bottom:.2},
        contentBinding: SC.Binding.oneWay('.parentView*content.firstObject.environmental_constraint_percents'),
        contentDisplayProperties: ['contentFirstObject'],

        contentView: SC.SourceListView.extend(SC.ContentDisplay, {
            classNames: ['footprint-environmental-constraint-percent-source-list-view'],
            rowHeight: 20,
            isEditable: YES,
            isEnabledBinding: SC.Binding.oneWay('.content').bool(),
            contentDisplayProperties: ['content'],
            contentBinding: SC.Binding.from('.parentView.parentView.content'),

            exampleView: Footprint.EditableConstraintPercentFieldView.extend({
                nameValueBinding: '*content.db_entity.name'
            })
        })
    }),
    saveButtonView: SC.ButtonView.design({
        layout: {bottom:.1, left: 20, height: 24, width: 60},
        title: 'Update',
        action: 'doAnalysisToolUpdate',
        isCancel: YES
    }),
    updatingStatusView: Footprint.UpdatingOverlayView.extend({
        layout: { left: 100, right: 30, bottom:.1, height: 27},
        isOverlayVisibleBinding: SC.Binding.oneWay('.parentView.isOverlayVisible'),
        previousStatus: NO,
        title: 'Updating..',

        justUpdatedObserver: function() {
            if (this.didChangeFor('justUpdatedObserver', 'isOverlayVisible')) {
                if (this.get('isOverlayVisible') == YES && this.get('previousStatus') == NO) {
                    this.set('previousStatus', YES);
                    this.set('justUpdated', NO);
                }
                else if (this.get('isOverlayVisible') == NO && this.get('previousStatus') == YES) {
                    // Indicate just saved if we are still showing the last saved content
                    this.set('justUpdated', YES);
                    this.set('previousStatus', NO);
                    this.set('Footprint.environmentalConstraintUpdaterToolEditController.recordsAreUpdating', NO);
                }
            }
        }.observes('.isOverlayVisible')
    })
});
