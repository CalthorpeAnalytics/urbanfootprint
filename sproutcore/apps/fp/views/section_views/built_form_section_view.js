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


sc_require('views/info_views/record_item_with_style_view');
sc_require('views/info_views/built_form/built_form_scroll_view');

Footprint.BuiltFormSectionView = SC.View.extend({
    childViews: 'toolbarView listView overlayView'.w(),
    classNames: "footprint-built-form-section-view".w(),
    builtForms: null,
    builtFormSetContent: null,
    builtFormSetSelection: null,
    builtFormSetStatus: null,
    builtFormContent: null,
    builtFormSelection: null,
    selection: null,
    activeBuiltForm: null,
    toolBarVisible: null,

    menuItems: null,

    toolbarView: Footprint.LabelSelectToolbarView.extend({
        classNames: "footprint-built_form-toolbar-view".w(),
        titleViewLayout: {height: 24},
        controlSize: SC.REGULAR_CONTROL_SIZE,
        icon: sc_static('images/section_toolbars/pulldown.png'),

        contentBinding: '.parentView.builtFormSetContent',
        isVisibleBinding: SC.Binding.oneWay('.parentView.builtFormSetStatus').matchesStatus(SC.Record.READY),
        selectionBinding: '.parentView.builtFormSetSelection',
        recordType: Footprint.BuiltForm,
        activeRecordBinding: SC.Binding.oneWay('.parentView.activeBuiltForm'),

        title: null,
        itemTitleKey: 'name',

        menuItemsBinding: SC.Binding.oneWay('.parentView.menuItems')
    }),

    overlayView: Footprint.OverlayView.extend({
        layout: { top: 24 },
        contentBinding: SC.Binding.oneWay('.parentView.builtForms'),
        statusBinding:SC.Binding.oneWay('*content.status')
    }),

    listView: Footprint.BuiltFormScrollView.extend({
        layout: {top: 24},
        contentBinding: SC.Binding.oneWay('.parentView.builtFormContent'),
        selectionBinding: SC.Binding.from('.parentView.builtFormSelection')
    })
});
