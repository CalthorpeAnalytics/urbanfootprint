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

Footprint.EditableBuildingUsePercentFieldView = Footprint.EditableModelStringView.extend(SC.Control, {
    classNames: ['footprint-editable-content-view'],
    backgroundColor: '#F8F8F8',

    renderDelegateName:'ellipsesLabelRenderDelegate',
    buildingUsePercents:null,
    content: null,
    allContent: null,
    contentValueKey: null,
    name: null,
    nameBinding: SC.Binding.oneWay('.parentView.name'),

    // Getter/Setter. The Setter creates a new BuildingUsePercent if the user
    // puts in a percent where a BuildingUsePercent is not yet defined.
    value: function(propertyPath, value) {
        var buildingUsePercent = this.get('content');
        var allContent = this.get('allContent');
        var contentValueKey = this.get('contentValueKey');
        if (value) {
            if (buildingUsePercent) {
                buildingUsePercent.set(contentValueKey, value);
            }
            else {
                // The user is setting a property of a BuildingUseProperty that was
                // previously undefined. Create a record and add it to the
                // other BuildingUsePercents.
                var store = this.getPath('buildingUsePercents.store');
                var buildingUseDefinition = store.find(SC.Query.local(
                    Footprint.BuildingUseDefinition, {
                        conditions: 'name = {name}',
                        name: this.get('name')
                    })).firstObject();

                var buildingAttributeSet = this.getPath('buildingUsePercents.parentRecord');
                // Get the parent BuildingUsePercent if it already exists
                var parentBuildingUsePercent = buildingAttributeSet.buildingUsePercentOfBuildingUseDefinition(buildingUseDefinition.get('category'));
                // Create the new BuildingUsePercent.
                var newBuildingUsePercent = this.get('buildingUsePercents').createNestedRecord(
                    Footprint.BuildingUsePercent,
                    {
                        building_use_definition: buildingUseDefinition.get('id'),
                        building_attribute_set: buildingAttributeSet.get('id'),
                        efficiency: parentBuildingUsePercent ? parentBuildingUsePercent.get('efficiency') : 1.0,
                        square_feet_per_unit: parentBuildingUsePercent ? parentBuildingUsePercent.get('square_feet_per_unit') : 500,
                        percent: 0
                    });
                // Bug in SC nested records sometimes returns a previous version of the record, not the final version, so we need to get the final one
                newBuildingUsePercent = this.getPath('buildingUsePercents.lastObject');
                newBuildingUsePercent.attributes();
                if (this.get('contentValueKey')=='percent')
                    value = parseFloat(parseFloat(value).toFixed(2));
                // Set the contentValueKey value to the passed in value
                newBuildingUsePercent.set(this.get('contentValueKey'), value);
                // Send an event to alert dependent records of the change
                if (!newBuildingUsePercent.get('isTopLevel'))
                    // If we aren't a parent BuildingUsePercent send an event
                    Footprint.statechart.sendEvent('buildingUsePercentPropertyDidChange', SC.Object.create({
                        content:newBuildingUsePercent,
                        allContent: allContent
                    }));


                // Tell the parent that the collection changed since listing to the buildingUsePercents.[] causes crazy errors
                this.get('parentView').propertyDidChange('buildingUsePercents');

                // Return the child value so the view can maintain its display
                return newBuildingUsePercent.getPath(contentValueKey);




            }
        }
        else
            return passThroughNeitherNullNorUndefined(buildingUsePercent && buildingUsePercent.getPath(contentValueKey), '--');



    }.property('contentValueKey', 'content', 'allContent').cacheable()
});

Footprint.EditableBuildingUsePercentFieldsView = SC.View.extend(SC.Control, {
    classNames: ['footprint-editable-list-view', 'footprint-building-use-field-view'],
    childViews:'nameTitleView sqftView efficiencyView percentView'.w(),

    // A BuildingUseDefinition
    content:null,
    allContent: null,
    // The buildingUsePercents collection
    buildingUsePercents: null,
    // Used to handle the situation where the buildingUsePercents list is present but not yet loaded. We
    // could also use length, or resolve the issue stated above where listening to buildingUsePercents.[]
    // causes issues during cloning.
    buildingUsePercentsStatus: null,
    buildingUsePercentsStatusBinding: SC.Binding.oneWay('*buildingUsePercents.status'),

    buildingUseProperties: null,
    // buildngUseProperties that can't be written
    readonlyProperties: null,
    name: null,
    nameBinding: SC.Binding.oneWay('*content.name'),

    nameTitleView: Footprint.EditableModelStringView.extend({
        valueBinding: SC.Binding.oneWay('.parentView.name'),
        layout: {left: 0, width: 0.8, top: 1, bottom: 1}
    }),

    sqftView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 175, left: 30, width: 120, height:30},
        contentBinding:SC.Binding.oneWay('.parentView.buildingUsePercent'),
        contentValueKey: 'square_feet_per_unit',
        titleViewLayout: {height:.4},
        contentLayout: {top:.4, width: 80}
    }),

    efficiencyView: Footprint.EditableBuildingUsePercentFieldView.extend({
        layout: {left: 0.55, width: 0.2, top: 1, bottom: 1},
        isVisibleBinding: SC.Binding.oneWay('.parentView.buildingUseProperties').contains('efficiency'),
        isEditableBinding: SC.Binding.oneWay('.parentView.readonlyProperties').contains('efficiency').not(),
        contentBinding:SC.Binding.oneWay('.parentView.buildingUsePercent'),
        allContentBinding:SC.Binding.oneWay('.parentView.allContent'),
        contentValueKey: 'efficiency',
        buildingUsePercentsBinding: SC.Binding.oneWay('.parentView.buildingUsePercents')
    }),

    percentView: Footprint.EditableBuildingUsePercentFieldView.extend({
        layout: {left: 0.8, width: 0.2, top: 1, bottom: 1},
        isEditableBinding: SC.Binding.oneWay('.parentView.readonlyProperties').contains('percent').not(),
        contentBinding:SC.Binding.oneWay('.parentView.buildingUsePercent'),
        allContentBinding:SC.Binding.oneWay('.parentView.allContent'),
        contentValueKey: 'percent',
        buildingUsePercentsBinding: SC.Binding.oneWay('.parentView.buildingUsePercents')
    })
});
