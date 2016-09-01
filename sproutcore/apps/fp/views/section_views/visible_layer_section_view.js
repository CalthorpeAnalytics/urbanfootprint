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

sc_require('views/info_views/views_list_view.js');
sc_require('views/info_views/views_item_content.js');
sc_require('views/info_views/layer/edit_style_value_context_view');
sc_require('views/info_views/record_item_with_style_view');

Footprint.VisibleLayerSectionView = SC.View.extend({
    classNames: ['footprint-visible-layer-section', 'footprint-map-overlay-section'],
    childViews: ['reorderBackgroundLayersView', 'reorderForegroundLayersView'],
    reorderBackgroundLayersView: SC.View.extend({
        layout: { height: .35 },
        childViews: ['reorderLabelView', 'reorderListView'],
        reorderLabelView: SC.LabelView.extend({
            layout: { top: 5, height: 20, left: 5 },
            classNames: ['footprint-header'],
            value: 'Reorder Basemaps'
        }),
        reorderListView: SC.ScrollView.extend({
            layout: { top: 30, bottom: 5, left: 5, right: 5 },
            backgroundColor: 'grey',
            contentView: SC.SourceListView.extend({
                backgroundColor: 'lightgrey',
                showAlternatingRows : YES,
                contentBinding: SC.Binding.oneWay('Footprint.layersVisibleBaseMapController.arrangedObjects'),
                contentValueKey: 'name',
                canReorderContent: YES
            })
        })
    }),
    reorderForegroundLayersView: SC.View.extend({
        layout: { top: .35 },
        childViews: ['reorderLabelView', 'reorderListView'],

        reorderLabelView: SC.LabelView.extend({
            layout: { top: 5, height: 20, left: 5 },
            classNames: ['footprint-header'],
            value: 'Reorder Layers'
        }),
        reorderListView: SC.ScrollView.extend({
            layout: { top: 30, bottom: 5, left: 5, right: 5 },
            backgroundColor: 'grey',
            contentView: SC.SourceListView.extend({
                backgroundColor: 'lightgrey',
                showAlternatingRows : YES,
                contentBinding: SC.Binding.oneWay('Footprint.layersVisibleForegroundController.arrangedObjects'),
                contentValueKey: 'name',
                canReorderContent: YES
            })
        })
    })
});
