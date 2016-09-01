// ==========================================================================
// Project:   SCTable - JavaScript Framework
// Copyright: ©2011 Jonathan Lewis and contributors.
// License:   Licensed under MIT license (see license.js)
// ==========================================================================

/*globals SCTable*/

/*
  Item view used by SCTable.TableHeaderView to render a column header view.
*/

SCTable.TableColumnHeaderView = SC.View.extend(SC.Control, {

  // PUBLIC PROPERTIES
  
  classNames: 'sctable-column-header-view',
  
  /*
    Set to an SCTable.SORT_DIRECTION_ enumeration as defined in core.js.
  */
  sortDirection: null,

  displayProperties: ['sortDirection', 'isMouseOver'],

  /*
    Min width for resize dragging.
  */
  minWidth: 30,

  /*
    YES when mouse is hovering over this view.
  */
  isMouseOver: NO,
  
  // PUBLIC METHODS
  
  contentPropertyDidChange: function() {
    this.displayDidChange();
  },
  
  render: function(context, firstTime) {
    var sortClasses = ['sort-indicator'];
    var sortDirection = this.get('sortDirection');
    var classNames = this.getPath('content.classNames');

    if (!SC.none(sortDirection)) {
      sortClasses.push(sortDirection);
    }

    context = context.addClass('col-%@'.fmt(this.get('contentIndex')));

    if (this.get('isMouseOver')) {
      context = context.addClass('hover');
    }

    if (classNames) {
      context = context.addClass(classNames);
    }

    context = context.begin('div').addClass('col-border').end();

    if (this.getPath('content.name') === this.getPath('content.valueKey')) {
      context = context.begin('div').addClass('col-name').text(this.getPath('content.name')).end();
    } else {
        context = context.begin('label').addAttr('title', this.getPath('content.name'))
              .begin('div').addClass('col-name').text(this.getPath('content.name'))
              .end()
            .end();
    }

    if (this.getPath('content.canSort')) {
      context = context.begin('div').addClass(sortClasses).end();
    }
    
    if (this.getPath('content.canResize')) {
      context = context.begin('div').addClass('resize-handle').end();
    }
  },

  willDestroyLayer: function() {
    this.set('content', null); // make sure all observers disengage.
    this.set('tableDelegate', null);
  },
  
  /*
    Watch for actions on the resize handle div and feed them back to the table.
  */
  mouseDown: function(evt) {
    var ret = NO, del;

    // initialize
    this._isDraggingHandle = NO;
    this._mouseDownInfo = null;

    if (evt.target.className === 'resize-handle') { // take over the event if we're clicking a resize handle
      this._isDraggingHandle = YES;
      this._mouseDownInfo = {
        didMove: NO,
        startPageX: evt.pageX,
        startWidth: this.get('frame').width
      };

      del = this.get('displayDelegate');
      if (del && del.isTableColumnsDelegate) {
        del.beginColumnResizeDrag(evt, this.get('content'), this.get('contentIndex'));
      }

      ret = YES;
    }

    return ret;
  },

  mouseDragged: function(evt) {
    var del, newWidth;

    if (this._isDraggingHandle) {
      this._mouseDownInfo.didMove = YES;
      del = this.get('displayDelegate');

      if (del && del.isTableColumnsDelegate) {
        newWidth = Math.max(this._mouseDownInfo.startWidth + evt.pageX - this._mouseDownInfo.startPageX, this.get('minWidth'));
        del.updateColumnResizeDrag(evt, this.get('content'), this.get('contentIndex'), newWidth);
      }
    }

    return this._isDraggingHandle;
  },
  
  mouseUp: function(evt) {
    var del, newWidth, ret = this._isDraggingHandle;
    
    if (this._isDraggingHandle) {
      newWidth = Math.max(this._mouseDownInfo.startWidth + evt.pageX - this._mouseDownInfo.startPageX, this.get('minWidth'));
      this.setPathIfChanged('content.width', newWidth);

      del = this.get('displayDelegate');
      if (del && del.isTableColumnsDelegate) {
        del.endColumnResizeDrag(evt, this.get('content'), this.get('contentIndex'), newWidth);
      }
    }
    
    // clean up
    this._isDraggingHandle = NO;
    this._mouseDownInfo = null;

    return ret; // take the event if we dragged, to avoid an action getting fired to the owning collection view
  },
  
  mouseEntered: function() {
    //console.log('..mouse entered %@'.fmt(this.get('contentIndex')));
    if (!this.getPath('displayDelegate.isResizeDragInProgress')) {
      this.setIfChanged('isMouseOver', YES);
    }
  },
  
  mouseExited: function() {
    //console.log('..mouse exited %@'.fmt(this.get('contentIndex')));
    if (!this.getPath('displayDelegate.isResizeDragInProgress')) {
      this.set('isMouseOver', NO);
    }
  },
  
  // PRIVATE PROPERTIES

  _isDraggingHandle: NO,
  _mouseDownInfo: null
  
});
