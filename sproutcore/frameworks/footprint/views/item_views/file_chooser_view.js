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


sc_require('views/file_chooser');

/***
 * Overrides child views to support localization
 * Notice that this view expects to be with a parentView with form.input.value
 */
Footprint.FileChooserView = SC.FileChooserView.extend({
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
         notUploading: null,
         notUploadingBinding: SC.Binding.oneWay('.isUploading').not(),
         isEnabledBinding: SC.Binding.and('.parentView.isEnabled', '.notUploading'),
         hasFocusBinding: SC.Binding.oneWay('.parentView.form.input.isFirstResponder'),
         // Added
         localize: YES
     }),
     labelView: Footprint.LabelView.extend({
        layout: SC.outlet('parentView.labelLayout'),
        controlSize: SC.outlet('parentView.controlSize'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.showLabel'),
        valueBinding: SC.Binding.oneWay('.parentView.orm.input.value')
     })
});
