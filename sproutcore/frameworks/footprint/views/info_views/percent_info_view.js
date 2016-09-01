
 /* 
* UrbanFootprint-California (v1.0), Land Use Scenario Development and Modeling System.
* 
* Copyright (C) 2014 Calthorpe Analytics
* 
* This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3 of the License.
* 
* This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
* 
* You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
* 
* Contact: Joe DiStefano (joed@calthorpe.com), Calthorpe Analytics. Firm contact: 2095 Rose Street Suite 201, Berkeley CA 94709. Phone: (510) 548-6800. Web: www.calthorpe.com
*/
sc_require('views/info_views/editable_field_button_view');

/***
 * Allows showing an editing a percent
*/
Footprint.PercentInfoView = SC.View.extend({
    childViews: ['titleView', 'symbolView', 'inputView'],
    classNames: ['percent-info-view'],
    valueSymbol: '%',
    title: 'Title',
    value:null,
    displayValue: null,
    titleLayout: null,
    inputLayout: null,
    symbolLayout: null,
    valueLayout: {left: 5, height: 20, right:14},
    buttonsLayout: {height: 20, width: 14, right:0},

    titleView: SC.LabelView.design({
        classNames: ['percent-item-title'],
        layoutBinding: SC.Binding.from('.parentView.titleLayout'),
        localize: true,
        textAlign: SC.ALIGN_LEFT,
        valueBinding: SC.Binding.oneWay('.parentView.title')
    }),

    symbolView: SC.LabelView.design({
        classNames: ['percent-item-symbol-label'],
        layoutBinding: SC.Binding.from('.parentView.symbolLayout'),
        valueBinding: SC.Binding.from('.parentView.valueSymbol')
    }),

    inputView: Footprint.EditableFieldButtonView.extend({
        classNames: ['percent-item-value-label', 'footprint-editable-content-11px-view'],
        layoutBinding: SC.Binding.from('.parentView.inputLayout'),
        valueLayoutBinding: SC.Binding.oneWay('.parentView.valueLayout'),
        buttonsLayoutBinding: SC.Binding.oneWay('.parentView.buttonsLayout'),
        textAlign: SC.ALIGN_CENTER,
        valueBinding: SC.Binding.from('.parentView.value'),
        valueStep: 1,
        minimum: 0,
        maximum: 100,
        validator: function() {
            return SC.Validator.Number.create({places:1});
        }.property().cacheable()
    }),
})