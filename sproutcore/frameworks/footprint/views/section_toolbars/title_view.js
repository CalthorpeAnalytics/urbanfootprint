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



Footprint.TitleView = SC.ToolbarView.extend({
     classNames: "footprint-title-view".w(),
     childViews:'labelView'.w(),
     anchorLocation: SC.ANCHOR_TOP,
     labelViewLayout: {left:0, right:0},

     title:null,
     content:null,
     contentNameProperty:null,

     labelView: SC.LabelView.extend({
         layoutBinding:SC.Binding.oneWay('.parentView.labelViewLayout'),
         content:null,
         contentBinding:SC.Binding.oneWay('.parentView.content'),

         contentStatus:null,
         contentStatusBinding:SC.Binding.oneWay('*content.status'),
         contentNameProperty:'name',
         contentNamePropertyBinding:SC.Binding.oneWay('.parentView.contentNameProperty').transform(function(name) {
            return name || 'name';
         }),

         title:null,
         titleBinding:SC.Binding.oneWay('.parentView.title'),

         fullLabel:function() {
             if (this.get('contentStatus') & SC.Record.READY) {
                 var subtitle = this.getPath('content.%@'.fmt(this.get('contentNameProperty')));
                 if (subtitle)
                     return '%@ for %@'.fmt(this.get('title'), subtitle);
             }
             return 'Loading';
         }.property('content', 'contentStatus', 'title', 'contentNameProperty').cacheable(),
         value: null,
         valueBinding: SC.Binding.oneWay('.fullLabel')
     })
 });
