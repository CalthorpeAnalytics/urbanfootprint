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


sc_require('controllers/controllers');

/***
 * All behaviors in the system
 * @type {Footprint.SingleSelectionSupport}
 */
Footprint.behaviorsController = SC.ArrayController.create(Footprint.SingleSelectionSupport, {

});

/***
 * Nested store version of the Behaviors for editing the intersection of the currently edited feature_behavior.
 * Binds the singleSelection two-way to the feature_behavior.behavior
 */
Footprint.behaviorsEditController = Footprint.EditArrayController.create(Footprint.SingleSelectionSupport, {
    allowsEmptySelection:NO,
    sourceController: Footprint.behaviorsController,
    isEditable:YES,
    recordType: 'Footprint.Behavior',
    orderBy: ['key ASC'], // TODO switch to name when we get that set up
    storeBinding: SC.Binding.oneWay('Footprint.layersEditController.store'),

    dbEntity: null,
    dbEntityBinding: SC.Binding.oneWay('Footprint.layerEditController*db_entity'),
    dbEntityStatus: null,
    dbEntityStatusBinding: SC.Binding.oneWay('*dbEntity.status'),
    featureBehavior: function() {
        if ((this.getPath('dbEntity.status') & SC.Record.READY) &&
            this.getPath('dbEntity.feature_behavior.parentRecord')) // don't know why this is ever null, but it is
            return this.getPath('dbEntity.feature_behavior');
        return null;
    }.property('dbEntity', 'dbEntityStatus').cacheable(),

    // This junk is here because parentRecord (aka the DbEntity) is sometimes undefined
    parentRecord: null,
    parentRecordBinding: SC.Binding.oneWay('*featureBehavior.parentRecord'),
    parentRecordStatus: null,
    parentRecordStatusBinding: SC.Binding.oneWay('*parentRecord.status'),

    // Get/set the behavior of the featureBehavior.
    // For some reason the binding often fires when featureBehavior (a nested record) is
    // in a bad state where it has no parentRecord, which cause the write to fail
    // So we guard against that here

    behavior: function(propKey, value) {
        if (typeof(value) !== 'undefined') {
            if (this.getPath('parentRecord.status') & SC.Record.READY)
                this.setPath('featureBehavior.behavior', value);
        }
        return this.getPath('featureBehavior.behavior');
    }.property('featureBehavior', 'parentRecord').cacheable(),

    featureBehaviorObserver: function() {
        // When a dbEntity status becomes ready set the property if unset
        if ((this.getPath('dbEntity.status') & SC.Record.READY) &&
            this.getPath('featureBehavior.parentRecord') && // don't know why this is ever null, but it is
            !this.getPath('featureBehavior.behavior'))
                this.setPath('featureBehavior.behavior', this.get('singleSelection'));
    }.observes('*dbEntity.status', '.featureBehavior'),

    singleSelectionBinding: '*behavior',
    conditions: function() {
        return '%@ AND %@'.fmt(sc_super(), 'abstract != YES')
    }.property().cacheable()
});
