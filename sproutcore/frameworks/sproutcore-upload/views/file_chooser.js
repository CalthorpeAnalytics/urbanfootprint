/*-------------------------------------------------------------------------------------------------
 - Project:   sproutcore-upload                                                                   -
 - Copyright: ©2013 Matygo Educational Incorporated operating as Learndot                         -
 - Author:    Joe Gaudet (joe@learndot.com) and contributors (see contributors.txt)               -
 - License:   Licensed under MIT license (see license.js)                                         -
 -------------------------------------------------------------------------------------------------*/
sc_require('views/upload_form');
sc_require('views/file_input_view');

/**
 * @class
 *
 * Basic file chooser
 *
 * @extends {SC.View}
 */
SC.FileChooserView = SC.View.extend({

    classNames: 'sc-file-chooser-view',

    childViews: ['buttonView', 'labelView', 'form'],

    url: '',

    result: '',

    resultBinding: SC.Binding.oneWay('.form.result'),

    submitOnChange: YES,

    buttonIcon: 'cloud-upload',

    buttonTitle: 'Choose a File',

    uploadingText: 'Uploading',

    buttonThemeName: 'square',

    showLabel: YES,

    controlSize: SC.REGULAR_CONTROL_SIZE,

    isUploading: SC.outlet('form.isUploading'),

    reset: function() {
        this.get('form').reset();
    },

    submit: function () {
        this.get('form').submit();
    },

    buttonLayout: {
        top: 0,
        bottom: 0,
        width: 140
    },

    labelLayout: {
        top: 0,
        bottom: 0,
        right: 0,
        left: 140
    },

    inputName: 'files[]',

    buttonView: SC.ButtonView.extend({
        layout: SC.outlet('parentView.buttonLayout'),
        controlSize: SC.outlet('parentView.controlSize'),
        themeNameBinding: SC.Binding.oneWay('.parentView.buttonThemeName'),
        classNameBindings: ['hasFocus:focus'],
        iconBinding: SC.Binding.oneWay('.parentView.buttonIcon'),
        title: function () {
            return this.get('isUploading') ? this.getPath('parentView.uploadingText') : this.getPath('parentView.buttonTitle');
        }.property('isUploading'),
        isUploadingBinding: SC.Binding.oneWay('.parentView.form.isUploading'),
        isActiveBinding: SC.Binding.oneWay('.parentView.form.isActive'),
        isEnabledBinding: SC.Binding.oneWay('.isUploading').not(),
        hasFocusBinding: SC.Binding.oneWay('.parentView.form.input.isFirstResponder')
    }),

    labelView: SC.LabelView.extend({
        layout: SC.outlet('parentView.labelLayout'),
        controlSize: SC.outlet('parentView.controlSize'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.showLabel'),
        valueBinding: SC.Binding.oneWay('.parentView.form.input.value')
    }),

    form: SC.UploadFormView.extend({
        submitOnChange: SC.outlet('parentView.submitOnChange'),
        inputName: SC.outlet('parentView.inputName')
    })
})
;