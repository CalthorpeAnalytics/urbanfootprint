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
  * A lightweight controller that manages the map tools properties
  * content is A Footprint.MapTools instance (singleton?) for painting, selection, etc. tools for the map
  * This is setup by the view so that the tools can access the map and send actions to the view
  * @type {Class}
  */
Footprint.mapToolsController = SC.ObjectController.create({

    isDataManager: null,
    isDataManagerBinding: SC.Binding.oneWay('Footprint.scenarioActiveController*configEntityDelegate.isDataManager'),

    /***
     * The tools allowed above the map.
     * All our included unless this is a data manager site, in which case we hide the Built From manager button.
     */
    toolConfigs: function() {
        return [
            // View and edit the selected item's attributes
            SC.Object.create({
                icon: sc_static('images/latest_icons/zoom_extent.png'),
                action: 'zoomToProjectExtent',
                isEnabled: YES,
                type: 'navigator',
                isStatelessButton: YES,
                toolTip: 'Zoom to Project Extent'
            }),
            SC.Object.create({
                icon: sc_static('images/latest_icons/zoom_selection.png'),
                action: 'zoomToSelectionExtent',
                isEnabled: YES,
                type: 'featurer',
                isStatelessButton: YES,
                toolTip: 'Zoom to Selection Extent'
            }),
            SC.Object.create({
                icon: sc_static('images/latest_icons/clear_selection.png'),
                keyEquivalent: 'esc',
                action: 'doClearSelection',
                isEnabled: YES,
                type: 'deselector',
                isStatelessButton: YES,
                toolTip: 'Clear Selection'
            }),
            SC.Object.create({
                icon: sc_static('images/latest_icons/pan.png'),
                keyEquivalent: 'ctrl_n',
                action: 'navigate',
                isEnabled: YES,
                type: 'navigator',
                toolTip: 'Navigate \n \nHold Shift and drag to create zoom extent'
            }),
            SC.Object.create({
                icon: sc_static('images/latest_icons/identify.png'),
                keyEquivalent: 'ctrl_i',
                action: 'identify',
                isEnabled: YES,
                type: 'selector',
                toolTip: 'Identify \n \nClick to see details of an item'
            }),
            SC.Object.create({
                icon: sc_static('images/latest_icons/select_single.png'),
                keyEquivalent: 'ctrl_p',
                action: 'pointbrush',
                isEnabled: NO,
                type: 'selector',
                toolTip: 'Point Selector \n \nHold Ctrl/Meta key to extend current selection'
            }),
            SC.Object.create({
                icon: sc_static('images/latest_icons/select_rect.png'),
                keyEquivalent: 'ctrl_b',
                action: 'rectanglebrush',
                isEnabled: NO,
                type: 'selector',
                toolTip: 'Box Selector \n \nHold Ctrl/Meta key to extend current selection'
            }),
            SC.Object.create({
                icon: sc_static('images/latest_icons/select_poly.png'),
                keyEquivalent: 'ctrl_o',
                action: 'polybrush',
                isEnabled: NO,
                type: 'selector',
                toolTip: 'Polygon Selector \n \nHold Ctrl/Meta key to extend current selection'
            }),
            SC.Object.create({
                icon: sc_static('images/latest_icons/export.png'),
                keyEquivalent: 'ctrl_e',
                action: 'doExportMap',
                isEnabled: YES,
                type: 'navigator',
                isStatelessButton: YES,
                toolTip: 'Export Map as Image'
            })
        ].concat(
            this.get('isDataManager') ?
                [] :
                [SC.Object.create({
                    icon: sc_static('images/latest_icons/built_form.png'),
                    keyEquivalent: 'ctrl_q',
                    action: 'doManageBuiltForms',
                    isEnabled: YES,
                    type: 'navigator',
                    isStatelessButton: YES,
                    toolTip: 'Built Form Manager'
                })]
        );
    }.property('isDataManager').cacheable(),

    /***
     * The tool for selecting, which means creating some kind of
     * bounds for a selection Only one of the following can be
     * non-null. One one tool is active at a time
     */
    activeToolKeysByType: SC.Object.create({
        selector: null,
        deselector: null,
        navigator: null, // The active navigation tool key
        featurer: null // The active featurer tool key, so far just 'identify'
    }),

    // Always set to the active tool key despite its type
    activeToolKey:null,

    /***
     * The ToolConfig specified above of the activeToolKey
     */
    activeToolConfig: function() {
        return this.get('toolConfigs').findProperty('action', this.get('activeToolKey'));
    }.property('activeTooleKey', 'toolConfigs').cacheable(),

    selectToolByKey: function(toolKey) {
        var toolConfig = this.get('toolConfigs').findProperty('action', toolKey);
        var type = toolConfig.get('type');
        var key = toolConfig.get('action');

        // Only one of the activeToolKeysByType will have a non-null value
        ['selector', 'deselector', 'navigator', 'featurer'].forEach(function (aType) {
            this.activeToolKeysByType.set(aType, type == aType ? key : null);
            if (type==aType)
                this.set('activeToolKey', key);
        }, this);
    },

    /***
     * Clear the active tool and go back to the default (navigate)
     * @param toolKey
     */
    clearActiveTool: function() {
        this.selectToolByKey('navigate');
    },

    /**
     * The active paint tool according to activeToolKeysByType.selector
     * We store each selector tool in a property that has the name of the tool by its key/action
     */
    activeSelectorTool:null,
    activeSelectorToolKeyObserver: function() {
        var paintCurTool = this.get('activeSelectorTool');
        if (paintCurTool) {
            paintCurTool.getPath('mapTools.pointDrawLayer').disable();
            paintCurTool.getPath('mapTools.rectangleDrawLayer').disable();
            paintCurTool.getPath('mapTools.polygonDrawLayer').disable();
        }

        var paintNewToolName = this.activeToolKeysByType.get('selector');
        var paintNewTool = paintNewToolName ? this.get(paintNewToolName) : null;

        // paint tool could be null (non-paint map tool selected)
        // or it could be one of "polybrush" or "pointbrush"
        // problem is getPath('mapTools.polygonDrawLayer') will throw error if it does not exist

        this.set('activeSelectorTool', paintNewTool);
        paintNewTool = this.get('activeSelectorTool');
        if (paintNewToolName == 'polybrush') {
            paintNewTool.getPath('mapTools.polygonDrawLayer').enable();
        } else if (paintNewToolName == 'rectanglebrush') {
            paintNewTool.getPath('mapTools.rectangleDrawLayer').enable();
        } else if (paintNewToolName == 'pointbrush') {
            paintNewTool.getPath('mapTools.pointDrawLayer').enable();
        }
    }.observes('*activeToolKeysByType.selector'),

    layerActiveControllerObserver: function() {
        // console.log("active layer (for selection purposes) changed");
        this.clearActiveTool();
    }.observes('Footprint.layerActiveController.content')
});
