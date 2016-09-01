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




Footprint.CrudState = SC.State.extend({

    // -----------------------
    // Always-available actions.
    //

    /***
     * @param context. Context contains:
     *  recordType: Required. The kind of record to view/edit
     *  activeRecord: Optional. The record to edit or clone. Set null to create a record from scratch
     *  content: Optional. Used for the activeRecord if activeRecord undefined. If activeRecord is simply null
     *  then null will be used, assuming a creation case
     *  nowShowing: Optional. Default 'Footprint.ModalFeatureSummaryInfoView'. The view to show of the tabbed
     *  views in the modal window
     *  Note that showing the modal has nothing to do with whether or not the content is ready.
     *  There are times when we want to show the modal while the content loads.
     *  // TODO rename activeRecord to content throughout
     */
    doShowModal: function(context) {
        // Resolve the infoView to use with the following three alternatives
        var infoPaneStringOrView = context && context.get('infoPane');
        var recordType = context.get('recordType');

        // Make sure the recordType matches the content.
        // Otherwise this event belongs to another CrudState instance
        if (!(context.get('content') || []).every(function(record) {
            return record.instanceOf(recordType);
        }))
            return NO;

        if (infoPaneStringOrView) {
            var recordType = context.get('recordType');
            var infoPaneViewClass = typeof(infoPaneStringOrView) == 'string' ? SC.objectForPropertyPath(infoPaneStringOrView) : infoPaneStringOrView;
            if (!infoPaneViewClass) {
                throw Error('infoPane was not set or configured for recordType %@'.fmt(recordType));
            }
            var createdInfoPane;
            var infoPaneGuid = SC.guidFor(infoPaneViewClass);
            if (this._infoPane && this._infoPane.constructor == infoPaneViewClass) {
                // infoPane is already set to the same type, just update the context
                this._infoPane.set('context', context);
                this._infoPane.append();
                Footprint.crudController.set('infoPaneIsVisible', YES);
            }
            else if (this._infoPaneCache && this._infoPaneCache[infoPaneGuid]) {
                // infoPane is a different record type but that type has been cached
                if (this._infoPane.get('isAttached')) {
                    // It should already be removed
                    logWarning('Previous infoPane %@ was not removed properly'.fmt(this._infoPane.constructor));
                    this._infoPane.remove();
                }
                this._infoPane = this._infoPaneCache[infoPaneGuid];
                this._infoPane.set('context', context);
                createdInfoPane = this._infoPane;
                if (!createdInfoPane.get('isPaneAttached')) {
                    createdInfoPane.append();
                    Footprint.crudController.set('infoPaneIsVisible', YES);
                }
            }
            else {
                // infoPane is a different record type and that type has not been cached
                // This is either a view class or instance. It will be an instance if it belongs
                // to an SC.Page
                var createdInfoPane = null;
                if (infoPaneViewClass.instanceOf) {
                    createdInfoPane = infoPaneViewClass;
                    createdInfoPane.set('recordType', recordType);
                    createdInfoPane.set('context', context);
                }
                else {
                    createdInfoPane = infoPaneViewClass.create({
                        recordType: recordType,
                        context: context
                    });
                }
                // Display it
                createdInfoPane.append();
                Footprint.crudController.set('infoPaneIsVisible', YES);
                // Remember it for reenter and exit
                this._infoPane = createdInfoPane;
                // Cache the creation
                this._infoPaneCache = this._infoPaneCache || {};
                this._infoPaneCache[infoPaneGuid] = this._infoPane;
            }
        }
    },
    doHideModal: function(context) {
        if (this._infoPane) {
            this._infoPane.remove();
            Footprint.crudController.set('infoPaneIsVisible', NO);
        }
        return YES;
    },

    /***
     * Exports modal table content as CSV.
     * The table may not yet have all of its Features loaded, because
     * it uses an SC.SparseArray. Therefore this needs to wait for all
     * @param context: contains the following
     *  recordType: The Feature subclass type
     *  exportContent: The data to export (for local exports only)
     *  isLocalExport: True for local export from the client. False to export from the server.
     *  isSummary: Default false. If True then this a summary result export. Matters only for non-local exports
     */
    doQueryResultExport: function(context) {
        if (context.get('isLocalExport')) {
            var layerName = (context.get('recordType') || Footprint.Feature).toString().split('.')[1].decamelize() + '_selection.csv';
            var data = context.get('exportContent');
            var csvContent = 'data:text/csv;charset=utf-8,';
            csvContent += data.map(function(infoArray) {
                return infoArray.join(',');
            }).join('\n');
            var encodedUri = encodeURI(csvContent);
            var link = document.createElement('a');
            link.setAttribute('href', encodedUri);
            link.setAttribute('download', layerName);

            link.click();
        }
        else {
            SC.AlertPane.info('Exporting the current query results--it will start downloading as soon as it is ready. \n\n ' +
            'Please do not close your UrbanFootprint session.');
            Footprint.DataSource.export(
                context.get('isSummary')  ?
                    'export_query_summary' :
                    'export_query_results',
                context.get('content')
            );
        }
    },

    doResultTableExport: function(context) {
        SC.AlertPane.info('Exporting the summary table. It will start downloading as soon as it is ready. \n\n ' +
            'Please do not close your UrbanFootprint session.');
        Footprint.DataSource.export('export_result_table', context.get('content'));
    },
    /***
     * Converts modal table content to CSV and presents it in a window for copying
     * @param context
     */
    doCopy: function(context) {
        var csv = context.get('content').map(function (row) {
            return row.join(',');
        }).join('\n');
        Footprint.clip.setText(csv);
    },

    /*********************************************
     *
     * The CRUD actions.
     * These are triggered whether the modal is open or not. They route through the
     * generic doProcessRecord action, which opens the modal if needed.
     *
     */

    /***
     * Create a brand spankin' new record with minimum attributes copied from the context.
     * @param context - context.content is the is the context that is minimally copied
     */
    doCreateRecord:function(context) {
        // view objects don't like to get passed to the ArrayController, so filter for the key we want
        var safeContext = filterKeys(context, ['infoPane', 'recordsEditController', 'recordType', 'content']);
        var pluralContext = toArrayController(this._context || {}, safeContext, {crudType:'create'});
        this.statechart.sendAction('doProcessRecord', pluralContext);
    },

    /***
     * Create a new record by cloning the record in the context
     * @param context - context.content is cloned
     */
    doCloneRecord:function(context) {
        // We always deal with adding records one at a time, but the context.content
        // will either be singular or a single-item array, since some of the saving_crud_state
        // stuff always turns content into an array for simplicity.

        // view objects don't like to get passed to the ArrayController, so filter for the keys we want
        var safeContext = filterKeys(context, ['infoPane', 'recordsEditController', 'recordType', 'content']);
        var pluralizeContext = toArrayController(this._context || {}, safeContext, {crudType:'clone'});
        this.statechart.sendAction('doProcessRecord', pluralizeContext);
    },

    /***
     * Update the record in the context.
     * @param context - context.content is used for the editing states
     */
    doUpdateRecord:function(context) {
        var pluralizeContext = toArrayController(this._context || {}, context, {crudType:'update'});
        this.statechart.sendAction('doProcessRecord', pluralizeContext);
    },

    /***
     * View the record in the context
     * TODO use the regular edit state unless we need a different state for read-only
     * @param context - context.content is the selected record
     */
    doViewRecord:function(context) {
        var pluralizeContext = toArrayController(this._context || {}, context, {crudType:'view'});
        this.statechart.sendAction('doProcessRecord', pluralizeContext);
    },

    /***
     * Query based on the recordType in the context
     * @param context - context.recordType is the type of record used for the querying states
     */
    doQueryRecords: function(context) {
        var singularContext = toArrayController(context);
        this.statechart.sendAction('doProcessRecord', singularContext);
    },

    /***
     * This action is sent by the doFooRecord(s) actions above. If this method handles the
     * action, it goes to the modal state and pops open the modal. If we're already in the
     * modal state, it will handle it instead.
     */
    doProcessRecord: function(context) {
        this.gotoState(this.modalState, context);
    },

    // -----------------------------------
    // Substates
    //

    initialSubstate: 'noModalState',

    noModalState: SC.State,

    modalState: SC.State.plugin('Footprint.CrudModalState')
});
