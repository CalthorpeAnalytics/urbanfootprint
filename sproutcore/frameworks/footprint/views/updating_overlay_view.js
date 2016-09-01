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

sc_require('views/info_views/updated_info_view');

Footprint.UpdatingOverlayView = SC.View.extend({
    childViews: ['updatingIconView', 'updatingTitleView', 'justUpdatedIconView', 'justUpdatedView'],
    classNames: ['updating-overlay-view'],
    justUpdated: NO,
    isOverlayVisible: NO,
    title: null,
    activeLayer: null,

    updatingIconView: SC.ImageView.extend({
        layout: { left:5, width:24, height:24, right: 30, top: -2},
        useCanvas: NO,
        value: sc_static('footprint:images/spinner24.gif'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.isOverlayVisible')
    }),
    updatingTitleView: SC.LabelView.extend({
        layout: {left: 35, top: 5},
        valueBinding: '.parentView.title',
        isVisibleBinding: SC.Binding.and('.parentView.isOverlayVisible', '.parentView.title')
    }),
    justUpdatedIconView: SC.ImageView.extend({
        layout: { left:0, width:27, height:27, right: 30},
        useCanvas: NO,
        value: sc_static('footprint:images/check.png'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.justUpdated')
    }),
    justUpdatedView: SC.LabelView.extend({
        layout: {left: 35, top: 5},
        value: 'Updated',
        isVisibleBinding: SC.Binding.oneWay('.parentView.justUpdated')
    })
});


/***
 * Extends the parent class to show an Updated message based on the status
 * The updated message is shown after the given status is BUSY and has
 * become READY_CLEAN. If the content changes then the message disappears.
 * @type {RangeObserver}
 */
Footprint.UpdatingOverlayStatusView = Footprint.UpdatingOverlayView.extend({
    classNames: ['footprint-updating-overlay-status-view'],
    childViews: ['updatingIconView', 'updatingTitleView', 'justUpdatedView'],
    status: null,
    content: null,
    justUpdated: NO,
    updatingTitle: null,

    isVisible: function() {
        return (this.get('status') & SC.Record.BUSY) || this.get('justUpdated');
    }.property('status','justUpdated').cacheable(),

    justUpdatedObserver: function() {
        if (this.didChangeFor('justUpdatedObserver', 'status', 'content')) {
            if (this.get('status') & SC.Record.BUSY) {
                this.set('lastSavedContent', this.get('content'));
            }
            // Indicate just saved if we are still showing the last saved content
            this.set('justUpdated',
                this.get('status') === SC.Record.READY_CLEAN && this.get('content') == this.get('lastSavedContent'));
        }
    }.observes('.status', '.content'),

    updatingIconView: SC.ImageView.extend({
        layout: { left:0, top: 1, width:27, height:25, right: 30},
        useCanvas: NO,
        value: sc_static('footprint:images/spinner36.gif'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.BUSY)
    }),
    updatingTitleView: SC.LabelView.extend({
        layout: {left: 35, top: 5},
        valueBinding: SC.Binding.oneWay('.parentView.updatingTitle'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.BUSY)
    }),
    justUpdatedView: Footprint.UpdatedInfoView.extend({
        isVisibleBinding: SC.Binding.oneWay('.parentView.justUpdated')
    })
});
