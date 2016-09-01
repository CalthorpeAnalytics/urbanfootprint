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


sc_require('views/progress_overlay_view');

Footprint.ProgressBarView = SC.View.extend({

    childViews: ['savingView', 'progressView'],
    /***
     * One or many objects to track
     */
    nestedStoreContent: null,
    saveInProgress:null,
    saveInProgressBinding: SC.Binding.oneWay('*content.saveInProgress'),
    nestedStoreContentStatus: null,
    nestedStoreContentStatusBinding: SC.Binding.oneWay('*nestedStoreContent.status'),
    nestedStoreHasChanges: null,
    nestedStoreHasChangesBinding: SC.Binding.oneWay('*nestedStoreContent.store.hasChanges'),
    title: 'Saving...',
    // Layout of the title
    titleLayout: null,
    // Layout of the progress bar
    progressBarLayout: null,
    // The Footprint.Progress bar gets the main store content from the nestedStoreContent
    contentBinding: SC.Binding.oneWay('.progressView.content'),

    isVisibleBinding: SC.Binding.oneWay('*progressView.isVisible'),

    savingView: SC.View.extend({
        childViews: ['updatingIconView', 'updatingTitleView'],
        layoutBinding: SC.Binding.oneWay('.parentView.titleViewLayout'),
        justUpdated: NO,
        isOverlayVisible: null,
        isOverlayVisibleBinding: SC.Binding.oneWay('.parentView.isVisible'),
        title: null,
        titleBinding: SC.Binding.oneWay('.parentView.title'),

        updatingIconView: SC.ImageView.extend({
            layout: { left: 5, width: 24, height: 24, right: 30, top: -2},
            useCanvas: NO,
            value: sc_static('footprint:images/spinner24.gif'),
            isVisibleBinding: SC.Binding.oneWay('.parentView.isOverlayVisible')
        }),
        updatingTitleView: Footprint.LabelView.extend({
            layout: {left: 35, top: 5, height: 16},
            valueBinding: '.parentView.title',
            isVisibleBinding: SC.Binding.oneWay('.parentView.isOverlayVisible')
        })
    }),

    progressView: Footprint.ProgressOverlayForNestedStoreView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.progressBarLayout'),
        nestedStoreContentBinding: SC.Binding.oneWay('.parentView.nestedStoreContent')
    })
});
