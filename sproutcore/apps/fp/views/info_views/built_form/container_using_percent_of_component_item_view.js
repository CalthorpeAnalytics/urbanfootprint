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
 * Shows the percentage of the component being editing in use by a container
 * For instance when editing a BuildingType, this shows the percentage of the BuildingType
 * being used by a Placetype
 */
Footprint.ContainerUsingPercentOfComponentItemView = SC.View.extend(SC.Control, {
    classNames: ['container-using-percent-of-component-item-view'],
    layout: { height: 34 },
    displayProperties: 'content percent containerStatus'.w(),
    childViews: 'nameLabelView percentLabelView'.w(),
    /***
     * This is a ComponentPercentMixin record
     */
    content: null,

    container: null,
    containerBinding: SC.Binding.oneWay('*content.subclassedContainer'),
    containerStatus: null,
    // This nonsense is needed because the container.status doesn't fire
    // an observer when it changes. Obviously a bug
    containerStatusObserver: function() {
        if (this.getPath('container.status') & SC.Record.BUSY) {
             this._timer = SC.Timer.schedule({
                target: this, action: 'timerFired', interval: 500,  repeats: YES
             });
        }
        this.setIfChanged('containerStatus', this.getPath('container.status'));
    }.observes('*container.status'),
    timerFired: function() {
        if (this.getPath('container.status') & SC.Record.READY) {
            this.setIfChanged('containerStatus', this.getPath('container.status'));
            this._timer.invalidate();
        }
    },
    percent: null,
    percentBinding: SC.Binding.oneWay('*content.percent'),

    nameLabelView: SC.LabelView.extend({
        layout: { left: 0.02, width: 0.7 },
        displayProperties: 'value container containerStatus'.w(),
        container: null,
        containerBinding: SC.Binding.oneWay('.parentView.container'),
        containerStatus: null,
        containerStatusBinding: SC.Binding.oneWay('.parentView.containerStatus'),
        /***
         * TODO There's a nested record bug that caches the name as null
         * sometimes, so fall back to the attribute
         */
        value: function() {
            return this.getPath('container.name') || this.getPath('container.attributes.name');
        }.property('container', 'containerStatus').cacheable()
    }),
    percentLabelView: SC.LabelView.extend({
        layout: { left: 0.71, right: 0.02 },
        percent: null,
        percentBinding: SC.Binding.oneWay('.parentView.percent'),
        textAlign: SC.ALIGN_CENTER,
        value: function() {
            return '%@ %'.fmt(100*parseFloat(this.get('percent')).toFixed(1));
        }.property('percent').cacheable()
    })
});
