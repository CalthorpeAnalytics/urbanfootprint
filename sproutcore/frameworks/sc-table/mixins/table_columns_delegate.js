// ==========================================================================
// Project:   SCTable - JavaScript Framework
// Copyright: ©2011 Jonathan Lewis and contributors.
// License:   Licensed under MIT license (see license.js)
// ==========================================================================

/*globals SCTable*/

/*
  Defines an internal communication API for the TableView components.  Not meant to
  be used externally.
*/

SCTable.TableColumnsDelegate = {

  // PUBLIC PROPERTIES
  
  isTableColumnsDelegate: YES,
    
  // PUBLIC METHODS

  beginColumnResizeDrag: function(evt, col, colIndex) {
    //console.log('%@.beginResizeDrag()'.fmt(this));
  },
  
  updateColumnResizeDrag: function(evt, col, colIndex, newWidth) {
    //console.log('%@.updateResizeDrag()'.fmt(this));
  },

  endColumnResizeDrag: function(evt, col, colIndex, newWidth) {
    //console.log('%@.endResizeDrag()'.fmt(this));
  },
  
  tableColumnDidRequestSort: function(col, colIndex, direction) {
    //console.log('%@.tableColumnDidRequestSort(col: %@, colIndex: %@, direction: %@)'.fmt(this, col, colIndex, direction));
  }

};
