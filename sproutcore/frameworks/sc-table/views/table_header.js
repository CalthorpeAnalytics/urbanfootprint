// ==========================================================================
// Project:   SCTable - JavaScript Framework
// Copyright: ©2011 Jonathan Lewis and contributors.
// License:   Licensed under MIT license (see license.js)
// ==========================================================================

/*globals SCTable*/

sc_require('mixins/table_columns_delegate');

/*
  Extends SC.CollectionView to render the table's header.
*/

SCTable.TableHeaderView = SC.CollectionView.extend(SCTable.TableColumnsDelegate, {

  // PUBLIC PROPERTIES

  classNames: 'sctable-header-view',

  /*
    Mirrors the SCTable.TableView.sort property.  See table.js for documentation.
  */
  sort: null,

  /*
    Pointer to the TableView that owns this header.
  */
  ownerTableView: null,

  ghostActsLikeCursor: YES,

  /*
    @read-only
    YES while a column edge is being dragged for resizing.
  */
  isResizeDragInProgress: NO,

  /*
    YES if we should continually resize a column whose resize handle is being dragged.
    If NO, the column header view itself will only be resized after the drag ends.
  */
  shouldLiveResize: YES,

  /*
    View class definition for showing the insertion point for reorder dragging.
  */
  insertionPointView: SC.View.extend({
    backgroundColor: '#57647F',
    layout: { left: 0, top: 0, bottom: 0, width: 2 },
    render: function(context, firstTime) {
      if (firstTime) {
        context.push('<div class=\"anchor\"></div>');
      }
    }
  }),

  // PUBLIC METHODS

  layoutForContentIndex: function(contentIndex) {
    var content = this.get('content');
    var left = 0, width, ret;
    
    // TODO: Set up an internal lookup table of some sort to avoid the brute force looping search here.
    if (content && content.isEnumerable) {
      content.forEach(function(col, index) {
        if (index < contentIndex) {
          left += col.get('width');
        }
        else if (index === contentIndex) {
          width = col.get('width');
        }
      });
      
      ret = {
        left: left,
        width: width
      };
    }

    return ret;
  },

  /*
    Overriding from SC.CollectionView to apply sort info to each item view prior
    to creation.
  */
  createItemView: function(exampleClass, idx, attrs) {
    var sort = this.get('sort');
    var valueKey = sort ? sort.valueKey : null;
        
    if (attrs.content && (attrs.content.get('valueKey') === valueKey)) {
      attrs.sortDirection = sort ? sort.direction : null;
    }
    else {
      delete attrs.sortDirection; // attrs is reused, so clean it up
    }

    return exampleClass.create(attrs);
  },

  tableColumnDidRequestSort: function(col, colIndex, direction) {
    var del = this.get('ownerTableView');

    //console.log('%@.tableColumnDidRequestSort(col: %@, colIndex: %@, direction: %@)'.fmt(this, col, colIndex, direction));

    if (del && del.tableColumnDidRequestSort) {
      del.tableColumnDidRequestSort(col, colIndex, direction);
    }
  },

  collectionViewDragViewFor: function(view, dragContent) {
    var ret;
    var height = 30;
    var names = [];
    
    dragContent.forEach(function(i) {
      var itemView = this.itemViewForContentIndex(i);
      if (itemView) {
        names.push(itemView.getPath('content.name'));
      }
    }, this);

    ret = SC.View.create({
      layout: { width: 100, height: height * names.length },
      backgroundColor: 'gray',
      content: names,
      rowHeight: height,
      
      createChildViews: function() {
        var childViews = [];
        var names = this.get('content'), i;
        var rowHeight = this.get('rowHeight');

        if (names) {
          for (i = 0; i < names.length; i++) {
            childViews.push(this.createChildView(SC.LabelView, {
              layout: { left: 0, right: 0, top: rowHeight * i, height: rowHeight },
              value: names[i]
            }));
          }
        }

        this.set('childViews', childViews);
      }
    });

    return ret;
  },

  insertionIndexForLocation: function(loc, dropOperation) { 
    var childViews = this.get('childViews');
    var i, frame;
    var ret = -1;
    
    if (childViews) {
      
      // TODO: Set up an internal lookup table of some sort to avoid the brute force looping search here.
      for (i = 0; i < childViews.length; i++) {
        frame = childViews[i].get('frame');
        
        if ((loc.x >= frame.x) && (loc.x <= (frame.x + frame.width))) {
          ret = [i, SC.DROP_AFTER];

          if ((loc.x - frame.x) < ((frame.x + frame.width) - loc.x)) {
            ret[1] = SC.DROP_BEFORE;
          }

          break;
        }
      }
    }

    return ret;
  },
  
  showInsertionPoint: function(itemView, dropOperation) {
    //console.log('%@.showInsertionPoint(itemView: %@, dropOperation: %@)'.fmt(this, itemView, dropOperation));
    
    var view = this._insertionPointView;
    var frame = itemView.get('frame');
    var left = frame.x;
    
    if (!view) {
      view = this._insertionPointView = this.get('insertionPointView').create();
    }
    
    if (dropOperation & SC.DROP_AFTER) {
      if (itemView.get('contentIndex') === (this.get('length') - 1)) {
        left = frame.x + frame.width - view.get('frame').width;
      }
      else {
        left = frame.x + frame.width;
      }
    }
    
    view.adjust({ left: left });
    this.appendChild(view);
  },
  
  hideInsertionPoint: function() {
    //console.log('%@.hideInsertionPoint()'.fmt(this));
    if (this._insertionPointView) {
      this._insertionPointView.removeFromParent().destroy();
    }
    this._insertionPointView = null;
  },
  
  beginColumnResizeDrag: function() {
    //console.log('%@.beginResizeDrag()'.fmt(this));
    this.set('isResizeDragInProgress', YES);
  },
  
  updateColumnResizeDrag: function(evt, col, colIndex, newWidth) {
    //console.log('%@.updateResizeDrag()'.fmt(this));

    if (this.get('shouldLiveResize')) {
      this._resizeData = {
        evt: evt,
        col: col,
        colIndex: colIndex,
        newWidth: newWidth
      };
    
      this.invokeOnce('_overrideColumnWidth');
    }
  },

  endColumnResizeDrag: function() {
    //console.log('%@.endResizeDrag()'.fmt(this));
    this.set('isResizeDragInProgress', NO);
    this._resizeData = null; // clean up
  },
  
  // PRIVATE METHODS
  
  _sortDidChange: function() {
    //console.log('%@._sortDidChange(%@)'.fmt(this, this.get('sort')));
    this.invokeOnce('_updateSortView');
  }.observes('sort'),
  
  _updateSortView: function() {
    var childViews = this.get('childViews'), i, col;
    var sort = this.get('sort');
    var valueKey = sort ? sort.valueKey : null;
    var dir = sort ? sort.direction : null;
    
    //console.log('%@._updateSortView()'.fmt(this));

    if (childViews) {
      for (i = 0; i < childViews.length; i++) {
        col = childViews[i].get('content');
        
        if (col) {
          if (col.get('valueKey') === valueKey) {
            childViews[i].set('sortDirection', dir);
          }
          else {
            childViews[i].set('sortDirection', null);
          }
        }
      }
    }
  },
  
  _overrideColumnWidth: function() {
    var columns, length, i, itemView, left, frame;
    
    if (this._resizeData) {
      columns = this.get('content');
      length = columns ? columns.get('length') : 0;
      
      this.beginPropertyChanges();

      if (this._resizeData.colIndex < length) {
        itemView = this.itemViewForContentIndex(this._resizeData.colIndex);
        if (itemView) {
          itemView.adjust({ width: this._resizeData.newWidth });
          left = itemView.get('frame').x + this._resizeData.newWidth;
        }

        for (i = this._resizeData.colIndex + 1; i < length; i++) {
          itemView = this.itemViewForContentIndex(i);
          frame = itemView.get('frame');
          itemView.adjust({ left: left });
          left = left + frame.width;
        }
      }

      this.endPropertyChanges();
    }
  },
  
  // PRIVATE PROPERTIES
  
  _resizeData: null,
  _insertionPointView: null

});
