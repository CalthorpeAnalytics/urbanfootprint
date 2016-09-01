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


sc_require('system/array_status');

Footprint.LoadingSpinnerView = Footprint.View.extend({
    childViews: ['loadingOverlayView', 'errorOverlayView'],
    classNames: ['overlay-view'],

    /***
     * The content whose status is being observed. Not required if simply monitoring status is sufficient
     */
    content:null,
    status:null,
    /***
     * Default no, optionally show a loading label
     */
    showLabel: NO,

    arrayController: SC.ArrayController.create(SC.ArrayStatus),
    contentObserver: function() {
        if (this.get('testItems') && this.get('content'))
            this.setPathIfChanged('arrayController.content', this.get('content'));
    }.observes('.content'),
    arrayControllerStatus: null,
    arrayControllerStatusBinding: SC.Binding.oneWay('*arrayController.status'),

    /***
     * The content status. If set explicitly it is sent to statusMatches to determine if the overlay should be shown.
     * If set and testItems is also YES, The items will be tested if statusMatches returns false for status. If not
     * set and testItems is YES, the items will be checked. If status is null and testItems is NO, then content.status will
     * be checked
     */
    computedStatuses: function() {
        if (this.get('status')) {
            // Check status or both status and arrayController.status
            return [this.get('status')].concat(this.get('testItems') ? [this.getPath('arrayController.status')]: []);
        }
        if (this.get('testItems')) {
            // Check just arrayController status
            return [this.getPath('arrayController.status')];
        }
        // Check content.status
        return [this.getPath('content.status')];
    }.property('status', 'testItems', 'arrayControllerStatus').cacheable(),

    // If true test the status of all content items
    testItems: NO,
    showOnBusyOnly: NO,

    /***
     * We show the overlay if any status we check returns BUSY (if showOnBusyOnly=YES) or any status returns anything other than READY
     * We either check just status, all content items' statuses, or both
     */
    isVisible: function() {
        // If any computedStatus matches return true
        return  this.get('computedStatuses').some(function(computedStatus) {
            return this.statusMatches(computedStatus);
        }, this);
    }.property('computedStatuses').cacheable(),

    statusMatches: function(status) {
        return this.get('showOnBusyOnly') ?
            this.get('status') & SC.Record.BUSY :
            !(this.get('status') & SC.Record.READY) && !(this.get('status') & SC.Record.ERROR);
    },

    loadingOverlayView: SC.ImageView.extend({
        layout: { width:24, height:24, centerX: 0, centerY: 0},
        isVisibleBinding:SC.Binding.oneWay('.parentView.isVisible'),
        useCanvas: NO,
        value: sc_static('footprint:images/spinner24.gif')
    }),

    errorOverlayView: SC.ImageView.extend({
        layout: { width:24, height:24, centerX: 0, centerY: 0},
        useCanvas: NO,
        isVisibleBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.ERROR),
        value: sc_static('footprint:images/error24.png'),
        hint: 'An Error Occurred...'
    })
});
