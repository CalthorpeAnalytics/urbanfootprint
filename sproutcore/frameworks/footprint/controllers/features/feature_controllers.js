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


sc_require('controllers/attributes_controller');
sc_require('controllers/layer_selection_controllers');

Footprint.FeaturesControllerMixin = {

    /***
     * Delegate SC.Observable to extend dbEntityKeyToFeatureRecordType lookup
     */
    configEntityDelegateBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.configEntityDelegate'),

    /***
     * Lookup the of Footprint.Feature subclass by DbEntityKey
     */
    dbEntityKeyToFeatureRecordType: function () {
        return this.getPath('configEntityDelegate.dbEntityKeyToFeatureRecordType') || {};
    }.property('configEntityDelegate').cacheable(),

    // Temporary hack to alert listeners when the content is updated by an edit session
    updateDate: null,

    layer: null,
    layerStatus: null,
    layerStatusBinding: SC.Binding.oneWay('*layer.status'),
    recordType: function () {
        return this.get('layer') && (this.get('layerStatus') & SC.Record.READY) && this.getPath('layer.featureRecordType');
    }.property('layer', 'layerStatus').cacheable(),

    configEntity: null,
    configEntityBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),

    defaultsController: function () {
        if (this.get('recordType')) {
            return this.getPath('configEntityDelegate.defaultsControllers').get(this.getPath('layer.db_entity.key'));
        }
    }.property('configEntityDelegate', 'recordType').cacheable(),

    calculateBounds: function () {
        this.mapProperty('wkb_geometry', function (geometry) {
            // TODO
        });
    }.property('features').cacheable()
};

/***
 * Controls the active features of the configEntity that are selected based on the LayerSelection
 * @type {*|void}
 */
Footprint.featuresActiveController = Footprint.ArrayController.create(Footprint.FeaturesControllerMixin, {
    allowsEmptySelection: YES,
    allowsMultipleSelection: YES,
    layerBinding: SC.Binding.oneWay('Footprint.layerSelectionActiveController.layer'),
    /***
     * Because SC.SparseArray has no status manage, we set its status property in Footprint.DataSource manually
     * This observers keeps an eye on that status
     * https://groups.google.com/forum/#!msg/sproutcore/zjeu0xkbXCE/yAus1XMnTPgJ
     * content.storeKeys is the SC.SparseArray
     */
    _contentStatusDidChange: function () {
        if (!this.get('content')) {
            this.set('sparseArrayStatus', SC.Record.EMPTY);
            return NO;
        }
        this.set('sparseArrayStatus', this.getPath('content.storeKeys.status') || SC.Record.EMPTY);
    }.observes('*content.storeKeys.status'),

    /***
     * A special status for the sparse array with custom statuses for partial loading
     */
    sparseArrayStatus: SC.Record.EMPTY,
    /***
     * Override the usual status to the be the sparseArrayStatus
     * @returns {*}
     */
    status: function () {
        return this.get('sparseArrayStatus');
    }.property('sparseArrayStatus').cacheable()
});
/***

 * The editing version of featuresActiveController
 * Except for the selection, this is synced manually in the
 * Footprint.FeaturesAreReadyState, so that the edit controller
 * only gets the features that have been lazy loaded.
 * @type {EditControllerSupport}
 */
Footprint.featuresEditController = Footprint.ArrayController.create(
    Footprint.FeaturesControllerMixin,
    Footprint.EditControllerSupport,
    Footprint.SelectAllSupport,
    {
        allowsEmptySelection: YES,
        allowsMultipleSelection: YES,
        sourceController: Footprint.featuresActiveController,
        isEditable: YES,
        selectedRows: function () {
            if (this.get('selection') && this.getPath('selection.firstObject')) {
                return this.get('selection').map(function (row) {
                    return row;
                });
            }
        }.property('selection').cacheable(),

        /***
         * Used to inform views that the records are updating before the status of the controller changes.
         * TODO verify that the status alone is sufficient to inform the views
         */
        recordsAreUpdating: NO,
        layerBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController.layer'),

        /***
         * Triggers recordsDidUpdate change when we finish updating.
         * Views can observes recordsDidUpdate to just know when updates finish
         */
        recordsAreUpdatingObserver: function() {
            if (!this.get('recordsAreUpdating'))
                this.set('recordsDidUpdate', this.get('recordsDidUpdate') + 1);
        }.observes('.recordsAreUpdating'),

        /***
         * Marker property that we increment when updated. This property is bound to by Views that
         * need to know when the features have finished updating. The actual value is meaningless
         */
        recordsDidUpdate: 0,

        // The `featuresStatus` property is based on the status of each item in our content (which is
        // typically an SC.RecordArray). If any one item is BUSY or DIRTY, this value will reflect
        // that.
        // Note, that the status of the SC.RecordArray (our content) is based on the status of the query
        // in the store, not on the individual status' of the items.
        featuresStatus: SC.Record.EMPTY,

        // Observe changes to the content (i.e. SC.RecordArray) in order to setup and remove item status observers.
        contentDidChange: function () {
            var content = this.get('content'),
                lastContent = this._lastContent;

            if (content !== lastContent) {

                // Clean up last content's items.
                if (lastContent) {
                    lastContent.removeObserver('[]', this, 'contentsItemsDidChange');
                }

                // Begin observing new content's items.
                if (content) {
                    content.addObserver('[]', this, 'contentsItemsDidChange');
                }

                // Trigger a one-time content's items change.
                this.contentsItemsDidChange();

                // Cache the content in order to be able to clean up changes.
                this._lastContent = content;
            }
        }.observes('content'),

        // Observe changes to the content's items (i.e. addition, reordering or removal of items) in
        // order to setup and remove per-item status observers. If the content's items change, added
        // items need to be observed and removed items need to be cleaned up.
        contentsItemsDidChange: function () {
            var content = this.get('content');

            var lastContentsItems = this._lastContentsItems;
            if (!lastContentsItems) {
                lastContentsItems = [];
            }

            // Check for previous items no longer present.
            for (var i = lastContentsItems.length - 1; i >= 0; i--) {
                var lastItem = lastContentsItems[i];

                if (!content || content.indexOf(lastItem) < 0) {
                    // No longer in content.
                    lastItem.removeObserver('status', this, 'itemStatusDidChange');

                    // Remove the item from the cache.
                    lastContentsItems.replace(i, 1);
                }
            }

            // Check for new items not previously observed.
            if (content && content.get('length') > 0) {
                var len = content.get('length');
                for (i = 0; i < len; i++) {
                    var item = content.objectAt(i);

                    if (lastContentsItems.indexOf(item) < 0) {
                        // New to content.
                        item.addObserver('status', this, 'itemStatusDidChange');

                        // Cache each item in order to be able to clean up per-item changes.
                        lastContentsItems.push(item);
                    }
                }

                // Set the initial featuresStatus.
                this.set('featuresStatus', this.mapProperty('status').max());
            } else {
                // Clear featuresStatus.
                this.set('featuresStatus', SC.Record.EMPTY);
            }

            this._lastContentsItems = lastContentsItems;
        },

        // Each time any per-item's status changes, recompute the features status.
        itemStatusDidChange: function (item) {
            this.set('featuresStatus', this.mapProperty('status').max());
        }
    });

/***
 * Provides a list of the available attributes of a Feature class, and optionally adds
 * the attributes of joined Feature classes (for querying)
 */
Footprint.FeatureFieldsController = Footprint.AttributesController.extend({
    allowsMultipleSelection: NO,
    dbEntity: null,
    dbEntityStatus: null,
    dbEntityStatusBinding: SC.Binding.oneWay('*dbEntity.status'),

    /**
     * Prepend the db_entity key to each attribute in the fields property
     */
    prependDbEntity: NO,
    /***
     * Fields to exclude from the fields property. These must be fully qualified if
     * prependDbEntity is YES, otherwise just specify the field names.
     */
    excludeFields: null,

    // Allows the addition of join fields
    extraFields: null,

    fields: function () {
        if (!(this.getPath('dbEntityStatus') & SC.Record.READY) || !(this.get('templateFeatureStatus') & SC.Record.READY))
            return;
        var dbEntityKey = this.getPath('dbEntity.key');
        var featureFields = this.getPath('templateFeature.feature_fields');
        var excludeFields = this.get('excludeFields') || [];
        return (this.get('extraFields') || []).concat(
            dbEntityKey && featureFields ?
                featureFields.map(function (field) {
                    // Return the prepended field names or just the field names
                    return this.get('prependDbEntity') ?
                        '%@.%@'.fmt(dbEntityKey, field) :
                        field;
                }, this).filter(function (field) {
                    // Make sure the complete field name is not explicitly excluded
                    return !excludeFields.contains(field);
                }) :
                []
        );
    }.property('dbEntity', 'dbEntityStatus', 'templateFeature', 'templateFeatureStatus', 'prependDbEntity', 'excludeFields', 'attributeLookup', 'extraFields').cacheable()
});

/***
 * Holds the ConfigEntity that we use for the upload context.
 * Currently this is just bound to the active Project, but it will need to be more flexible in the future
 */
Footprint.featureClassUploadController = SC.Object.create({
    configEntity: null,
    configEntityBinding: SC.Binding.oneWay('Footprint.projectActiveController.content'),
    content: function () {
        return SC.Object.create({
            configEntity: this.get('configEntity')
        });
    }.property('configEntity').cacheable()
});
