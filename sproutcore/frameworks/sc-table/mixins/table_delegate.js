// ==========================================================================
// Project:   SCTable - JavaScript Framework
// Copyright: ©2011 Jonathan Lewis and contributors.
// License:   Licensed under MIT license (see license.js)
// ==========================================================================

/*globals SCTable*/

/*
  Defines the TableView's delegate API.  By default the TableView is also its
  own delegate, but if you'd like to define your own delegate to override any of
  these functions, simply mix this into an object and point the TableView.delegate
  property at it.  That object will then start getting these requests.
*/

SCTable.TableDelegate = {

  // PUBLIC PROPERTIES
  
  isTableDelegate: YES,
  
  // PUBLIC METHODS

  /*
    Called when someone clicks on a column header view after it has already been
    selected, indicating a request to sort.
    
    To allow the TableView to handle sorting itself, return NO to indicate you did
    not handle it.
    
    To handle it yourself, override this method and return YES to indicate that
    you're handling the request (i.e. inline, or with a server call, etc).
    When your sort is finished, set the TableView.sort property to update the view
    with the kind of sort that you performed.
  */
  tableDidRequestSort: function(tableView, content, column, columnIndex, direction) {
    return NO; // return NO if we did not handle it.  The TableView will then use its default sort.
  },
  
  /*
    This method is called once per cell being rendered, to generate the content of the
    cell's outer div element.  Override it to add custom content.  By default it simply
    pushes an additional div containing the cell's value as text onto the render context.
    
    This method is called quite often, so keep it fast for the best table performance.
    If you're rendering user-saved data, make sure it's safe as well as this function
    pushes HTML code straight into the DOM.
    
    NOTE: Always return the render context, even if you do nothing with it.  This
    function is a subroutine in an existing render() call.
  */
  renderTableCellContent: function(tableView, renderContext, rowContent, rowIndex, column, columnIndex) {
    return renderContext.push('<div class=\"text\">%@</div>'.fmt(
        SC.RenderContext.escapeHTML(String(rowContent ? rowContent[column.get('valueKey')] : null))));
  },
  
  /*
    Called when a mouse-down occurs on a table row view.  'evt' is the original mouse event, so you can
    query it for the actual DOM target that was hit if desired.
  */
  mouseDownOnTableRow: function(tableView, rowView, evt) {
  }

};
