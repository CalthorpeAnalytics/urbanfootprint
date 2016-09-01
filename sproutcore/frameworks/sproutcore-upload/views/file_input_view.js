/*-------------------------------------------------------------------------------------------------
 - Project:   sproutcore-upload                                                                   -
 - Copyright: ©2013 Matygo Educational Incorporated operating as Learndot                         -
 - Author:    Joe Gaudet (joe@learndot.com) and contributors (see contributors.txt)               -
 - License:   Licensed under MIT license (see license.js)                                         -
 -------------------------------------------------------------------------------------------------*/

SC.FileInputView = SC.View.extend(SC.Control, {
    classNames: 'sc-file-field-input-view'.w(),

    layout: {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
    },

    tagName: 'input',

    name: 'files[]',

    type: 'file',

    acceptsFirstResponder: YES,

    multiple: 'false',

    value: 'No File Selected',

    reset: function() {
        this.set('value', null);
        this.$().val(null);
    },

    isEnabled: YES,

    attributeBindings: ['name', 'type', 'multiple', 'accept'],

    accept: '',

    keyEquivalent: 'enter',

    // This helper gets us isEnabled functionality from the SC.Control mixin
    $input: function () {
        return this.$();
    },

    didCreateLayer: function () {
        SC.Event.add(this.$()[0], 'change', this, this.change);
        SC.Event.add(this.$()[0], 'focus', this, this.focus);

        // IE is stupid
        if (SC.browser.isIE) {
            var $this = this.$(), self;
            this.$()[0].onfocus = function (evt) {
                evt.target.blur();
                evt.target.click();
            };
        }
    },

    willDestroyLayer: function () {
        SC.Event.remove(this.$()[0], 'change', this, this.change);
        SC.Event.remove(this.$()[0], 'focus', this, this.focus);
    },

    didBecomeFirstResponder: function () {
        this.$input().focus();
    },

    focus: function (evt) {
        var scroller = this.$().closest('.sc-container-view'),
            stored = scroller.scrollTop();

        var resetMethod = function() {
            scroller.scrollTop(stored);
            this.scrollToVisible();
        }

        if (SC.RunLoop.isRunLoopInProgress()) {
            this.invokeLast(resetMethod);
        }
        else {
            SC.run(resetMethod, this);
        }
        
    },

    insertTab: function () {
        this.getPath('nextValidKeyView').becomeFirstResponder();
        this.$().blur();
        return YES;
    },

    insertBacktab: function () {
        this.getPath('previousValidKeyView').becomeFirstResponder();
        this.$().blur();
        return YES;
    },

    insertNewline: function () {
        this.$().click();
        return YES;
    },

    keyDown: function (evt) {
        return this.isSpace(evt) || this.interpretKeyEvents(evt) || this.performKeyEquivalent(evt.commandCodes()[0], evt);
    },

    isSpace: function (evt) {
        var ret = evt.which === 32;
        if (ret) {
            this.$().click();
        }
        return ret;
    },

    didAppendToDocument: function () {
        this.set('value', null);
    },

    change: function () {
        var value = this.$().val();
        // Scrub "C:\fakepath" from value. Some browsers (notably IE and Chrome) use this to mask the
        // actual path to the file for security reasons.  More here:
        // http://acidmartin.wordpress.com/2009/06/09/the-mystery-of-cfakepath-unveiled/
        if (SC.typeOf(value) === SC.T_STRING && value.indexOf("C:\\fakepath\\") === 0) {
            value = value.slice("C:\\fakepath\\".length);
        }
        if (value) {
            this.set('value', value);
        }
    },

    mouseDown: function (evt) {
        if (!this.get('isEnabled')) return YES;
        evt.allowDefault();
        this.set('isActive', YES);
        return YES;
    },

    mouseUp: function (evt) {
        if (!this.get('isEnabled')) return YES;
        evt.allowDefault();
        this.set('isActive', NO);
        return YES;
    }

});