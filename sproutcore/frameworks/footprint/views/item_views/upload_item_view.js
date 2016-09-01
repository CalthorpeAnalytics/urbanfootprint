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

sc_require('views/upload_form_view');
sc_require('views/item_views/file_chooser_view');

Footprint.UploadItemView = SC.View.extend({
    childViews: ['uploadButtonView', 'hasFileView'],
    // The context of the upload. In our case this is currently a controller with a ConfigEntity,
    // which we want to be the target of the upload, but it could be something else
    // The context is sent to the data_source
    context: null,
    buttonTitle: null,
    fileName: SC.outlet('uploadButtonView.form.lastValue'),
    hasNewFile: SC.outlet('hasFileView.isVisible'),
    isUploading: null,
    isUploadingBinding: SC.Binding.oneWay('.uploadButtonView.isUploading'),

    uploadButtonView: Footprint.FileChooserView.extend({
        layout: { height: 42, left: 0},
        buttonTitleBinding: SC.Binding.oneWay('.parentView.buttonTitle'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),

        buttonLayout: {
            top: 0,
            height: 24,
            width: 100
        },
        labelLayout: {
            top: 26,
            bottom: 0,
            right: 0,
            left: 0
        },

        context: null,
        contextBinding: SC.Binding.oneWay('.parentView.context'),

        /***
         * Fetches the uploadUri passing the context to the DataSource to set any necessary parameters
         */
        url: function() {
            var context = this.get('context');
            return context ?
                Footprint.store.dataSource.uploadUri(context) :
                '/content-not-set'; // action can handle null
        }.property('context').cacheable(),

        // bending over backwards to proxy isUploading to somewhere central
        isUploadingBinding: SC.Binding.oneWay('.form.isUploading'), // this should be in the view class, not here.
        resultDidUpdate: function() {
            return;
            // TODO no longer relevant
            var result = this.get('result');
            // We need to know the extension of the submitted file
            if (!result || !this.get('content'))
                return;
            var extension = this.getPath('form.value').split('.').slice(-1)[0];
            this.setPath('content.upload_id', '%@.%@'.fmt(result.upload_id, extension));
            this.setPath('content.srid', result.srid);
            this.reset()
        }.observes('result'),

        form: Footprint.UploadFormView.extend({
            submitOnChange: SC.outlet('parentView.submitOnChange'),
            inputName: SC.outlet('parentView.inputName')
        })
    }),

    hasFileView: SC.LabelView.extend({
        layout: { top: 30, bottom: 0},
        hasFile: null,
        hasFileBinding: SC.Binding.oneWay('.parentView*content.upload_id').bool(),
        fileName: null,
        fileNameBinding: SC.Binding.oneWay('.parentView.fileName'),
        isNew: null,
        isNewBinding: SC.Binding.oneWay('.pane.contentIsNew'),
        isVisibleBinding: SC.Binding.and('.hasFile', '.isNew'),
        value: function() {
            return 'File %@ successfully uploaded, okay to save layer...'.fmt(this.get('fileName'));
        }.property('fileName').cacheable()
    })
});
