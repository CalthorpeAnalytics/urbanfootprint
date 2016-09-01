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


Footprint.topSectionVisibleViewController = SC.ObjectController.create({
    topSectionIsVisible: NO,
    // The active view. The view and content are maintained when topSectionIsVisible is false, so that the user
    // can quickly return to the last view
    view: null,
    // One of the values 'projectInfo', 'query', 'approval' corresponding to the current view
    content: null,

    topSectionTopViewIsVisiblelayout: {height: 200},
    topSectionTopViewIsNotVisiblelayout: {height: 0},
    bottomSectionBottomViewIsVisibleLayout: {top: 200},
    bottomSectionTopViewIsNotVisiblelayout: {top: 0},
    editLayerSelection: null,
    editLayerSelectionBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController.content'),
    editLayerSelectionStatus: null,
    editLayerSelectionStatusBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController.status').defaultValue(null),

    /***
     * This updates the Footprint.layerSelectionEditController.content's selection_options.constrain_to_query
     * We only want to constrain the LayerSelection to the query when the query (filter or summary) interface
     * is visible. Otherwise the user might not understand why their bounds query doesn't behave as expected.
     */
    topSectionViewOrItsVisibilityObserver: function() {
        if (!(this.get('editLayerSelection') && (this.get('editLayerSelectionStatus') & SC.Record.READY)))
            return;
        if (this.didChangeFor('topSectionViewCheck', 'editLayerSelection', 'topSectionIsVisible', 'content')) {
            // Update the LayerSelection constrain_to_query flag. This tells the system to acknowledge or ignore
            // the current filter/join properties based on the the visibility of the topSection
            Footprint.layerSelectionEditController.setPathIfChanged(
                'selection_options.constrain_to_query',
                this.get('topSectionIsVisible') && this.get('content') == 'query');

            // Tell the states that the visibility changed
            Footprint.statechart.sendEvent('layerSelectionDidChange', this);
        }
    }.observes('.topSectionIsVisible', '.content', '.editLayerSelection', '.editLayerSelectionStatus'),

    topSectionLayout: function() {
        if (this.get('topSectionIsVisible')) {
            return this.get('topSectionTopViewIsVisiblelayout')
        }
        return this.get('topSectionTopViewIsNotVisiblelayout')
    }.property('topSectionIsVisible'),


    bottomSectionLayout: function() {
        if (this.get('topSectionIsVisible')) {
            return this.get('bottomSectionBottomViewIsVisibleLayout')
        }
        return this.get('bottomSectionTopViewIsNotVisiblelayout')
    }.property('topSectionIsVisible'),
});

Footprint.editSectionController = SC.ArrayController.create({
    editSectionIsVisible: NO
});
