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

sc_require('views/info_views/select_attribute_info_views');
sc_require('views/info_views/label_select_info_view');


/***
 * The user picks a join type here. If the join type
 * is attribute, then the user needs to specify the source id and target id
 * in the extra drop downs. If it's a geographic join they specify the geographic types in dropdowns
 */
DataManagerUI.views.JoinView = Footprint.LabelSelectInfoView.extend({
    childViews:['nameTitleView', 'labelSelectView', 'fromGeographicTypeView', 'fromAttributeView', 'toGeographicTypeView', 'toAttributeView'],
    layout: { top: 0, height: 44},
    // The layout of the join type button and also the from/to buttons below
    buttonLayout: {top: 20, height: 24, width: 80},

    classNames:['join-view'],
    title: 'DMUI.JoinType',
    // Simply strings 'geographic' or 'attribute' representing joinType options
    toolTip: 'polygon to polygon: Primary UF Geography polygons intersect new layer polygons \n \n' +
    ' polygon to centroid: Primary UF Geography polygons intersect new layer centroids \n \n' +
    ' centroid to polygon: Primary UF Geography centroids intersect new layer polygons \n \n' +
    ' attribute: Primary UF Geography primary key joins on new layer primary key',
    menuWidth: 80,

    // The type of intersection of the Primary Geography DbEntity, not this DbEntity
    // This view is only visible for geographic joins
    fromGeographicTypeView: Footprint.JoinColumnsInfoView.extend({
        layout: {top: 0, left: 90, width: 80},
        buttonLayoutBinding: SC.Binding.oneWay('.parentView.buttonLayout'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.selectedItem').valueEquals('geographic'),
        classNames:['from-type-view'],
        title: 'DMUI.JoinFromType',
        menuWidth: 80,

        contentBinding: SC.Binding.oneWay('Footprint.primaryDbEntityGeographicIntersectionEditController.content'),
        selectionBinding: 'Footprint.primaryDbEntityGeographicIntersectionEditController.selection',
        // We don't want to take any action. JoinColumnsInfoView is designed for updating the LayerSelection
        selectionAction: null
    }),

    // The attribute of the Primary Geography DbEntity, not this DbEntity
    // This view is only visible for attribute joins
    fromAttributeView: Footprint.JoinColumnsInfoView.extend(Footprint.AttributeJoinColumnsViewMixin, {
        layout: {top: 0, left: 90, width: 80},
        buttonLayoutBinding: SC.Binding.oneWay('.parentView.buttonLayout'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.selectedItem').valueEquals('attribute'),
        classNames:['from-attribute-view'],
        title: 'DMUI.JoinFromAttribute',
        menuWidth: 200,

        contentBinding: SC.Binding.oneWay('Footprint.primaryDbEntityAttributeIntersectionEditController.content'),
        status: null, // Override computed status
        statusBinding: SC.Binding.oneWay('Footprint.primaryDbEntityAttributeIntersectionEditController.status'),
        selectionBinding: 'Footprint.primaryDbEntityAttributeIntersectionEditController.selection',
        // We don't want to take any action. JoinColumnsInfoView is designed for updating the LayerSelection
        selectionAction: null
    }),

    // The type of intersection of this DbEntity
    // This view is only visible for geographic joins
    toGeographicTypeView: Footprint.JoinColumnsInfoView.extend({
        layout: {top: 0, left: 180, width: 80},
        buttonLayoutBinding: SC.Binding.oneWay('.parentView.buttonLayout'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.selectedItem').valueEquals('geographic'),
        classNames:['to-type-view'],
        title: 'DMUI.JoinToType',
        menuWidth: 80,

        contentBinding: SC.Binding.oneWay('Footprint.targetDbEntityGeographicIntersectionEditController.content'),
        selectionBinding: 'Footprint.targetDbEntityGeographicIntersectionEditController.selection',
        // We don't want to take any action. JoinColumnsInfoView is designed for updating the LayerSelection
        selectionAction: null
    }),

    // The attribute of this DbEntity that shall join to that of the
    // primary Geography DbEntity specified above
    // This view is only visible for attribute joins
    toAttributeView: Footprint.SelectAttributeInfoView.extend({
        layout: {top: 0, left: 180, width: 80},
        isVisibleBinding: SC.Binding.oneWay('.parentView.selectedItem').valueEquals('attribute'),
        classNames:['to-attribute-view'],
        title: 'DMUI.JoinToAttribute',
        menuWidth: 200,

        contentBinding: SC.Binding.oneWay('Footprint.targetDbEntityJoinAttributeIntersectionEditController.content'),
        statusBinding: SC.Binding.oneWay('Footprint.targetDbEntityJoinAttributeIntersectionEditController.status'),
        selectionBinding: 'Footprint.targetDbEntityJoinAttributeIntersectionEditController.selection',
        // We don't want to take any action. JoinColumnsInfoView is designed for updating the LayerSelection
        selectionAction: null
    })

});
