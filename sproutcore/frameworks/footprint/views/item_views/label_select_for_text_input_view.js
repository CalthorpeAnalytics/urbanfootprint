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

sc_require('views/label_select_view');

Footprint.LabelSelectForTextInputView = Footprint.LabelSelectView.extend({
    classNames: ['footprint-select-for-text-input-view'],

    /***
     * Required. Specify the inputView whose value should be set in response to the user clicking enter
     * or clicking on an item in the list
     */
    targetInputView: null,

    menuPaneType: SC.PickerPane,
    menuIsModal: YES,
    preferType: SC.PICKER_MENU,
    preferMatrix: [0, 0, SC.POSITION_BOTTOM],

    /***
     * Make selectable so the user can click items and scroll through them
     */
    isSelectable: YES,
    /***
     * YES by default. If YES, do not clear the selection when the user hits enter or clicks the
     * currently selected item. IF NO, clear the selection so that no selected item is maintained.
     * Normally this should be set to NO if the value is being appended to the input.
     */
    keepSelectionAfterChoosing: YES,

    searchContext: null,
    searchString: null,

    // Does the current active search clause match this LabelSelectView
    matchesSearchClause: NO,

    /***
     * Any change to the labelSelectView selection is reported here and used
     * to set the value of targetInputView, which is presumably an SC.View with a value property.
     * Note that if the input wants to append, it should handle it with a value property setter
     * TODO this could be done with an event instead, but it's had to get the popup to fire events
     */
    selectedItemValueObserver: function() {
        var selectedItemValue = this.get('selectedItemValue');
        var inputView = this.get('targetInputView');
        if (selectedItemValue && inputView) {
            inputView.setValueForMenu(this.escapeValueIfNeeded(selectedItemValue));
        }
    }.observes('.targetInputView', '.selectedItemValue'),

    /***
     * Override to escape values that need it.
     * @param value
     * @returns {*}
     */
    escapeValueIfNeeded: function(value) {
        return value;
    },

    /***
     * When the user hits enter do the same thing as when they hit up from the first item.
     * Their selectedItem will already be in the inputView
     */
    handleEnterFromMenu: function() {
        // Now with focus restored set the selectedItem as if the user typed it.
        var selectedItemValue = this.get('selectedItemValue');
        var inputView = this.get('targetInputView');
        if (selectedItemValue && inputView) {
            inputView.setValueForMenu(this.escapeValueIfNeeded(selectedItemValue));
        }
        // Finalize by setting value
        inputView.finalizeMenuValue();
        // Clear the selection if should not be kept after hitting enter
        if (!this.get('keepSelectionAfterChoosing'))
            this.deselectAllFromMenu();
        inputView.restoreFocus();
    },

    // Observe the matchesSearchClause flag and pop open the menu whenever it's is true.
    // Close the menu if it is false
    matchesSearchObserver: function() {
        // TODO Turning of 'AUTO COMPLETE' functionality for SCAG pilot
        return;

        // If the string actually changed and the menu isn't open, open it up
        if (this.get('matchesSearchClause')) {
            if (!this.getPath('menu.isAttached')) {
                this._acceptKeyPane = NO;
                // Simulate clicking the button so the popup pane initiates fully
                // The pane will popup but not accept keyPane. Thus the input field retains focus
                this._action();
                this._acceptKeyPane = YES;
            }
        }
        else {
            this.removeMenu();
        }
    }.observes('.matchesSearchClause'),

    /***
     * When the user hits key up with the first index selected, make the text input the focus again.
     * We store the last string so that if the user up arrows back to the text input we can restore
     * it. However if they click an item in the list we wipe out the saved string
     */
    handleKeyUpFromFirstItem: function() {
        var inputView = this.getPath('targetInputView');
        if (this.get('searchString'))
            this.set('value', this.get('searchString'));
        inputView.restoreFocus();
        this.deselectAllFromMenu();
    },
});
