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


Footprint.ToggleButtonInfoView = Footprint.InfoView.extend({
    classNames: "footprint-toggle-button-info-view".w(),
    titleViewLayout: {height: 24, right: 26},
    checkBoxLayout: {right: 0, width: 24},
    contentValueKey: null,
    content: null,
    action: null,

    contentView: SC.CheckboxView.extend({
        classNames: ['footprint-toggle-button-view'],
        layoutBinding: SC.Binding.oneWay('.parentView.checkBoxLayout'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        toolTipBinding: SC.Binding.oneWay('.parentView.toolTip'),
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.contentValueKey'),
        actionBinding: SC.Binding.oneWay('.parentView.action')
    })
});

Footprint.SelectAllToggleButtonInfoView = Footprint.ToggleButtonInfoView.extend({
    classNames:'footprint-select-all-view'.w(),
    titleViewLayout: {height: 24, right: 26},
    checkBoxLayout: {right: 0, width: 24},
    title: 'Select All',
    toolTip: 'Select All'
});
