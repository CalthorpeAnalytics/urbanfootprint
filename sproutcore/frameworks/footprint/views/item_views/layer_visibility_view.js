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


sc_require('views/item_views/layer_item_visibility_view');

/***
 * Layers are always in the Default LayerLibraries starting at the scope of their DbEntity's ConfigEntity
 * and all the way down to the lowest scope, which should be the UserProfile.
 *
 * A second LayerLibrary, Application, contains a subset of those Layers based on a user's choice of what
 * should be visible in the application. A user can determine the inclusion in this subset LayerLibrary based
 * on their permission level. For instance, a user with Project edit permission could decide that a Layer
 * is excluded from the Project's Application LayerLibrary. This would exclude it from all Scenario and
 * UserProfile level Application LayerLibraries below the Project. A User with Scenario edit permission
 * could then choose to include the Layer at the Scenario or UserProfile level to bring the Layer into
 * the LayerLibrary at one of those levels. Preconfigured layers use a configuration flag to determine
 * whether or not the Layer should be put in the Application LayerLibrary at it's ConfigEntity scope
 * (and thus adopted by child LayerLibraries)
 */
Footprint.LayerVisibilityView =  SC.View.extend({
    layout: { right:0, width: 100},
    // TODO: If user is an admin of any particular dbEntity scope,
    // they should see a set of checkboxes from the bottom-most
    // visibility (probably user or scenario all the way up to their
    // highest dbEntity scope. For now, we just show the scenario scope.
    childViews: [
        //'projectVisibilityView'
        'scenarioVisibilityView',
    ],
    classNames: ['footprint-visibility-view'],

    content: null,
    theLayer: null,
    scenario: null,
    layerLibrariesApplicationEdit: null,

    /***
     * If checked this puts the Layer in the APPLICATION LayerLibrary at the Project scope, which
     * will cause it to be adopted by each of the Project's Scenario's APPLICATION LayerLibrary.
     * If this is unchecked from checked it will remove the Layer from the APPLICATION LayerLibrary
     * and thus from each of Scenario's APPLICATION LayerLibrary, except for the current Scenario
     * if its visibility checkbox is checked at the time of this unchecking. There is no explicit
     * state for this checkbox other than checking to see if the Layer is currently in the APPLICATION LayerLibrary
     */
    projectVisibilityView: Footprint.LayerItemVisibilityView.extend({
        layout: {left: 15, width:16, height: 16, centerY: 0},
        classNames: ['scenario-visibility-view'],
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        layerLibrariesApplicationEditBinding: SC.Binding.oneWay('.parentView.layerLibrariesApplicationEdit'),

        configEntityBinding: SC.Binding.oneWay('.parentView*scenario.project'),
        theLayerBinding: SC.Binding.oneWay('.parentView.theLayer'),
    }),

    /***
     * When converting from Project to Scenario Visibility this removes the layers from the default LayerLibrary
     * of the other Scenarios. It never deletes the Layers
     */
    scenarioVisibilityView: Footprint.LayerItemVisibilityView.extend({
        layout: { right: 15, width:16, height: 16, centerY: 0 },
        classNames: ['scenario-visibility-view'],
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        configEntityBinding: SC.Binding.oneWay('.parentView.scenario'),
        layerLibrariesApplicationEditBinding: SC.Binding.oneWay('.parentView.layerLibrariesApplicationEdit'),

        theLayerBinding: SC.Binding.oneWay('.parentView.theLayer'),
    }),
});
