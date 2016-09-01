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


Footprint.UploadFormView = SC.UploadFormView.extend({

    // Override this so that we can catch errors
    iframe: SC.IFrameView.extend({
        load: function () {
            try {
                sc_super()
            }
            catch(e) {
                // Clear the value so the user can try again
                this.setPath('parentView.input.value', null);
                SC.AlertPane.warn({
                    message: "Upload failed",
                    description: "Please try again. If the upload continues to fail, contact technical support for help"
                });
            }
            this.setPath('parentView.isUploading', NO);
        }
    }),
    lastValue: null,

    /***
     * Override to add the file_name parameter
     */
    action: function () {
        return '%@&file_name=%@'.fmt(sc_super(), this.get('value'));
    }.property('url', 'uuid', 'value').cacheable(),

    // Override to prepend a timestamp so that ids increase with time
    uuid: function () {
        var uuid = sc_super();
        return '%@-%@'.fmt(SC.DateTime.create().get('milliseconds'), uuid);
    }.property().cacheable(),

    // Add our own observer to store the lastValue
    valueDidChange: function () {
        var value = this.get('value');
        if (value && value !== 'No File Selected') {
            this.set('lastValue', this.get('value'));
            // Force the uuid to change. This updates the action before we submit
            this.propertyDidChange('uuid');
            sc_super();
        }
    }.observes('value'),

    // Override to reset the form on click
    // This helps with erroneous uploads when the user
    // tries to upload the same file again
    input: SC.FileInputView.extend({
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        accept: SC.outlet('parentView.accept'),
        name: SC.outlet('parentView.inputName'),
        mouseUp: function (evt) {
            this.reset();
            if (!this.get('isEnabled')) return YES;
            evt.allowDefault();
            this.set('isActive', NO);
            return YES;
        }
    })
});
