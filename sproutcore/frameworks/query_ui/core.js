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

// ==========================================================================
// Project:   QueryUI
// ==========================================================================
/*globals QueryUI, Footprint */


/** @namespace

  This object acts as a controller backing the query UI components. It could be refactored into
  substate(s) when combined into the real project.

  @extends SC.Object
*/
QueryUI = SC.Object.create(
    /** @scope QueryUI.prototype */ {

    /*
      The SELECT clause for the primary layer.

      @type String
      @default '*'
    */
    // primarySelectValue: function () {
    //   var  = this.get(''),
    //     ret;

    //   if () {
    //     ret = ;
    //   }

    //   return ret;
    // }.property(''),

    /*
      The ADD FIELD clause for the primary layer.

      @type String
      @default ''
    */
    // primaryAddFieldValue: '',

    /*
      The WHERE clause for the primary layer.

      @type String
      @default ''
    */
    // primaryWhereValue: '',

    /*
      The store in use.

      @type SC.Store
      @default null
    */
    // TODO: Where should this come from? It's a bit odd to have to set it on a controller.
    store: null,

    addSummary: function () {
        // Create a new summary.
        var query = QueryUI.queryController.get('content'),
            summaries = query.get('summaries');

        // When adding nested objects, push the raw Object. Don't create a record on the store.
        summaries.pushObject({
            name: 'QUI.DefaultSummaryName {name}'.loc(query.get('name')),
            type: 'GenericObjects' // Due to a bug in SC.Record nested objects, you need to specify a type when using a key on the attribute.
        });

        // Select the new summary.
        QueryUI.summariesController.selectObject(summaries.get('lastObject'));

        // Append the modal pane.
        var summaryPane = QueryUI.views.get('summaryPane');
        summaryPane.append();
    },

    createQuery: function (layer) {
        var store = this.get('store'),
            title;

        // Create a new default title based on the initial layer and date.
        var now = SC.DateTime.create(),
            dateString = now.toFormattedString('%y-%m-%d'),
            allQueries = QueryUI.allQueriesController.get('arrangedObjects'), // This must be pre-loaded!
            allTitles = allQueries.getEach('name'),
            i = 1,
            proposedTitle;

        title = proposedTitle = 'QUI.DefaultQueryName {name, date}'.loc(layer.get('name'), dateString);

        // If the title is already in use, append a number.
        while (allTitles.indexOf(proposedTitle) >= 0) {
            proposedTitle = title + ' (' + i + ')';
            i++;
        }

        QueryUI.queryController.set('content', store.createRecord(Footprint.LayerSelection, {
            name: proposedTitle,
            selection_layer: layer.get('id')
            // summary_results: []
            // ? What else ?
        }));
    },

    /*
        Clear the query.
    */
    closeQuery: function () {
        // Reset the query.
        var query = QueryUI.queryController.get('content'),
            store = this.get('store');

        switch (query.get('status')) {
        // If a Query is new, destroy it.
        case SC.Record.READY_NEW:
            query.destroy();

            break;

        // If a Query is dirty, discard changes.
        case SC.Record.READY_DIRTY:
            store.discardChanges();

            break;
        default:
        }

        QueryUI.queryController.set('content', null);
    },

    /*
        Remove the queries pane.
    */
    closeQueriesPane: function () {
        // Remove the pane.
        var queriesPane = QueryUI.views.get('queriesPane');
        queriesPane.remove();

        // Clear out the controller content.
        QueryUI.allQueriesController.set('content', null);
    },

    /*
      Removes the summary and removes the summary pane.
    */
    closeSummary: function () {
        // Remove the pane.
        var summaryPane = QueryUI.views.get('summaryPane');
        summaryPane.remove();

        // Reset the summary.
        var summary = QueryUI.summaryController.get('content');

        if (summary.get('status') === SC.Record.READY_NEW) {
            // Destroy the new summary.
            summary.destroy();
        } else if (summary.get('status') === SC.Record.READY_DIRTY) {
            // Discard the changes.
            var store = summary.get('store');
            store.discardChanges();
        } // else do nothing.

        QueryUI.summaryController.set('content', null);
    },

    /*
        Run a query.
    */
    runQuery: function () {
        var query = QueryUI.queryController.get('content'),
            store = query.get('store');

        switch (query.get('status')) {
        // If a Query is new, save it now.
        case SC.Record.READY_NEW:
            query.commitRecord();

            break;

        // If a Query is dirty, update it now in the main store.
        case SC.Record.READY_DIRTY:
            store.commitChanges(); // Commit changes from nested store.

            // Find the primary store record and commit it.
            var parentStore = store.get('parentStore'),
                parentQuery;

            parentQuery = parentStore.find(query);
            parentQuery.commitRecord();

            break;
        default:
        }
    },

    /*
      Displays the manage queries pane.
    */
    showManageQueries: function () {
        // Append the panel pane.
        var queriesPane = QueryUI.views.get('queriesPane');
        queriesPane.append();
    },

    /*
      Displays the options menu.
    */
    showOptionsMenu: function (sender) {
        // Append the menu.
        var optionsMenu = QueryUI.views.get('optionsMenu');

        optionsMenu.popup(sender);
    }

});

/*
    All query records in the store.

    Set this content manually to an SC.Query.
*/
QueryUI.allQueriesController = SC.ArrayController.create({
});

/*
    The currently selected query.
*/
QueryUI.queryController = SC.ObjectController.create({

    /*
      The QueryUI.Query record in use.

      @type QueryUI.Query
      @default null
    */
    content: null,

    /*
      A simple Boolean indicating whether the join layer has been set on the query or not.

      @type Boolean
      @default false
    */
    hasJoinLayer: false,
    hasJoinLayerBinding: SC.Binding.oneWay('*content.joinLayer').bool(),

    /*
      Whether the current query is valid or not.

      When this is true, the query is ready to be sent to the server.

      @type Boolean
      @default false
    */
    isValidQuery: function () {
        var appearsValid = false,
            query = this.get('content');

        if (query) {
            appearsValid = true;
            // TODO: Inspect the statement clauses for validity.
        }

        return appearsValid;
    }.property('content', 'primarySelectValue', 'primaryAddFieldValue', 'primaryWhereValue'),

});

/*
    The summaries of the current query.
*/
QueryUI.summariesController = SC.ArrayController.create({
    contentBinding: SC.Binding.oneWay('QueryUI.summaries')
});

/*
    The current selected summary.
*/
QueryUI.summaryController = SC.ObjectController.create({
    contentBinding: SC.Binding.oneWay('QueryUI.summariesController.selection').single(),

    /*
        A simple boolean to indicate if the summary appears valid or not.
    */
    isValidSummary: function () {
      var content = this.get('content'),
        ret = false;

      if (content) {
        var groupByStatement = content.get('groupByStatement'),
            summarizeByStatement = content.get('summarizeByStatement');

        ret = !SC.none(groupByStatement) && !SC.none(summarizeByStatement);
      }

      return ret;
    }.property('content'),
});

QueryUI.summaryLayersController = SC.ArrayController.create({

});
