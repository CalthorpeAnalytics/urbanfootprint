/*-------------------------------------------------------------------------------------------------
 - Project:   sproutcore-upload                                                                   -
 - Copyright: ©2013 Matygo Educational Incorporated operating as Learndot                         -
 - Author:    Joe Gaudet (joe@learndot.com) and contributors (see contributors.txt)               -
 - License:   Licensed under MIT license (see license.js)                                         -
 -------------------------------------------------------------------------------------------------*/

sc_require('views/spinner_view');
sc_require('views/upload_form');

SC.ImageUploadView = SC.View.extend({

    childViews: ['spinnerView', 'uploadForm'],

    classNames: 'sc-image-upload-view',

    classNameBindings: ['isActive:active', 'hasValue:has-value', 'hasFocus:focus'],

    displayProperties: ['imageUrl'],

    url: '',

    imageUrl: '',

    isActiveBinding: SC.Binding.oneWay('*uploadForm.isActive'),

    isEnabledBinding: SC.Binding.oneWay('*uploadForm.isEnabled'),

    resultBinding: SC.Binding.oneWay('*uploadForm.result'),

    hasValueBinding: SC.Binding.oneWay('.value').bool(),

    uploadOnChange: YES,

    isUploading: NO,

    hasFocusBinding: SC.Binding.oneWay('.uploadForm.input.isFirstResponder'),

    /**
     * Adds our icon dom object
     * @param context
     */
    render: function (context) {
        context.begin().addClass('icon').end();
        context.addStyle('background-image', "url('%@')".fmt(this.get('imageUrl')));
    },

    /**
     * Updateds the existing dom object with the url
     */
    update: function () {
        this.invokeLast(function () {
            var imageUrl = this.get('imageUrl');
            if (imageUrl) {
                this.$().css({"background-image": "url('%@')".fmt(imageUrl)});
            }
        });
    },

    _setBackground: function () {

    },

    /**
     * Extract the image url from the result
     * @param {SC.Object} result
     * @return {String}
     */
    imageUrlFromResult: function (result) {
        return result.get('url');
    },

    /**
     * Extract the value from the result
     * @param {SC.Object} result
     * @return {String}
     */
    valueFromResult: function (result) {
        return result.get('url');
    },

    /**
     * Extract the result from the value, this is for a case where you are
     * editing an existing value - in our case we will return the value, but in
     * some cases we might  want to fetch a record from the store
     * @param {String} value
     * @return {SC.Object}
     */
    resultFromValue: function (value) {
        return value ? this.get('result') : null;
    },

    valueDidChange: function () {
        this.set('result', this.resultFromValue(this.get('value')));
    }.observes('value'),

    /**
     * Observes the result and it's status (if it's a record) and updates
     * the url accordingly
     */
    resultDidChange: function () {
        var result = this.get('result'), imageUrl;
        if (result) {
            imageUrl = this.imageUrlFromResult(result);
            if (imageUrl) {
                SC.imageQueue.loadImage(imageUrl, this, function (imageUrl) {
                    this.set('isUploading', NO);
                    this.set('imageUrl', imageUrl);
                    this.setIfChanged('value', this.valueFromResult(result));
                });
            }
        }
        else {
            this.set('imageUrl', '');
        }
    }.observes('*result.status'),

    // **************************************************
    // Drop Support

    /**
     * If the browser supports FormData posting we will allow this object to
     * handle drag and drop uploading so we need to setup some events
     */
    didCreateLayer: function () {
        if (window.FormData) {
            SC.Event.add(this.$(), "dragover", this, this._dragover);
            SC.Event.add(this.$(), "drop", this, this._drop);
        }
    },

    /**
     * Tear down any drag and drop events we may have setup
     */
    willDestroyLayer: function () {
        if (window.FormData) {
            SC.Event.remove(this.$(), "drop", this, this._drop);
            SC.Event.remove(this.$(), "dragover", this, this._dragover);
        }
    },

    /**
     * Drop event handler
     * @param {SC.Event} event
     * @private
     */
    _drop: function (event) {
        event.preventDefault();
        this._uploadFile(event.dataTransfer.files[0]);
    },

    _dragover: function (e) {
        e.preventDefault();
    },

    _uploadFile: function (file) {
        if (file.type.match(/image/)) {
            this.set('isUploading', YES);
            var fd = new FormData();
            fd.append('file', file);
            SC.Request.postUrl(this.get('url'), fd).notify(this, '_didUploadFile').send();
        }
    },

    _didUploadFile: function (response) {
        this.set('result', SC.Object.create(JSON.parse(response.get('body'))));
    },

    // **************************************************
    // views
    //

    uploadForm: SC.UploadFormView.extend({
        uploadForm: SC.outlet('parentView.url'),
        isUploadingDidChange: function () {
            this.setPath('parentView.isUploading', YES);
        }.observes('isUploading'),

        accept: 'image/*',
        delegate: SC.outlet('parentView'),

        didAppendToDocument: function () {
            this.set('value', null);
            this.$().each(function () {
                this.reset();
            });
        },

        input: SC.FileInputView.extend({
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            accept: SC.outlet('parentView.accept')
        })
    }),

    spinnerView: SC.SpinnerView.extend({
        layout: {
            top: 0,
            right: 0,
            bottom: 0,
            left: 0
        },
        isVisibleBinding: SC.Binding.oneWay('.parentView.isUploading')
    })
})
;