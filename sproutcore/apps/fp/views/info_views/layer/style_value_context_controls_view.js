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


Footprint.StyleValueContextControlsView = SC.View.extend({
    childViews: ['copyButtonView', 'pickIdView', 'deleteButtonView', 'symbolSelectorView', 'valueView', 'selectAllToggleButtonView'],
    recordType: Footprint.StyleValueContext,
    content: null,
    selection: null,
    /***
     * The Footprint.StyleAttribute containing the StyleValueContexts. It is used to determined
     * if the attribute is a related object and thus to show available related objects.
     * This is not used if editing Footprint.ZoomLevelStyles
     */
    styleAttribute: null,
    /***
     * Bind to a controller that holds Footprint.StyleValueContexts so that we can manage select all
     */
    styleValueContextsController: null,

    copyButtonView: Footprint.AddButtonView.extend({
        layout: {left: 0, width: 16, top: 4, height: 16 },
        action: 'doAddStyleValueContext',
        // We want to clone the selected item
        // Or simply create if nothing is selected
        contentBinding: SC.Binding.oneWay('.parentView*selection.firstObject'),
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        styleAttribute: null,
        styleAttributeBinding: SC.Binding.oneWay('.parentView.styleAttribute'),
        noRelatedRecordType: null,
        noRelatedRecordTypeBinding: SC.Binding.oneWay('*styleAttribute.relatedRecordType').not(),
        isVisibleBinding: SC.Binding.oneWay('.noRelatedRecordType'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
    }),

    // For related record attributes, this offers up the ids that aren't styled
    // This is always used in place of the copyButtonView
    pickIdView: Footprint.LabelSelectView.extend({
        layout: {left: 0, width: 18, top: 2, height: 20 },
        contentBinding: SC.Binding.oneWay('Footprint.styleValueContextUnrepresentedValuesController.arrangedObjects'),
        icon: 'add-icon',
        itemTitleKey: 'name',
        selectionAction: 'doAddStyleValueContextFromId',
        nullTitle: 'Add New Building Use',
        styleAttribute: null,
        styleAttributeBinding: SC.Binding.oneWay('.parentView.styleAttribute'),
        isEnabledBinding: SC.Binding.oneWay('.content'),
        isVisibleBinding: SC.Binding.oneWay('*styleAttribute.relatedRecordType')
    }),

    deleteButtonView: Footprint.DeleteButtonView.extend({
        layout: { left: 24, width: 16, top: 4, height: 16},
        action: 'doPromptDeleteRecord',
        // We want to clone the selected item
        contentBinding: SC.Binding.oneWay('.parentView*selection.firstObject'),
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        isEnabledBinding: SC.Binding.oneWay('.content').bool()
    }),

    /**
     * Allows the user to update the one or more selected Footprint.StyleValueContext records
     */
    symbolSelectorView: SC.SegmentedView.extend({
        layout: {left: 40, width: 160},
        classNames: ['footprint-segmented-button-view', '.ace.sc-regular-size.sc-segment-view', 'sc-button-label'],
        itemValueKey: 'value',
        itemTitleKey: 'value',
        itemActionKey: 'action',
        itemToolTipKey: 'toolTip',
        selectSegmentWhenTriggeringAction: YES,

        items: [
            SC.Object.create({value: '<', toolTip: 'Update selected values less than', action: 'updateStyleContextSymbol'}),
            SC.Object.create({value: '<=', toolTip: 'Update selected values less than or equal to', action: 'updateStyleContextSymbol'}),
            SC.Object.create({value: '=', toolTip: 'Update selected values to equal to', action: 'updateStyleContextSymbol'}),
            SC.Object.create({value: '>=', toolTip: 'Update selected values to greater than or equal to', action: 'updateStyleContextSymbol'}),
            SC.Object.create({value: '>', toolTip: 'Update selected values to greater than', action: 'updateStyleContextSymbol'})
        ],
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView*selection'),
        contentStatus: null,
        contentStatusBinding: SC.Binding.oneWay('.parentView*content.status'),
        contentValueKey: 'symbol',
        // Needed by Footprint.pluralContentValueProperty but not used
        refreshValue: null,
        value: Footprint.pluralContentValueProperty
    }),

    valueView: Footprint.EditableModelStringView.extend({
        layout: {left: 200, width: 50, height: 24},
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView*selection').transform(function(selection) {
            return selection && selection.get('length') == 1 ? selection.get('firstObject') : null;
        }),
        contentValueKey: 'value'
    }),

    selectAllToggleButtonView: Footprint.SelectAllToggleButtonInfoView.extend({
        layout: {width: 80, right: 0, height: 24, centerY: 0},
        classNames: 'footprint-style_editor-select-all-view'.w(),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        // Bind to the controller so that we can use its selectAll property
        contentBinding: SC.Binding.oneWay('.parentView.styleValueContextsController'),
        contentValueKey: 'selectAll'
    })
});
