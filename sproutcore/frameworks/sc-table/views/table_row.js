// ==========================================================================
// Project:   SCTable - JavaScript Framework
// Copyright: ©2011 Jonathan Lewis and contributors.
// License:   Licensed under MIT license (see license.js)
// ==========================================================================

/*globals SCTable*/

/*
  Item view used by SCTable.TableView to draw one row.  This view calls
  SCTable.TableDelegate.renderTableCellContent() to allow custom cell rendering.
*/

SCTable.TableRowView = SC.View.extend(SC.Control, /*SC.Benchmark,*/ {

  // PUBLIC PROPERTIES
  
  classNames: 'sctable-row-view',
  
  //verbose: YES, // for benchmarking
  
  isMouseOver: NO,

  displayProperties: ['isMouseOver'],

  /*
    Set this to YES if you want rows to be highlighted when the mouse moves over them.
    Note that this slows down the performance of the table somewhat by forcing a re-render
    of any row whose highlight status changes, so for the fastest experience, set it to NO.
    
    Note that this property will be set by the owning TableView to match its global
    'shouldHighlightRowOnMouseOver' property, so you shouldn't have to set it here.
  */
  shouldHighlightRowOnMouseOver: NO,

  /*
    @read-only
  */
  tableDelegate: function() {
    return this.getPath('displayDelegate.tableDelegate');
  }.property('displayDelegate').cacheable(),
  
  // PUBLIC METHODS

  willDestroyLayer: function() {
    this.set('content', null); // make sure all observers disconnect from content
  },

  contentPropertyDidChange: function(target, key) {
    this.displayDidChange();
  },

  // TODO: This render is fast, but make it faster.
  render: function(context, firstTime) {
    //this.start('row render');
    
    var tableDelegate = this.get('tableDelegate');
    var columns = this.getPath('displayDelegate.columns');
    var left = 0, value, width;
    var content = this.get('content');
    var contentIndex = this.get('contentIndex');
    var classes = [(contentIndex % 2 === 0) ? 'even' : 'odd'];
    
    if (this.get('isMouseOver')) {
      classes.push('hover');
    }
  
    context = context.addClass(classes);
  
    if (columns && columns.isEnumerable) {
      columns.forEach(function(col, index) {
        var iconKey = col.get('iconKey');
  
        width = col.get('width') || 0;
        context = context.push('<div class=\"cell col-%@ %@\" style=\"left: %@px; top: 0px; bottom: 0px; width: %@px;\">'.fmt(index, (iconKey ? 'has-icon' : ''), left, width));
        context = tableDelegate.renderTableCellContent(this, context, content, contentIndex, col, index);
        context = iconKey ? context.push('<div class=\"icon %@\"></div></div>'.fmt(content.get(iconKey))) : context.push('</div>');
  
        left += width;
      }, this);
    }
  
    //this.end('row render');
  },

  mouseDown: function(evt) {
    var del = this.get('tableDelegate');
    
    if (del) {
      del.mouseDownOnTableRow(this.get('displayDelegate'), this, evt);
    }
    
    return NO;
  },

  mouseEntered: function(evt) {
    if (this.get('shouldHighlightRowOnMouseOver')) {
      this.set('isMouseOver', YES);
    }
  },

  mouseExited: function(evt) {
    if (this.get('isMouseOver') || this.get('shouldHighlightRowOnMouseOver')) {
      this.set('isMouseOver', NO);
    }
  }

});

SCTable.TableRowView.mixin({
  isReusableInCollections: YES
});
