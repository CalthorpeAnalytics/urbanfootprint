/*-------------------------------------------------------------------------------------------------
 - Project:   sproutcore-upload                                                                   -
 - Copyright: ©2013 Matygo Educational Incorporated operating as Learndot                         -
 - Author:    Joe Gaudet (joe@learndot.com) and contributors (see contributors.txt)               -
 - License:   Licensed under MIT license (see license.js)                                         -
 -------------------------------------------------------------------------------------------------*/

describe("SC.UploadForm", function () {

    var iframeView;

    beforeEach(function () {
        var pane;
        inRunLoop(function () {
            pane = SC.MainPane.create({
                childViews: ['iframeView'],
                iframeView: SC.IFrameView.extend({
                })
            });

            pane.append();
            iframeView = pane.iframeView;
        }, this);
    });

    it("Should bind all of the appropriate attributes to the view layer", function () {
        var viewLayer = iframeView.$();
        viewLayer.attr('src', 'about:blank');
        viewLayer.attr('border', 0);
        viewLayer.attr('name', SC.guidFor(iframeView));
    });

});
