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


/***
 * The InputView for a SelectOrAddView.
 * TODO all references to parentView below should be replaced by sending events
 */
Footprint.SelectOrAddInputView = Footprint.EditableModelStringView.extend({
    classNames: ['footprint-select-or-add-input-view'],

    // Temporary set to YES to keep the menu open when the focus changes from the input field
    // to the popup menu via a downkey stroke
    _leaveMenuOpen: NO,

    labelSelectView: null,

    content:null,

    isTextArea: YES,
    // Default false. If true, append menu selections to the input view. This is probably
    // only used in conjunction with isTextArea set true
    appendSelectionToInput: NO,

    // The searchString which determines what is filtered in the menu pane
    // This matches the value unless the user is going through results in the menu pane
    searchContext: function() {
        return this.get('parentView').createSearchContext(this.get('nonMenuValue'));
    }.property('nonMenuValue').cacheable(),

    searchString: function() {
        return this.getPath('searchContext.searchString');
    }.property('searchContext').cacheable(),

    addAction: null,

    hint: null,

    // The lone selected item of the selection
    selectedItem: null,
    // The value of the selectedItem based on itemTitleKey or selectedItem if the latter is null
    selectedItemValue: null,

    nonMenuValue: null,
    _value:  null,
    /***
     * Updating the values updates the nonMenuValue, which the searchContext depends on
     */
    value: function(propKey, value) {
        if (value !== undefined) {
            // This only changes when set('value' is called
            this.set('nonMenuValue', value);
            // This is updated here and by setValueForMenu
            this.set('_value', value);
        }
        // Return the _value or an empty string so we don't display 'null'
        var val = this.get('_value');
        return (!val || val=='null') ? null : val;
    }.property('_value'),

    // There seems to be a major bug in text_field where value doesn't update when command keys like the following
    // are typed, rather than normal keys. This corrects the problem by notifying that a fieldValueDidChang
    // needs to run to sync value to the underlying html DOM value
    deleteBackward: function() {
        var ret = sc_super();
        this._fieldValueDidChangeTimer = this.invokeLater(this.fieldValueDidChange, 10);
        return ret;
    },
    deleteForward: function() {
        var ret = sc_super();
        this._fieldValueDidChangeTimer = this.invokeLater(this.fieldValueDidChange, 10);
        return ret;
    },
    insertNewline: function() {
        var ret = sc_super();
        this._fieldValueDidChangeTimer = this.invokeLater(this.fieldValueDidChange, 10);
        return ret;
    },
    insertTab: function() {
        var ret = sc_super();
        this._fieldValueDidChangeTimer = this.invokeLater(this.fieldValueDidChange, 10);
        return ret;
    },
    insertBacktab: function() {
        var ret = sc_super();
        this._fieldValueDidChangeTimer = this.invokeLater(this.fieldValueDidChange, 10);
        return ret;
    },

    /***
     * This setter is used by the dropdown menu to update value
     * It's different than entering input text because the dropdown menu value is
     * meant to sometimes replace the tokenValue or tokenType of the current searchContext clause.
     * For instance if the user starts typing an attribute and then selects an item from the list
     * to complete the typing we want to replaced the typed part with the selected value
     * @param value
     * it simply appends
     */
    setValueForMenu: function(value) {
        // TODO simply always append for SCAG pilot release

            // TODO this will insert at the carrot or replace the selection if I can keep the clicking
            // or drop downs from activating select all
        //var textSelection = this.get('selection');
        //var val = this.get('_value') || '';
        //var selectionStart = textSelection ? textSelection.get('start') : val.get('length');
        //var selectionEnd = textSelection ? textSelection.get('end') : val.get('length');
        //var textUpToStart = (this.get('_value') || '').slice(0, selectionStart);
        //var textToToEnd = (this.get('_value') || '').slice(selectionEnd, -1);
        //this.set(
        //    '_value',
        //    '%@%@%@'.fmt(textUpToStart, value, textToToEnd)
        //);

        if (this.get('appendSelectionToInput')) {
            this.set(
                '_value',
                (this.get('_value') ? '%@ '.fmt(this.get('_value')) : '').concat(value)
            );
        }
        else {
            this.set('_value', value);
        }
        return;

        if (value !== undefined) {
            // The value is coming from the user selecting from the menu
            // Just have it replace the portion of the previous value
            // that represents the searchString portion of the string, which might be the entire value
            var searchContext = this.get('parentView').createSearchContext(this.get('value'));
            var searchString = searchContext.get('searchString');
            var clause = searchContext.get('clause');
            // If searchString is null it means there is an error parsing. Try to get what the user has typed
            if (!searchString && searchString != '')
                searchString = (clause['tree'] && clause['tree'].isEnumerable && clause['tree'].slice(-1)[0]['tokenValue']) || searchString;
            // Make sure to replace the last occurrence of the searchString with the value, unless it's whitespace
            // If the tokenType is a string we have to account for the fact that the searchString when parsed
            // doesn't maintain it's quotes, but our value will have quotes
            var escapedSearchString = escapeRegExp(searchString || '');
            var regex = searchContext.get('tokenType')=='STRING' ?
                RegExp('\'%@\'$'.fmt(escapedSearchString)):
                RegExp('%@$'.fmt(escapedSearchString));
            if (searchString && !searchString.match(/^\s+$/)) {
                this.set(
                    '_value',
                    this.get('_value').replace(regex, value)
                );
            }
            else {
                this.set(
                    '_value',
                    (this.get('_value') || '').concat(value)
                );
            }
        }
    },

    /***
     * When a menu item is clicked or entered (not just selected),
     * set value to the _value, which updates nonMenuValue to _value
     */
    finalizeMenuValue: function() {
        this.set('value', this.get('_value'));
    },

    /***
     * Override to clear the menu pane
     */
    willLoseFirstResponder: function() {
        sc_super();
        var labelSelectView = this.get('labelSelectView');
        labelSelectView.deselectAllFromMenu();
        if (!this._leaveMenuOpen)
            this.get('parentView').removeMenu();
    },
    /***
     * When the user hits key down select the first item of the menu if one exists
     * If the user hits RETURN pretend that the add button was hit
     * @param evt
     * @returns {boolean}
     */
    keyDown: function(evt) {
        var ret = sc_super();
        // Don't continue if modifiers are down. For some reason typing paren
        // functions as a KEY_DOWN
        if (evt.shiftKey || evt.metaKey || evt.altKey || evt.ctrlKey)
            return ret;
        if (evt.keyCode === SC.Event.KEY_DOWN) {
            // Don't handle, the code doesn't currently support this
            return ret;
            //this._leaveMenuOpen = YES;
            //this.get('parentView').handleDownKey();
            //this._leaveMenuOpen = NO;
            //return YES;
        }
        else if (evt.keyCode === SC.Event.KEY_RETURN && this.get('value')) {
            // Add whatever is currently typed or selected. This will only succeed if
            // the item isn't already in the list, unless we are appending
            if (this.get('addAction')) {
                var labelSelectView = this.get('labelSelectView');
                labelSelectView.deselectAllFromMenu();
                Footprint.statechart.sendAction(
                    this.get('addAction'),
                    SC.Object.create({value: this.get('value')})
                );
            }
        }
        else {
            return ret;
        }
    },

    /***
     * When the user hits the up key from the top item of the menu pane, restore focus
     * to the input, optionally restoring the user's last string if nothing was clicked
     * or entered in the menu pane
     */
    restoreFocus: function() {
        this._leaveMenuOpen = YES;
        this.becomeFirstResponder();
        this.get('pane').becomeKeyPane();
        this._leaveMenuOpen = NO;
        // Always set the cursor to the end of the text
        this.invokeNext(function() {
            this.set(
                'selection',
                SC.TextSelection.create({
                    start: this.getPath('value.length'),
                    end: this.getPath('value.length')
                }));
        });
    },

    /***
     * Returns true if value is one of the content items' itemTitleKey
     */
    valueInItems: function() {
        return (this.get('content') || []).find(function(item) {
            return item.get(this.get('itemTitleKey')) == this.get('value');
        }, this);
    }.property('content', 'itemTitleKey', 'value').cacheable()
});
