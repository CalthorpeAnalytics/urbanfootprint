/*-------------------------------------------------------------------------------------------------
 - Project:   sproutcore-upload                                                                   -
 - Copyright: ©2013 Matygo Educational Incorporated operating as Learndot                         -
 - Author:    Joe Gaudet (joe@learndot.com) and contributors (see contributors.txt)               -
 - License:   Licensed under MIT license (see license.js)                                         -
 -------------------------------------------------------------------------------------------------*/

describe("SC.ImageUploadView", function () {

    var imageUploadView;

    beforeEach(function () {
        var pane;
        inRunLoop(function () {
            pane = SC.MainPane.create({
                childViews: ['iframeView'],
                imageUploadView: SC.ImageUploadView.extend()
            });

            pane.append();
            imageUploadView = pane.imageUploadView;
        }, this);
    });

});