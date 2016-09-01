// ==========================================================================
// Project:   SproutCore - JavaScript Application Framework
// Copyright: ©2006-2009 Sprout Systems, Inc. and contributors.
//            Portions ©2008-2009 Apple Inc. All rights reserved.
// License:   Licensed under MIT license (see license.js)
// ==========================================================================

/** @class

    Implements additional hidden form fields for form submission along with a file upload

 @extends SC.View
 @since SproutCore 1.7.1b
 */
SC.FileFieldHiddenInputView = SC.View.extend({
    /**
     tag type to represent this view

     @property {String}
     */
    tagName: 'input',
    /**
     The name of the hidden field

     @property {String}
     */
    name: '',

    /**
     The value to place in the hidden field

     @property {String}
     */
    value: '',

    render: function (context, firstTime) {
        if (firstTime) {
            context.attr('type', 'hidden')
                .attr('name', this.get('name'))
                .attr('value', this.get('value'))
                .end();
        }
    }
});

