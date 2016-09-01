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

sc_require('views/info_views/analysis_module/analysis_module_view');
sc_require('views/section_views/built_form_section_view');
sc_require('views/info_views/built_form/editable_input_field_view');
sc_require('views/tool_segmented_button_view');
sc_require('views/remove_button_view');

Footprint.AgricultureBuilderManagementView = SC.View.extend({

    classNames: "footprint-agriculture-builder-module-management-view".w(),
    childViews: ['overlayView', 'toggleButtons', 'manageModuleView', 'activeBuiltFormSummaryView','featureBarView', 'builtFormSectionView'],

    activeLayer: null,
    activeLayerBinding: SC.Binding.oneWay('Footprint.layerActiveController.content'),

    activeLayerStatus: null,
    activeLayerStatusBinding: SC.Binding.oneWay('Footprint.layerActiveController*content.status'),

    selection: null,
    selectionBinding: SC.Binding.oneWay('Footprint.agricultureBuiltFormCategoriesTreeController.selection'),

    selectionFirstObject: null,
    selectionFirstObjectBinding: SC.Binding.oneWay('*selection.firstObject'),

    // Shows saving progress. Normally this is done in the analysis_module_section_view
    // but we need to also track saving the Features
    overlayView: Footprint.OverlayView.extend({
        contentBinding: SC.Binding.oneWay('Footprint.featuresEditController.content'),
        statusBinding:SC.Binding.oneWay('Footpritn.featuresEditController.status')
    }),

    toggleButtons: SC.View.extend({
        layout: {left: 5, top: 8, height: 16, width: 300},
        childViews: ['toggleView', 'redevelopmentToggleView'],
        // Only show this view if we have a selected a Layer that has a Builder
        isVisibleBinding: SC.Binding.oneWay('Footprint.layerActiveController.isBuilderView'),

        toggleView: Footprint.CheckboxInfoView.extend({
            layout: {left: 0, width: 120, top: 0},
            buttonLayout: {top:0, left:0, width:20},
            titleLayout: {top:0, left:20},
            classNames: ['featurer-bar-toggle'],
            title: 'Clear Base Condition',
            toolTip: 'Toggles whether the applied built form will completely clear base condition',
            valueBinding: 'Footprint.agricultureFeatureDefaultsController*content.update.clear_flag'
        }),

        redevelopmentToggleView: Footprint.CheckboxInfoView.extend({
            layout: {left: 130, width: 120, top: 0},
            buttonLayout: {top:0, left:0, width:20},
            titleLayout: {top:0, left:20},
            classNames: ['featurer-bar-toggle'],
            title: 'Redevelopment Flag',
            toolTip: 'If checked, treat the painted features as redevelopment, meaning the existing land use is not considered when calculated the change in du, emp, etc.',
            valueBinding: 'Footprint.agricultureFeatureDefaultsController*content.update.redevelop_flag'
        })
    }),

    featureBarView: SC.View.extend({
        layout: { top: 24, height: 46 },
        childViews: ['paramsView', 'buttonsView'],
        classNames: ['featurer-bar'],

        paramsView: SC.View.extend({
            layout: {left: 0, top: 0, height: 42},
            childViews: ['param1View', 'param2View', 'param3View'],

            titleLayout: {top: 0, left: 0, height: 14},
            inputLayout: {top: 16, left: 0, height: 20, width: 60},
            symbolLayout: {top: 20, left: 65, height: 12},

            param1View: Footprint.PercentInfoView.extend({
                layout: {left: 0, width: 100, top: 5},
                titleLayout: SC.outlet('parentView.titleLayout'),
                inputLayout: SC.outlet('parentView.inputLayout'),
                symbolLayout: SC.outlet('parentView.symbolLayout'),
                classNames: ['featurer-bar-param1'],
                valueSymbol: '%',
                title: 'Develop.',
                minimum: 0,
                maximum: 100,
                step: 1,
                toolTip: 'Sets the percent of the developable area that will receive new development. The area not receiving new development will remain as the base condition.',
                displayValue: null,
                displayValueBinding: SC.Binding.from('Footprint.agricultureFeatureDefaultsController*content.update.dev_pct'),
                value: function (propKey, value) {
                    if (value !== undefined) {
                        this.set('displayValue', value / 100);
                        return value;
                    }
                    return this.get('displayValue') * 100;
                }.property('displayValue').cacheable()
            }),

            param2View: Footprint.PercentInfoView.extend({
                layout: {left: 85, width: 100, top: 5},
                titleLayout: SC.outlet('parentView.titleLayout'),
                inputLayout: SC.outlet('parentView.inputLayout'),
                symbolLayout: SC.outlet('parentView.symbolLayout'),
                classNames: ['featurer-bar-param2'],
                valueSymbol: '%',
                title: 'Density',
                toolTip: 'Sets the percentage reduction in the applied density of the built form.',
                minimum: 0,
                maximum: 100,
                step: 1,
                displayValue: null,
                displayValueBinding: SC.Binding.from('Footprint.agricultureFeatureDefaultsController*content.update.density_pct'),
                value: function (propKey, value) {
                    if (value !== undefined) {
                        this.set('displayValue', value / 100);
                        return value;
                    }
                    return this.get('displayValue') * 100;
                }.property('displayValue').cacheable()
            }),

            param3View: Footprint.PercentInfoView.extend({
                layout: {left: 170, width: 100, top: 5},
                titleLayout: SC.outlet('parentView.titleLayout'),
                inputLayout: SC.outlet('parentView.inputLayout'),
                symbolLayout: SC.outlet('parentView.symbolLayout'),
                classNames: ['featurer-bar-param3'],
                valueSymbol: '%',
                title: 'Gross/Net',
                toolTip: 'Sets the percentage of developable area that will receive the applied built form density',
                minimum: 0,
                maximum: 100,
                step: 1,
                displayValue: null,
                displayValueBinding: SC.Binding.from('Footprint.agricultureFeatureDefaultsController*content.update.gross_net_pct'),
                value: function (propKey, value) {
                    if (value !== undefined) {
                        this.set('displayValue', value / 100);
                        return value;
                    }
                    return this.get('displayValue') * 100;
                }.property('displayValue').cacheable()
            })
        }),
    }),

    activeBuiltFormSummaryView: SC.View.extend({
        layout: { top: 70, height: 85 },
        classNames: ['footprint-active-built-form-summary-view'],
        childViews: ['titleView', 'nameView', 'styleView'],
        backgroundColor: '#f2f1ef',
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.selectionFirstObject'),

        titleView: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            layout: {left: 5, height: 14, top: 3},
            value: 'Active Built Form:'
        }),

        nameView: SC.LabelView.extend({
            classNames: ['footprint-active-built-form-name-view', 'toolbar'],
            layout: {left: 5, width:.95, height: 20, top: 18},
            valueBinding: SC.Binding.oneWay('.parentView*content.name'),
            textAlign: SC.ALIGN_CENTER

        }),

        styleView: SC.LabelView.extend(Footprint.StyleRenderMixin, {
            classNames: ['footprint-active-built-form-medium'],
            layout: {left: 5, width:60, height: 30, top: 45},
            displayProperties:['style'],
            renderStyleInChildElement: NO,

            /***
             * The Footprint.Style. This comes from the LayerStyle StyleAttribute for the id attribute
             */
            style: null,
            styleBinding: SC.Binding.oneWay('.parentView*content.medium.style_attributes').transform(function(styleAttributes) {
                if (!styleAttributes)
                    return null;
                return styleAttributes.filterProperty('attribute', 'id').getPath('firstObject.style_value_contexts.firstObject.style');
            }),

            render: function(context) {
                sc_super();
                // Style swab
                this.renderStyle(context);
            },
            update: function($context) {
                // Style swab
                this.updateStyle($context);
            }
        }),
    }),

    builtFormSectionView: Footprint.BuiltFormSectionView.extend({
        layout: {top: 155},
        builtFormsBinding: SC.Binding.from('Footprint.agricultureBuiltFormCategoriesTreeController'),
        builtFormSelectionBinding: SC.Binding.from('Footprint.agricultureBuiltFormCategoriesTreeController.selection'),
        builtFormContentBinding: SC.Binding.oneWay('Footprint.agricultureBuiltFormCategoriesTreeController.arrangedObjects'),
        builtFormSetSelectionBinding: SC.Binding.from('Footprint.agricultureBuiltFormSetsController.selection'),
        builtFormSetContentBinding: SC.Binding.from('Footprint.agricultureBuiltFormSetsController.content'),
        builtFormSetStatusBinding: SC.Binding.from('Footprint.agricultureBuiltFormSetsController.status'),
        activeBuiltFormBinding: SC.Binding.oneWay('Footprint.agricultureBuiltFormActiveController.content'),
        menuItems: [
            // View and edit the selected item's attributes
            { title: 'Manage Agriculture Types', action: 'doManageAgricultureTypes'}
        ]
    })
});
