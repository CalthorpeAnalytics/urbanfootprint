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
 * Sets the Layer visibility to Project or Scenario scope. See DbEntityEditItemView
 */
Footprint.LayerItemVisibilityView = SC.CheckboxView.extend({
    classNames: ['layer-item-visibility-view'],

    // Note that content must be defined as the DbEntity instance of the Layer

    configEntity: null,
    configEntityKey: null,
    configEntityKeyBinding: SC.Binding.oneWay('*configEntity.key'),
    // Editable versions of all APPLICATION LayerLibraries, keyed by ConfigEntity key
    layerLibrariesApplicationEdit: null,
    // This will be the Scenario or Project library, or a higher scope
    // We find the LayerLibrary we need based on the ConfigEntity key
    layerLibrary: function() {
        return this.getPath('layerLibrariesApplicationEdit.%@'.fmt(this.get('configEntityKey')));
    }.property('configEntityKey', 'layerLibrariesApplicationEdit').cacheable(),

    // This tracks the Layer content so we know to re-evalutate the value when it changes
    layerLibraryLayers: null,
    layerLibraryLayersBinding: SC.Binding.oneWay('*layerLibrary.observedRecords'),

    layerLibraryStatus: null,
    layerLibraryStatusBinding: SC.Binding.oneWay('*layerLibrary.status'),

    // All layers of the Library so that we can detect membership
    layers: null,
    layersBinding: SC.Binding.oneWay('*layerLibrary.layers'),
    layersStatus: null,
    layersStatusBinding: SC.Binding.oneWay('*layers.status'),

    // The current layer that this checkbox corresponds to.
    theLayer: null,
    dbEntityList: null,
    dbEntityListBinding: SC.Binding.oneWay('*configEntity.db_entities.observedRecords'),

    // fired when layers member changes: used to update 'value'
    // independent of the user actually clicking the checkbox.
    // The value is true if the DbEntity is new, meaning we always want to show the Layer
    // when its created, otherwise true if the Layer is ready and part of the LayerLibrary
    _layerMembershipChangeObserver: function() {

        // Check to see if the required values are ready. If not disable the checkbox
        var isReady = (this.getPath('layerLibraryStatus') & SC.Record.READY) &&
                (this.getPath('layersStatus') & SC.Record.READY) &&
                (this.getPath('theLayer.status') & SC.Record.READY);
        this.set('isEnabled', this.getPath('parentView.isEnabled') && !!isReady);
        // Don't set the checkbox while loading or updating
        if (!isReady)
            return;

        var checked = !!(this.getPath('content.status') == SC.Record.READY_NEW) || (
                isReady &&
                this.get('layers').contains(this.get('theLayer')));
        this._value = checked;

        // Now update the UI to match our internal state.
        this.set('value', checked);
    }.observes('*content.status',
               '*layers.[]',
               'layerLibraryStatus',
               'layersStatus',
               'layers',
               'theLayer'),


    // We can only enable ConfigEntity visibility if the DbEntity is stored at or above the ConfigEntity
    isDbEntityAtConfigEntityScope: function() {
        if (!this.get('configEntity') || !this.get('content'))
            return null;
        return this.getPath('configEntity.db_entities').contains(this.get('content'));
    }.property('configEntity', 'content', 'dbEntityList.[]').cacheable(),

    // Disable unless isDbEntityAtConfigEntityScope is True
    isEnabledBinding: SC.Binding.and('.parentView.isEnabled', '.isDbEntityAtConfigEntityScope'),

    // internal value to detect when the UI is out of sync with the
    // backend.
    _value: false,

    /***
     * If the Layer is in the LayerLibrary or a DbEntity is new we show the checkbox as checked
     */
    value: function(key, value) {
        if (value !== undefined) {
            // setter

            // we're changing the value, so we have to determine where this change came from
            if (value === this._value) {
                // This must have come from an internal event, like
                // doAddOrRemoveLayer being called, so return early
                // and don't use the statechart.
                return value;
            }

            // If we got here, the UI set this in response to the user
            // clicking, so we have to initiate the add/remove.
            this._value = value;

            // Note we need to pass the new value of 'value' because
            // this._value will change as a result of firing this.
            Footprint.statechart.sendAction(
                'doAddOrRemoveLayerFromApplicationLayerLibrary',
                SC.Object.create({theLayer: this.get('theLayer'), value: value, doSave: YES}));

            return value;
        }

        // getter
        return this._value;
    }.property(),
});
