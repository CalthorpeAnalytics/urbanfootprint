/*-------------------------------------------------------------------------------------------------
 - Project:   sproutcore-upload                                                                   -
 - Copyright: ©2013 Matygo Educational Incorporated operating as Learndot                         -
 - Author:    Joe Gaudet (joe@learndot.com) and contributors (see contributors.txt)               -
 - License:   Licensed under MIT license (see license.js)                                         -
 -------------------------------------------------------------------------------------------------*/

describe("SC.UploadForm", function () {

    var uploadForm;

    beforeEach(function () {
        var pane;
        inRunLoop(function () {
            pane = SC.MainPane.create({
                childViews: ['uploadForm'],
                uploadForm: SC.UploadFormView.extend({
                    name: randomString(10),
                    method: randomString(10),
                    url: randomString(10),
                    uuid: randomString(10),
                    target: randomString(10),
                    enctype: randomString(10)
                })
            });

            pane.append();
            uploadForm = pane.uploadForm;
        }, this);
    });

    it("Should bind all of the appropriate attributes to the view layer", function () {
        var viewLayer = uploadForm.$();
        expect(viewLayer.attr('name')).toBe(uploadForm.get('name'));
        expect(viewLayer.attr('method')).toBe(uploadForm.get('method'));
        expect(viewLayer.attr('action')).toBe("%@?X-Progress-ID=%@".fmt(uploadForm.get('url'), uploadForm.get('uuid')));
        expect(viewLayer.attr('target')).toBe(uploadForm.get('target'));
        expect(viewLayer.attr('enctype')).toBe(uploadForm.get('enctype'));
    });

});
