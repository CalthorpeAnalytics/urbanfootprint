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
 * Displays a saving overlay if visible.
 * You can key the message based using savingMessage property
 * @type {*|RangeObserver|Class|void}
 */
Footprint.SaveOverlayView = SC.View.extend({
    classNames: ['form-info-overlay'],
    childViews: ['labelView'],
    /***
     * Set to display a message according to what is happening. Defaults to 'Saving...'
     */
    isVisible: NO,
    savingMessage: 'Saving...',
    labelView: SC.LabelView.extend({
        layout: { height: 35, width: 250, centerX: 0, centerY: 0 },
        savingMessage: null,
        savingMessageBinding: SC.Binding.oneWay('.parentView.savingMessage'),
        value: function() {
            return this.getPath('parentView.savingMessage');
        }.property('savingMessage').cacheable()
    })
});
