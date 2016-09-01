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


Footprint.urbanBuiltFormCategoriesTreeController = Footprint.TreeController.create({
    /***
     *
     * Organizes the URBAN BuiltForms by their tags.
     * @type {*|void
     */
    content: Footprint.TreeContent.create({
        // The container object holding leaves
        leafSetBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormSetActiveController.content'),
        // The leaves of the tree
        leavesBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormSetActiveController.built_forms'),
        // The toOne or toMany property of the leaf to access the keyObject(s). Here they are Tag instances
        keyProperty:'tags',
        // The property of the keyObject to use for a name. Here it the 'tag' property of Tag
        keyNameProperty:'tag',
        // Options for sorting the BuiltForms
        sortProperties: ['flat_building_densities.combined_pop_emp_density','name'],
        // Reverse sorting for appropriate keys
        reverseSortDict: {'flat_building_densities.combined_pop_emp_density': YES},
        /**
         * The keys of the tree, currently all tags in the system, to which BuiltForms might associate
         * TODO these tags should be limited to those used by BuiltForms
        */
        keyObjectsBinding: 'Footprint.builtFormTagsController.content',

        /**
         * All media used by BuiltForms, so the user can select a Medium to go assign to the BuiltForm, or clone one.
         * TODO this doesn't make sense
         */
        media: function() {
            return  Footprint.store.find(
                SC.Query.local(
                    Footprint.Medium, {
                        conditions: "key BEGINS_WITH 'built_form_'",
                        orderBy: 'key'
                    }));
        }.property().cacheable()
    }),
    selectionDidChange: function() {
        if (this.getPath('selection.firstObject'))
            Footprint.statechart.sendAction('builtFormDidChange', SC.Object.create({content : this.getPath('selection.firstObject')}));
    }.observes('.selection')
});



Footprint.agricultureBuiltFormCategoriesTreeController = Footprint.TreeController.create({
    /***
     *
     * Organizes the Agriculture BuiltForms by their tags.
     * @type {*|void
     */
    content: Footprint.TreeContent.create({
        // The container object holding leaves
        leafSetBinding: SC.Binding.oneWay('Footprint.agricultureBuiltFormSetActiveController.content'),
        // The leaves of the tree
        leavesBinding: SC.Binding.oneWay('Footprint.agricultureBuiltFormSetActiveController.built_forms'),
        // The toOne or toMany property of the leaf to access the keyObject(s). Here they are Tag instances
        keyProperty:'tags',
        // The property of the keyObject to use for a name. Here it the 'tag' property of Tag
        keyNameProperty:'tag',
        // Options for sorting the BuiltForms
        sortProperties: ['name'],
        /**
         * The keys of the tree, currently all tags in the system, to which BuiltForms might associate
         * TODO these tags should be limited to those used by BuiltForms
        */
        keyObjectsBinding: 'Footprint.builtFormTagsController.content',
        /**
         * All media used by BuiltForms, so the user can select a Medium to go assign to the BuiltForm, or clone one.
         * TODO this doesn't make sense
         */
        media: function() {
            return  Footprint.store.find(
                SC.Query.local(
                    Footprint.Medium, {
                        conditions: "key BEGINS_WITH 'built_form_'",
                        orderBy: 'key'
                    }));
        }.property().cacheable()
    }),
    selectionDidChange: function() {
        if (this.getPath('selection.firstObject'))
            Footprint.statechart.sendAction('builtFormDidChange', SC.Object.create({content : this.getPath('selection.firstObject')}));
    }.observes('.selection')
});

/***
 * The active builtForm, as dictated by the user's selection
 * @type {*}
 */
Footprint.urbanBuiltFormActiveController = Footprint.ActiveController.create({
    listController:Footprint.urbanBuiltFormCategoriesTreeController
});
/***
 * The active builtForm, as dictated by the user's selection
 * @type {*}
 */
Footprint.agricultureBuiltFormActiveController = Footprint.ActiveController.create({
    listController:Footprint.agricultureBuiltFormCategoriesTreeController
});
/***
 *  Supports reading of the FlatBuiltForm versions of BuiltForms. These contain extra attributes not currentlty stored in the builtForm
 * @type {SelectionSupport}
 */
Footprint.flatBuiltFormsController = SC.ArrayController.create(SC.SelectionSupport, {
    allowsEmptySelection:NO
});
/***
 * The flatBuildForm corresponding to the builtFormActiveController content
 */
Footprint.flatBuiltFormActiveController = SC.ObjectController.create({
    contentBinding:SC.Binding.oneWay('Footprint.flatBuiltFormsController*selection.firstObject')
});

/**
 * Provides a detailed view of the media of the active BuiltForm
 * @type {SelectionSupport}
 */
Footprint.urbanBuiltFormMediaController = SC.ArrayController.create(SC.SelectionSupport, Footprint.ArrayContentSupport, {
    allowsEmptySelection:NO,
    contentBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormActiveController.media'),
    updateSelection: function() {
        this.updateSelectionAfterContentChange();
    }.observes('.firstObject')
});

/***===== BuiltForm CRUD controllers =====***/

/***
 * A flat list of all Building records
 * @type {SelectionSupport}
 */
Footprint.buildingsController = SC.ArrayController.create(SC.SelectionSupport, Footprint.RecordControllerChangeSupport, {
    allowsEmptySelection:YES,
    orderBy: ['name ASC'],
    contentDidChangeEvent: 'buildingControllerDidChange',
    selectedItemDidChangeEvent: 'selectedBuildingControllerDidChange',
    sourceSelection: null,
    sourceSelectionBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormCategoriesTreeController.selection'),
    selection: function() {
        if (!this.get("sourceSelection") || !this.get('content'))
            return;
        var builtForms = this.get('sourceSelection').filter(function(builtForm) {
            return this.get('content').contains(builtForm);
        }, this);
        var selectionSet = SC.SelectionSet.create();
        selectionSet.addObjects(builtForms);
        return selectionSet;
    }.property('sourceSelection', 'controller').cacheable()
});


/***
 * Nested store version of the buildings for editing. The selection is bound oneWay to the main controller, so that
 * when the main controller selection changes, this one updates its corresponding record
 */
Footprint.buildingsEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:NO,
    sourceController: Footprint.buildingsController,
    isEditable:YES,
    recordType: function() {
        return Footprint.Building
    }.property().cacheable(),
    orderBy: ['name ASC']
});

/***
 * A flat list of all Crop records
 * @type {SelectionSupport}
 */
Footprint.cropsController = SC.ArrayController.create(SC.SelectionSupport, Footprint.RecordControllerChangeSupport, {
    allowsEmptySelection:YES,
    orderBy: ['name ASC'],
    contentDidChangeEvent: 'cropControllerDidChange',
    selectedItemDidChangeEvent: 'selectedCropControllerDidChange',
    sourceSelection: null,
    sourceSelectionBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormCategoriesTreeController.selection'),
    selection: function() {
        if (!this.get("sourceSelection") || !this.get('content'))
            return;
        var builtForms = this.get('sourceSelection').filter(function(builtForm) {
            return this.get('content').contains(builtForm);
        }, this);
        var selectionSet = SC.SelectionSet.create();
        selectionSet.addObjects(builtForms);
        return selectionSet;
    }.property('sourceSelection', 'controller').cacheable()
});
/***
 * Nested store version of the buildings for editing. The selection is bound oneWay to the main controller, so that
 * when the main controller selection changes, this one updates its corresponding record
 */
Footprint.cropsEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:NO,
    sourceController: Footprint.cropsController,
    isEditable:YES,
    recordType: function() {
        return Footprint.Crop;
    }.property().cacheable(),
    orderBy: ['name ASC']
});
/***
 * A flat list of all BuildingType records
 * @type {SelectionSupport}
 */
Footprint.buildingTypesController = SC.ArrayController.create(SC.SelectionSupport, Footprint.RecordControllerChangeSupport, {
    allowsEmptySelection:YES,
    orderBy: ['name ASC'],
    contentDidChangeEvent: 'buildingTypesControllerDidChange',
    selectedItemDidChangeEvent: 'selectedBuildingTypesControllerDidChange',
    sourceSelection: null,
    sourceSelectionBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormCategoriesTreeController.selection'),
    selection: function() {
        if (!this.get("sourceSelection") || !this.get('content'))
            return;
        var builtForms = this.get('sourceSelection').filter(function(builtForm) {
            return this.get('content').contains(builtForm);
        }, this);
        var selectionSet = SC.SelectionSet.create();
        selectionSet.addObjects(builtForms);
        return selectionSet;
    }.property('sourceSelection', 'controller')
});

/***
 * Nested store version of the buildingTypes for editing. The selection is bound oneWay to the main controller, so that
 * when the main controller selection changes, this one updates its corresponding record
 */
Footprint.buildingTypesEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:NO,
    updateSummaryAttributes: NO,
    sourceController: Footprint.buildingTypesController,
    isEditable:YES,
    recordType: function() {
        return Footprint.BuildingType;
    }.property().cacheable(),
    orderBy: ['name ASC'],
});
/***
 * A flat list of all BuildingType records
 * @type {SelectionSupport}
 */
Footprint.cropTypesController = SC.ArrayController.create(SC.SelectionSupport, Footprint.RecordControllerChangeSupport, {
    allowsEmptySelection:YES,
    orderBy: ['name ASC'],
    contentDidChangeEvent: 'cropTypesControllerDidChange',
    selectedItemDidChangeEvent: 'selectedCropTypesControllerDidChange',
    sourceSelection: null,
    sourceSelectionBinding: SC.Binding.oneWay('Footprint.agricultureBuiltFormCategoriesTreeController.selection'),
    selection: function() {
        if (!this.get("sourceSelection") || !this.get('content'))
            return;
        var builtForms = this.get('sourceSelection').filter(function(builtForm) {
            return this.get('content').contains(builtForm);
        }, this);
        var selectionSet = SC.SelectionSet.create();
        selectionSet.addObjects(builtForms);
        return selectionSet;
    }.property('sourceSelection', 'controller')
});

/***
 * Nested store version of the buildingTypes for editing. The selection is bound oneWay to the main controller, so that
 * when the main controller selection changes, this one updates its corresponding record
 */

Footprint.cropTypesEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:NO,
    updateSummaryAttributes: NO,
    sourceController: Footprint.cropTypesController,
    isEditable:YES,
    recordType: function() {
        return Footprint.CropType;
    }.property().cacheable(),
    orderBy: ['name ASC']
});
/***
 * A flat list of all PlaceType records
 * @type {SelectionSupport}
 */
Footprint.placetypesController = SC.ArrayController.create(SC.SelectionSupport, Footprint.RecordControllerChangeSupport, {
    allowsEmptySelection:YES,
    orderBy: ['name ASC'],
    contentDidChangeEvent: 'placetypesControllerDidChange',
    selectedItemDidChangeEvent: 'selectedPlacetypesControllerDidChange',
    sourceSelection: null,
    sourceSelectionBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormCategoriesTreeController.selection'),
    selection: function() {
        if (!this.get("sourceSelection") || !this.get('content'))
            return;
        var builtForms = this.get('sourceSelection').filter(function(builtForm) {
            return this.get('content').contains(builtForm);
        }, this);
        var selectionSet = SC.SelectionSet.create();
        selectionSet.addObjects(builtForms);
        return selectionSet;
    }.property('sourceSelection', 'controller')
});

/***
 * Nested store version of the placeTypes for editing. The selection is bound oneWay to the main controller, so that
 * when the main controller selection changes, this one updates its corresponding record
 */
Footprint.placetypesEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:NO,
    updateSummaryAttributes: NO,
    sourceController: Footprint.placetypesController,
    isEditable:YES,
    recordType: function() {
        return Footprint.UrbanPlacetype;
    }.property().cacheable(),
    orderBy: ['name ASC']
});
/***
 * A flat list of all PlaceType records
 * @type {SelectionSupport}
 */
Footprint.landscapeTypesController = SC.ArrayController.create(SC.SelectionSupport, Footprint.RecordControllerChangeSupport, {
    allowsEmptySelection:YES,
    orderBy: ['name ASC'],
    contentDidChangeEvent: 'landscapeTypesControllerDidChange',
    selectedItemDidChangeEvent: 'selectedLandscapeTypesControllerDidChange',
    sourceSelection: null,
    sourceSelectionBinding: SC.Binding.oneWay('Footprint.agriculatureBuiltFormCategoriesTreeController.selection'),
    selection: function() {
        if (!this.get("sourceSelection") || !this.get('content'))
            return;
        var builtForms = this.get('sourceSelection').filter(function(builtForm) {
            return this.get('content').contains(builtForm);
        }, this);
        var selectionSet = SC.SelectionSet.create();
        selectionSet.addObjects(builtForms);
        return selectionSet;
    }.property('sourceSelection', 'controller')
});

/***
 * Nested store version of the placeTypes for editing. The selection is bound oneWay to the main controller, so that
 * when the main controller selection changes, this one updates its corresponding record
 */
Footprint.landscapeTypesEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:NO,
    updateSummaryAttributes: NO,
    sourceController: Footprint.landscapeTypesController,
    isEditable:YES,
    recordType: function() {
        return Footprint.LandscapeType;
    }.property().cacheable(),
    orderBy: ['name ASC']
});

/***
 * Holds all the available BuildingUseDefinitions. Since they are a tree structure via the category property,
 * we add the categories and leaves property to limit them to those who have/don't have a category (parent leaf) defined, respectively
 */
Footprint.buildingUseDefinitionsController = SC.ArrayController.create({
    allowsEmptySelection:YES,
    orderBy: ['name ASC']
});



Footprint.buildingUseDefinitionsEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:NO,
    sourceController: Footprint.buildingUseDefinitionsController,
    isEditable:YES,
    recordType: Footprint.BuildingUseDefinition,
    orderBy: ['name ASC']
});

Footprint.buildingUseDefinitionsTreeController = Footprint.TreeController.create({
    /***
     *
     * Organizes the BuildingUsePercents by their BuildingUseDefinition
     * @type {*|void
     */
    content: Footprint.TreeContent.create({
        // All the category BuildingUseDefinitions.
        keyObjectsBinding: 'Footprint.buildingUseDefinitionsController.categories',
        // The leaves of the tree. In this case all leaf BuildingUseDefinitions
        leavesBinding: SC.Binding.oneWay('Footprint.buildingUseDefinitionsController.leaves'),

        // The path from the leaf to its category
        keyProperty:'category',
        // The property of the keyObject to use for a name. Since we use leafValueLookup to make our leaf values BuildingUsePercents,
        // this property is relative to the BuildingUsePercent instance
        keyNameProperty:'name',
        // Options for sorting the BuildingUseDefinitions within each category
        sortProperties: ['name'],
        reverseNodeSetSortDict: {name: YES}
    })
});
