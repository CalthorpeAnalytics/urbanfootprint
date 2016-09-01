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



Footprint.LoadingPane = SC.MainPane.extend({
    childViews: 'loadingView clientLogoView progressView'.w(),
    classNames: ['loading-pane'],
    alternateLoad: function() {
        return Math.random() > 0.99;
    }.property().cacheable(),

    loadingView: SC.ImageView.extend({
        classNames:'loading-image'.w(),
        useCanvas:NO,
        layout: {centerX: 0, centerY:-150, width:300, height:300},
        value: sc_static('images/loading.png')
    }),
    clientLogoView: Footprint.ClientImageView.extend({
        classNames:'client-logo-image'.w(),
        layout: {centerX: 0, centerY:120, width:500, height:149},
        clientBinding: SC.Binding.oneWay('Footprint.regionActiveController*content.client'),
        clientPathBinding: SC.Binding.oneWay('Footprint.regionActiveController.clientPath'),
        imagePath: 'model_loading_logo.png'
    }),
    progressView: SC.ProgressView.extend({
        layout: {centerX:.0001, centerY:0, width:.2, height:16, top:0.9},
        valueBinding:SC.Binding.oneWay('Footprint.loadingStatusController.content'),
        minimum:0,
        maximum:10
    })
});
