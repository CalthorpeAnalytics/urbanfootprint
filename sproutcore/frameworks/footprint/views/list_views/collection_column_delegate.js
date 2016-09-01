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
// Project:   SC.CollectionColumnDelegate
// ==========================================================================
/*globals SC */

/**
 @namespace

 CollectionColumnDelegates are consulted by SC.HorizontalListView to
 control the width of columns, including specifying custom widths for
 specific columns.

 You can implement a custom column width in one of two ways.

 */
SC.CollectionColumnDelegate = {

    /** walk like a duck */
    isCollectionColumnDelegate: YES,

    /**
     Default column width.  Unless you implement some custom column width
     support, this column width will be used for all items.

     @property
         @type Number
     */
    columnWidth: 300,

    /**
     Index set of columns that should have a custom column width.  If you need
     certains columns to have a custom column width, then set this property to a
     non-null value.  Otherwise leave it blank to disable custom column widths.

     @property
         @type SC.IndexSet
     */
    customColumnWidthIndexes: null,

    /**
     Called for each index in the customColumnWidthIndexes set to get the
     actual column width for the index.  This method should return the default
     columnWidth if you don't want the row to have a custom height.

     The default implementation just returns the default columnWidth.

     @param {SC.CollectionView} view the calling view
     @param {Object} content the content array
     @param {Number} contentIndex the index
     @returns {Number} column width
     */
    contentIndexColumnWidth: function(view, content, contentIndex) {
        return this.get('columnWidth');
    }

};
