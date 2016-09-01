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


sc_require('views/info_views/layer/categorical_style_view');
sc_require('views/info_views/layer/quantitative_style_view');
sc_require('views/info_views/layer/single_style_view');

Footprint.LayerStyleRightSideView = SC.View.extend({
    childViews: ['symbologyTypeView', 'attributeSelectView', 'symbologyContainerView'],

    isEnabledBinding: SC.Binding.oneWay('Footprint.styleableAttributesEditController*selection.firstObject.isDefault').not(),
    symbologyTypeView: SC.View.extend({

        childViews: ['titleView', 'selectView'],
        layout: {top: 15, left: 60, width: 120, height: 38},

        titleView: SC.LabelView.extend({
            classNames: ['footprint-10font-title-view'],
            layout: {height: 14},
            value: 'Select Style Type:'
        }),

        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),

        selectView: Footprint.FootprintSelectView.extend({
            layout: {top: 14},
            contentController: Footprint.styleTypeEditController,
            itemTitleKey: 'style_type',

            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),

            selectionObserver: function () {
                //overrides the default selectionObserver in order to update the style value context content based on
                //the style type selection
                if (this.get('selection')) {
                    var selection = this.getPath('selection.firstObject');
                    var menuValue = this.getPath('menu.selectedItem.title');
                    var contentConroller = this.get('contentController');
                    var itemTitleKey = this.get('itemTitleKey');
                    //sometimes when selecting from this button this value is null
                    if (menuValue) {
                        contentConroller.selectObject(this.get('items').find(function(obj) {
                            return obj.get(itemTitleKey)==menuValue;
                        }));
                        //set the styled attribute to null whenever the style type changes
                        //whenever the style type selection changes reset the style value contexts to match
                        //the expected format for a given style type - for single it will clear all previous
                        //style value contexts and add a single default style value context - for categorical and
                        //quantitative it will remove all style value contexts and wait for the user to choose an
                        //attribute and generate the style value contexts from query
                        if (menuValue == 'single') {
                            Footprint.statechart.sendAction('setDefaultSingleStyleType');
                        }
                        else {
                            Footprint.statechart.sendAction('setDefaultNonSingleStyleType');
                        }
                    }
                }
            }.observes('*menu.selectedItem.title')
        })
    }),

    attributeSelectView: SC.View.extend({
        childViews: ['titleView', 'selectView'],
        layout: {top: 15, left: 210, width: 120, height: 38},
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),

        titleView: SC.LabelView.extend({
            classNames: ['footprint-10font-title-view'],
            layout: {height: 14},
            value: 'Select Attribute:'
        }),

        selectView: Footprint.FootprintSelectView.extend({
            layout: {top: 14},
            contentController: Footprint.styleAttributeEditController,
            emptyName: 'None',
            itemTitleKey: 'field',
            isEnabledBinding: SC.Binding.and('Footprint.styleTypeEditController.isNotSingle',
                                             '.parentView.isEnabled'),
            selectionObserver: function () {
                //overrides the default selectionObserver in order to update the style value context content based on
                //the style type selection
                if (this.get('selection')) {
                    var selection = this.getPath('selection.firstObject'),
                    menuValue = this.getPath('menu.selectedItem.title'),
                    contentConroller = this.get('contentController'),
                    itemTitleKey = this.get('itemTitleKey'),
                    //sometimes when selecting from this button this value is null
                    updateContent = selection && selection.get(itemTitleKey) == menuValue ? NO : YES;
                    if (menuValue) {
                        contentConroller.selectObject(this.get('items').find(function(obj) {
                            return obj.get(itemTitleKey)==menuValue;
                        }));
                        //reset the style value contexts to null if the styled attribute changes
                        if (updateContent) {
                            Footprint.statechart.sendAction('setDefaultNonSingleStyleType');
                        }
                    }
                }
            }.observes('*menu.selectedItem.title')
        })
    }),

    symbologyContainerView: SC.ContainerView.extend({
        layout: {left: 20, top: 65, right: 10},
        symbologyType: null,
        symbologyTypeBinding: SC.Binding.oneWay('Footprint.styleTypeEditController*selection.firstObject.style_type'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        nowShowing: function() {
            if (this.getPath('symbologyType')) {
                return 'Footprint.%@StyleView'.fmt(this.get('symbologyType').capitalize());
            }
            return null;
        }.property('symbologyType').cacheable()
    })
});
