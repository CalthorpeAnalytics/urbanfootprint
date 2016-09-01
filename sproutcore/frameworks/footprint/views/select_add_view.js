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



sc_require('views/label_select_view');
sc_require('views/section_toolbars/edit_button_view');
sc_require('views/info_views/name_info_view');

/***
 * Extends Footprint.SelectView to add the ability to add/edit an item inline
 * @type {SC.RangeObserver}
 */
Footprint.SelectAddView = SC.View.extend({

    classNames: "footprint-select-add-view".w(),
    childViews:'selectView addButtonView'.w(),
    itemTitleKey: null,
    showCheckbox: YES,
    items:null,
    values:null,
    value:null,
    showAddView: YES,
    emptyName:null,

    /**
     * The Record type being selected, edited or added
     */
    recordType:null,

    selectView: Footprint.LabelSelectView.extend({
        layout:{left:0, width:.5},
        emptyNameBinding: parentViewPath(1,'*emptyName'),

        itemTitleKeyBinding: parentViewPath(1, '.itemTitleKey'),
        showCheckboxBinding: parentViewPath(1, '.showCheckbox'),
        itemsBinding: parentViewPath(1, '.items'),
        valuesBinding: parentViewPath(1, '.values'),
        valueBinding: parentViewPath(1, '.value')
    }),

    addButtonView: Footprint.AddButtonView.extend({
        controlSize: SC.SMALL_CONTROL_SIZE,
        layout:{left:.5, width:.2, centerY:0.001, height:.5},
        recordTypeBinding: parentViewPath(1, '.recordType'),
        action: 'cloneSelected'
    }),

    toString: function() {
        return "%@:\n%@".fmt(sc_super(), this.toStringAttributes('recordType itemTitleKey items values value'.w()));
    }
});
