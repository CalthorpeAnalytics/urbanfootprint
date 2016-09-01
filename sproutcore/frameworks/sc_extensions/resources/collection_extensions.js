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


// TEMPORARY hack to fix broken multiline selection. Search for ABL comments
// This needs to be patched in SC
SC.CollectionView.reopen({
  // ..........................................................
  // MOUSE EVENTS
  //

  /** @private
    Handles mouse down events on the collection view or on any of its
    children.

    The default implementation of this method can handle a wide variety
    of user behaviors depending on how you have configured the various
    options for the collection view.

    @param ev {Event} the mouse down event
    @returns {Boolean} Usually YES.
  */
  mouseDown: function (ev) {
    var content = this.get('content');

    // Fast path!
    if (!content) return this.get('isSelectable');

    var itemView      = this.itemViewForEvent(ev),
        contentIndex  = itemView ? itemView.get('contentIndex') : -1,
        info, anchor, sel, isSelected, modifierKeyPressed, didSelect = NO;
        //allowsMultipleSel = content.get('allowsMultipleSelection');

    // ABL PATCH
    var allowsMultipleSelectionDel = this.delegateFor('allowsMultipleSelection', this.get('delegate'), content);
    allowsMultipleSel = allowsMultipleSelectionDel && allowsMultipleSelectionDel.get('allowsMultipleSelection');

    if (!this.get('isEnabledInPane')) return contentIndex > -1;

    if (!this.get('isSelectable')) return NO;

    // become first responder if possible.
    this.becomeFirstResponder();

    // Toggle the selection if selectOnMouseDown is true
    if (this.get('useToggleSelection')) {
      if (this.get('selectOnMouseDown')) {
        if (!itemView) return; // do nothing when clicked outside of elements

        // determine if item is selected. If so, then go on.
        sel = this.get('selection');
        isSelected = sel && sel.containsObject(itemView.get('content'));

        if (isSelected) {
          this.deselect(contentIndex);
        } else if (!allowsMultipleSel) {
          this.select(contentIndex, NO);
          didSelect = YES;
        } else {
          this.select(contentIndex, YES);
          didSelect = YES;
        }

        if (didSelect && this.get('actOnSelect')) {
          // handle actions on editing
          this._cv_performSelectAction(itemView, ev);
        }
      }

      return YES;
    }

    // received a mouseDown on the collection element, but not on one of the
    // childItems... unless we do not allow empty selections, set it to empty.
    if (!itemView) {
      if (this.get('allowDeselectAll')) this.select(null, false);
      return YES;
    }

    // collection some basic setup info
    sel = this.get('selection');
    if (sel) sel = sel.indexSetForSource(content);

    info = this.mouseDownInfo = {
      event:        ev,
      itemView:     itemView,
      contentIndex: contentIndex,
      at:           Date.now()
    };

    isSelected = sel ? sel.contains(contentIndex) : NO;
    info.modifierKeyPressed = modifierKeyPressed = ev.ctrlKey || ev.metaKey;


    // holding down a modifier key while clicking a selected item should
    // deselect that item...deselect and bail.
    if (modifierKeyPressed && isSelected) {
      info.shouldDeselect = contentIndex >= 0;

    // if the shiftKey was pressed, then we want to extend the selection
    // from the last selected item
    } else if (ev.shiftKey && sel && sel.get('length') > 0 && allowsMultipleSel) {
      sel = this._findSelectionExtendedByShift(sel, contentIndex);
      anchor = this._selectionAnchor;
      this.select(sel);
      this._selectionAnchor = anchor; //save the anchor

    // If no modifier key was pressed, then clicking on the selected item
    // should clear the selection and reselect only the clicked on item.
    } else if (!modifierKeyPressed && isSelected) {
      info.shouldReselect = contentIndex >= 0;

    // Otherwise, if selecting on mouse down,  simply select the clicked on
    // item, adding it to the current selection if a modifier key was pressed.
    } else {

      if ((ev.shiftKey || modifierKeyPressed) && !allowsMultipleSel) {
        this.select(null, false);
      }

      if (this.get("selectOnMouseDown")) {
        this.select(contentIndex, modifierKeyPressed);
      } else {
        info.shouldSelect = contentIndex >= 0;
      }
    }

    // saved for extend by shift ops.
    info.previousContentIndex = contentIndex;

    return YES;
  },

  /** @private */
  mouseUp: function (ev) {
    var view = this.itemViewForEvent(ev),
        info = this.mouseDownInfo,
        content = this.get('content');

    // Fast path!
    if (!content) {
      this._cleanupMouseDown();
      return true;
    }

    var contentIndex = view ? view.get('contentIndex') : -1,
        sel, isSelected, canEdit, itemView, idx;
        //allowsMultipleSel = content.get('allowsMultipleSelection');
    // ABL PATCH
    var allowsMultipleSelectionDel = this.delegateFor('allowsMultipleSelection', this.get('delegate'), content);
    allowsMultipleSel = allowsMultipleSelectionDel && allowsMultipleSelectionDel.get('allowsMultipleSelection');

    if (!this.get('isEnabledInPane')) return contentIndex > -1;
    if (!this.get('isSelectable')) return NO;

    if (this.get('useToggleSelection')) {
      // Return if clicked outside of elements or if toggle was handled by mouseDown
      if (!view || this.get('selectOnMouseDown')) return NO;

      // determine if item is selected. If so, then go on.
      sel = this.get('selection');
      isSelected = sel && sel.containsObject(view.get('content'));

      if (isSelected) {
        this.deselect(contentIndex);
      } else if (!allowsMultipleSel) {
        this.select(contentIndex, NO);
      } else {
        this.select(contentIndex, YES);
      }

    } else if (info) {
      idx = info.contentIndex;
      contentIndex = (view) ? view.get('contentIndex') : -1;

      // this will be set if the user simply clicked on an unselected item and
      // selectOnMouseDown was NO.
      if (info.shouldSelect) this.select(idx, info.modifierKeyPressed);

      // This is true if the user clicked on a selected item with a modifier
      // key pressed.
      if (info.shouldDeselect) this.deselect(idx);

      // This is true if the user clicked on a selected item without a
      // modifier-key pressed.  When this happens we try to begin editing
      // on the content.  If that is not allowed, then simply clear the
      // selection and reselect the clicked on item.
      if (info.shouldReselect) {

        // - contentValueIsEditable is true
        canEdit = this.get('isEditable') && this.get('canEditContent');

        // - the user clicked on an item that was already selected
        //   ^ this is the only way shouldReset is set to YES

        // - is the only item selected
        if (canEdit) {
          sel = this.get('selection');
          canEdit = sel && (sel.get('length') === 1);
        }

        // - the item view responds to contentHitTest() and returns YES.
        // - the item view responds to beginEditing and returns YES.
        if (canEdit) {
          itemView = this.itemViewForContentIndex(idx);
          canEdit = itemView && (!itemView.contentHitTest || itemView.contentHitTest(ev));
          canEdit = (canEdit && itemView.beginEditing) ? itemView.beginEditing() : NO;
        }

        // if cannot edit, schedule a reselect (but give doubleClick a chance)
        if (!canEdit) {
          if (this._cv_reselectTimer) this._cv_reselectTimer.invalidate();
          this._cv_reselectTimer = this.invokeLater(this.select, 300, idx, false);
        }
      }

      this._cleanupMouseDown();
    }

    // handle actions on editing
    this._cv_performSelectAction(view, ev, 0, ev.clickCount);

    return NO;  // bubble event to allow didDoubleClick to be called...
  }
});
