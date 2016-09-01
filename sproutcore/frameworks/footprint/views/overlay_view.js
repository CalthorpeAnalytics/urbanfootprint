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


sc_require('views/footprint_view');
sc_require('system/array_status');


Footprint.OverlayView = Footprint.View.extend({
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
    /***
     * The title of the label if showLabel is YES
     */
    title: 'Loading...',

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

    /**
     * If YES, then show the overlay only for BUSY, but not any other non-READY condition.
     *
     * If NO, then show the onerlay for ALL non-READY conditions, including BUSY.
     */
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
        if (this.get('showOnBusyOnly')) {
            return this.get('status') & SC.Record.BUSY;
        } else {
            return !(this.get('status') & SC.Record.READY);
        }
    },

    loadingOverlayView: SC.View.extend({
        childViews:['imageView', 'labelView'],

        isVisibleBinding:SC.Binding.oneWay('.parentView.isVisible'),
        /***
         * Default NO. Set to YES to show a text message in addition to the spinner
         */
        showLabel: NO,
        showLabelBinding: SC.Binding.oneWay('.parentView.showLabel'),

        /***
         * We support imageSize or 16. Default imageSize.
         * This could be done much cleaner with css
         */
        imageSize: 24,
        imageSizeBinding: SC.Binding.oneWay('.parentView.imageSize'),

        imageView: SC.ImageView.extend({
            showLabel: null,
            showLabelBinding: SC.Binding.oneWay('.parentView.showLabel'),

            imageSize: 24,
            imageSizeBinding: SC.Binding.oneWay('.parentView.imageSize'),

            layout: function() {
                var imageSize = this.get('imageSize');
                return this.get('showLabel') ?
                    { centerX:-45, centerY:0, width:imageSize, height:imageSize} :
                    { centerX:0, centerY:0, width:imageSize, height:imageSize};
            }.property('showLabel', 'imageSize').cacheable(),

            useCanvas: NO,
            value: sc_static('footprint:images/spinner36.gif'),
            imageSizeObserver: function() {
                if (this.get('imageSize') == 16)
                    var value = this.get('value');
                this.setIfChanged('value', value.replace('spinner36', 'spinner16'));
            }.observes('.imageSize')
        }),

        labelView: Footprint.LabelView.extend({
            layout: { centerX:-5, centerY:0, width:50, height:16},
            isVisibleBinding: SC.Binding.and('.parentView.isVisible', '.showLabel'),
            valueBinding: SC.Binding.oneWay('.parentView.title')
        })
    }),

    errorOverlayView: SC.View.extend({
        childViews:['labelView'],
        isVisible:NO,
        isVisibleBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.ERROR),
        labelView: SC.LabelView.extend({
            layout: { centerX:0, centerY:0, width:100, height:20},
            value: 'An Error Occurred...'
        })
    })
});
