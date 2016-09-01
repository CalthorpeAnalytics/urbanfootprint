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


Footprint.ExamplesView = SC.View.extend({
    layout: { left: 0.01, right: 0.7, top: 0.30, bottom: 0.05 },
    childViews: 'headerView imagesView noExamplesListView examplesListView'.w(),

    headerView: SC.LabelView.design({
        layout: { width: 150, height: 50 },
        classNames: ['sectionTitle'],
        tagName: "h1",
        value: "Examples"
    }),
    imagesView: SC.View.design({
        layout: { top: 0.05, bottom: 0.4 },
        childViews: 'bigImageView thumbnailsView'.w(),
        bigImageView: SC.View.design({
            layout : { right: 0.20 },
            childViews: 'bigImageImageView'.w(),
            displayProperties: ['content'],

            content:null,
            contentBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormMediaController*selection.firstObject.url'),

            bigImageImageView: SC.ImageView.extend({
                layout: { bottom: 0.10 },
                classNames: ['bigImage'],

                displayProperties: ['content'],
                content:null,
                contentBinding: SC.Binding.oneWay('.parentView*content'),

                value: function() {
                    return Footprint.STATIC.fmt(this.get('content'))
                }.property('content').cacheable()

            })
        }),
        thumbnailsView: SC.ScrollView.design({
            layout: { left: 0.80, bottom: 0.10},

            isVisibleBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormActiveController*content.media').bool(),
            contentView: SC.SourceListView.extend({
                rowHeight: 45,

                contentBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormActiveController*content.media'),

                selectionBinding: SC.Binding.from('Footprint.urbanBuiltFormMediaController.selection'),
                exampleView: SC.View.extend(SC.Control, {
                    layout: { height: 40 },
                    childViews: 'imageView'.w(),
                    contentValueKey: 'title',
                    imageView: SC.ImageView.extend({
                        layout: { left: 5, height: 40, width: 40 },
                        displayProperties: ['content'],

                        content:null,
                        contentBinding: SC.Binding.oneWay('.parentView*content.url'),

                        value: function() {
                            return Footprint.STATIC.fmt(this.get('content'))
                        }.property('content').cacheable()

                    })
                })
            })
        })
    }),
    noExamplesListView: SC.LabelView.design({
        layout: { top: 0.6, bottom: 0, width: 250, height: 20},
        value: "No examples to display",

        isVisibleBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormActiveController*content.examples').bool().not()

    }),
    examplesListView: SC.ScrollView.design({
        layout: { top: 0.6, bottom: 0},

        isVisibleBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormActiveController*content.examples').bool(),
        contentView: SC.SourceListView.extend({
            classNames: 'examplesList'.w(),
            rowHeight: 40,

            contentBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormActiveController*content.examples'),

            exampleView: SC.View.extend(SC.Control, {
                layout: { height: 50 },
                childViews: 'nameView url1View url2View'.w(),

                contentValueKey: 'title',
                nameView: SC.LabelView.extend({
                    layout: { left: 10, width: 300, height: 15},

                    content: null,
                    contentBinding: SC.Binding.oneWay('.parentView*content'),
                    valueBinding: SC.Binding.oneWay('.parentView*content.name')

                }),
                url1View: SC.LabelView.extend({
                    layout: { left: 10, top: 18, width: 150, height: 15},

                    content: null,
                    contentBinding: SC.Binding.oneWay('.parentView*content'),
                    value: function() {
                        var url = this.getPath('parentView*content.url_aerial');
                        return "<a href='http://" + url + "'>Street View</a>"

                    }.property('content').cacheable(),
                    escapeHTML: NO

                }),
                url2View: SC.LabelView.extend( {
                    layout: { left: 150, top: 18, width: 100, height: 15 },

                    content: null,
                    contentBinding: SC.Binding.oneWay('.parentView*content.url_street'),
                    value: function() {
                        var url = this.get('content');
                        return "<a href='http://" + url + "'>Street View</a>"
                    }.property('content').cacheable(),
                    escapeHTML: NO

                })
            })
        })
    })
});
