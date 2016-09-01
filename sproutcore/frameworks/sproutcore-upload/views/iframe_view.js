/*-------------------------------------------------------------------------------------------------
 - Project:   sproutcore-upload                                                                   -
 - Copyright: ©2013 Matygo Educational Incorporated operating as Learndot                         -
 - Author:    Joe Gaudet (joe@learndot.com) and contributors (see contributors.txt)               -
 - License:   Licensed under MIT license (see license.js)                                         -
 -------------------------------------------------------------------------------------------------*/

SC.IFrameView = SC.View.extend({

    result: null,

    tagName: 'iframe',

    classNames: 'sc-file-field-iframe'.w(),

    layout: {
        height: 0,
        width: 0,
        border: 'none'
    },

    attributeBindings: ['src', 'border', 'name', 'width', 'height'],

    name: function () {
        return SC.guidFor(this);
    }.property(),

    border: 0,

    width: 0,

    height: 0,

    src: 'about:blank',

    didCreateLayer: function () {
        SC.Event.add(this.$()[0], "load", this, this.load);

    },

    willDestroyLayer: function () {
        SC.Event.remove(this.$()[0], "load", this, this.load);
    },

    load: function (evt) {
        var result = null, layer = this.$()[0];

        if (layer.contentWindow) { // Iframe body content for IE & Chrome
            if (layer.contentWindow.document.body.firstChild === null) return;

            if (layer.contentWindow.document.body.firstChild.innerHTML) {
                result = layer.contentWindow.document.body.firstChild.innerHTML;
            }
            else {
                // Chrome doesn't seem to have anything in innerHTML, but data gives us what we want
                result = layer.contentWindow.document.body.firstChild.data;
            }
        }
        else if (layer.contentDocument) { // Iframe body content for other browsers

            if (layer.contentDocument.body.firstChild === null) return;

            result = layer.contentDocument.body.firstChild.innerHTML;
        }
        else {
            throw 'Unable to retrieve file upload return value. Unknown iframe DOM structure.';
        }

        try {
            this.set('result', SC.Object.create(JSON.parse(result)));
        } catch (err) {
            // Unable to parse the result
            console.error('Result:');
            console.dirxml(this._iframe.$()[0]);
            throw('Unable to parse file upload return value.\n\n' + err);
        }
    }
});