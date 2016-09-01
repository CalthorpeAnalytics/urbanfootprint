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


/***
 * Shows expandable vertical tabs to expose various section_views
 */
Footprint.MainPaneButtonController = SC.ArrayController.extend();
Footprint.MainPaneButtonController.mixin({
    SECTION_VISIBILITIES: ['editSectionIsVisible', 'analysisModuleSectionIsVisible', 'querySectionIsVisible']
});

Footprint.mainPaneButtonController = Footprint.MainPaneButtonController.create({
    init: function() {
        sc_super();
        // Create an observable property for each section's visibility
        Footprint.MainPaneButtonController.SECTION_VISIBILITIES.forEach(function(key) {
            this.set(key, NO);
        }, this)
    },

    constraintIsVisible: NO,
    analysisTool: null,
    activeLayer: null,
    activeLayerBinding: 'F.layerActiveController.content',
    analysisToolBinding: SC.Binding.oneWay('Footprint.analysisModulesRightSideEditController*content.firstObject'),
    environmentalConstraintTool: null,
    environmentalConstraintToolBinding: SC.Binding.oneWay('F.analysisModulesEditController.content').transform(function(modules) {
            if (modules) {
                return modules.filter(function (module) {
                    return module.get('key') == 'environmental_constraint'
                })
            }
        }
    ),

    /***
     * Set to YES when any of the section_views is visible
    */
    anySectionVisible: null,
    _previousVisibleSection: null,
    /***
     * Allows only one section to be visible at a time
     */
    isVisibleObserver: function() {
        // Find the section just made visible that was not the previous
        var newlyVisibleSection = Footprint.MainPaneButtonController.SECTION_VISIBILITIES.find(function(key) {
            return key!=this._previousVisibleSection && this.get(key);
        }, this);
        // If we have a new visible and old one, make the old one invisible
        if (newlyVisibleSection) {
            if (this._previousVisibleSection)
                this.set(this._previousVisibleSection, NO);
            this._previousVisibleSection = newlyVisibleSection
        }
        // Set anySectionVisible so views know whether or not a section is open
        this.setIfChanged(
            'anySectionVisible',
            !!Footprint.MainPaneButtonController.SECTION_VISIBILITIES.find(function(key) {
                return this.get(key);
            }, this));
        // Else if nothing is visible anymore clear the cache
        if (!this.get('anySectionVisible')) {
            this._previousVisibleSection = null;
        }
    }.observes('.analysisModuleSectionIsVisible', '.editSectionIsVisible', '.querySectionIsVisible'),

    constraintSectionObserver: function() {
        if(!this.get('editSectionIsVisible') || this.getPath('activeLayer.dbEntityKey') != 'scenario_end_state') {
            this.set('constraintIsVisible', NO);
        }
    }.observes('.editSectionIsVisible', '.activeLayer'),

    // Observe the editSectionIsVisible so we can send an event to the statechart when visible
    // This helps us fully load sparse arrays of Features before we make the editor available
    editSectionIsVisibleObserver: function() {
        if (this.get('editSectionIsVisible'))
            Footprint.statechart.sendEvent('editSectionDidBecomeVisible')
    }.observes('.editSectionIsVisible'),


    constraintSelectionObserver: function() {
        var environmentalConstraintTool = this.getPath('environmentalConstraintTool.firstObject');
        if(this.get('constraintIsVisible')) {
            F.analysisModulesEditController.selectObject(environmentalConstraintTool);
        }

    }.observes('.constraintIsVisible'),

    analysisSelectionObserver: function() {
        var analysisTool = this.getPath('analysisTool');
        if(this.get('analysisModuleSectionIsVisible')) {
            F.analysisModulesEditController.selectObject(analysisTool);
        }
    }.observes('.analysisModuleSectionIsVisible')
});
