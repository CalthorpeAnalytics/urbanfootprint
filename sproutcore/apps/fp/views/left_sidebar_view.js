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

/**
 * Contains the layer list, UF partner credits, and the UF copyright
 */
sc_require('views/section_views/layer_section_view');

Footprint.LeftSidebarView = SC.View.extend({
    classNames: ['footprint-sidebar-view'],
    layerId: 'footprint-sidebar-view',

    childViews: ['sidebarViewItself', /* 'partnerListView', */ 'copyrightView'],

    sidebarViewItself: SC.View.extend({
        childViews:['layerSectionView'],
        // TODO this should be dynamic 35 or 235 based on presence of partnerListView
        layout:function() {
            return {
                bottom: this.get('partnerListViewIsVisible') ? this.getPath('partnerListViewLayout.height'): 35
            };
        }.property('partnerListViewIsVisible', 'partnerListViewLayout').cacheable(),
        partnerListViewLayout: null,
        partnerListViewLayoutBinding: SC.Binding.oneWay('.parentView.partnerListView.layout'),
        partnerListViewIsVisible: null,
        partnerListViewIsVisibleBinding: SC.Binding.oneWay('.parentView.partnerListView.isVisible'),

        layerSectionView: Footprint.LayerSectionView.extend({
            layout: { top: 0, bottom: 0 },
            contentBinding: SC.Binding.from('Footprint.layerTreeController.arrangedObjects'),
            selectionBinding: SC.Binding.from('Footprint.layerTreeController.selection'),
            scenarioBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content')
        })
    }),
//    /***
//     * Lists partner organization association with analysis modules
//    */
//
//    partnerListView: SC.SourceListView.extend({
//        layout: {height: 200, bottom: 35},
//        isVisibleBinding: SC.Binding.oneWay('.content').notEmpty(NO),
//        rowHeight: 200,
//        actOnSelect: NO,
//        canReorderContent: NO,
//        showAlternatingRows: YES,
//        allContent: null,
//        allContentBinding: SC.Binding.oneWay('Footprint.analysisModulesController.content'),
//        allContentStatus: null,
//        allContentStatusBinding: SC.Binding.oneWay('Footprint.analysisModulesController.status'),
//        // Only include analysis modules that have partner descriptions
//        content: function() {
//            return (this.get('allContent') || []).filterProperty('partner_description');
//        }.property('allContent', 'allContentStatus').cacheable(),
//
//        exampleView: SC.View.extend({
//            childViews: 'partnerLabelView'.w(),
//            classNames: "footprint-partner-view",
//            partnerImageView: SC.ImageView.extend({
//                layout: {height: 35, left: 0, width: 35},
//                value: sc_static('images/default_logos/uf_thumbnail_35.png')
//            }),
//            partnerLabelView: SC.StaticContentView.extend({
//                classNames: "footprint-partner-label-view",
//                layout: {top: 0, left: 0},
//                contentBinding: SC.Binding.oneWay('.parentView*content.partner_description')
//            })
//        })
//    }),

    copyrightView: SC.View.extend({
        layout: { height: 35, bottom: 0 },
        childViews: 'copyrightImageView copyrightLabelView'.w(),
        classNames: "footprint-copyright-view",
        copyrightImageView: SC.ImageView.extend({
            layout: { height: 35, left: 0, width: 35 },
            value: sc_static('images/default_logos/uf_thumbnail_35.png')
        }),
        copyrightLabelView: SC.LabelView.create({
            classNames: "footprint-copyright-label-view",
            value: 'UrbanFootprint 1.5 rev. yyyy.mm.dd \n © 2016 Calthorpe Analytics', // auto-update-date: yyyy.mm.dd
            toolTip: 'Version yyyy.mm.dd-develop-c854682', // auto-update-rev: yyyy.mm.dd-develop-c854682
            layout: {top: 0.05, left: 40}
        })
    })
});
