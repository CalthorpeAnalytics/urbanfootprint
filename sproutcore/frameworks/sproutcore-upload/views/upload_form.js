/*-------------------------------------------------------------------------------------------------
 - Project:   sproutcore-upload                                                                   -
 - Copyright: ©2013 Matygo Educational Incorporated operating as Learndot                         -
 - Author:    Joe Gaudet (joe@learndot.com) and contributors (see contributors.txt)               -
 - License:   Licensed under MIT license (see license.js)                                         -
 -------------------------------------------------------------------------------------------------*/
sc_require('views/iframe_view');
sc_require('views/file_input_view');

/**
 * @class Hidden form for conducting fake ajax style upload
 *
 * @extends {SC.View}
 */
SC.UploadFormView = SC.View.extend({

    layout: {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
    },

    childViews: ['input', 'iframe'],

    classNames: 'sc-file-field-form'.w(),

    /**
     * Bind attributes to the dom values
     */
    attributeBindings: ['name', 'method', 'action', 'enctype', 'encoding', 'target'],

    tagName: 'form',

    name: SC.Binding.oneWay('.layerId'),

    uuid: function () {
        var uuid = "", i;
        for (i = 0; i < 24; i += 1) {
            uuid += Math.floor(Math.random() * 16);
        }
        return uuid;
    }.property().cacheable(),

    url: '',

    action: function () {
        var url = this.get('url');
        return "%@X-Progress-ID=%@".fmt(url.match(/\?/) ? url + '&' : url + '?', this.get('uuid'));
    }.property('url', 'uuid').cacheable(),

    target: '',

    targetBinding: '*iframe.name',

    method: 'post',

    enctype: 'multipart/form-data',

    encodingBinding: SC.Binding.oneWay('.enctype'),

    isUploading: NO,

    isEnabledBinding: SC.Binding.oneWay('.isUploading').not(),

    isActiveBinding: SC.Binding.oneWay('.input.isActive'),

    resultBinding: SC.Binding.oneWay('.iframe.result'),

    valueBinding: SC.Binding.oneWay('.input.value'),

    urlBinding: SC.Binding.oneWay('.parentView.url'),

    inputName: 'files[]',

    submitOnChange: YES,

    accept: '',

    valueDidChange: function () {
        var value = this.get('value');
        if (value && value !== 'No File Selected') {
            this.submit();
        }
    }.observes('value'),

    submit: function () {
        this.set('isUploading', YES);
        this.$()[0].submit();
    },

    reset: function () {
        this.iframe.set('result', null);
        this.input.reset();
    },

    willDestroyLayer: function () {
        this.removeAllChildren();
    },

    iframe: SC.IFrameView.extend({
        load: function () {
            sc_super();
            this.setPath('parentView.isUploading', NO);
        }
    }),

    input: SC.FileInputView.extend({
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        accept: SC.outlet('parentView.accept'),
        name: SC.outlet('parentView.inputName')
    })

});