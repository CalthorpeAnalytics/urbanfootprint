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


sc_require('views/info_views/key_info_view');

Footprint.MediumInfoView = Footprint.SelectUpdateInfoView.extend({
    classNames:'footprint-medium-info-view'.w(),
    childViews:'titleView contentView selectView'.w(),
    title: 'Medium',
    contentView:Footprint.NameInfoView.extend({
        layout: {left: .2, width: .8},
        contentBinding: SC.Binding.oneWay(parentViewPath(1,'*content.medium')),
        itemsBinding: SC.Binding.oneWay(parentViewPath(1,'*items'))
    })
});

/**
 * Edits Medium instances who define one or more CSS-style colors
 * @type {SC.RangeObserver}
 */
Footprint.MediumColorsInfoView = Footprint.MediumInfoView.extend({
    contentView:Footprint.NameInfoView.extend({
        layout: {left: .2, width: .8},
        // The instance can't be changed in the controller
        contentBinding: SC.Binding.oneWay(parentViewPath(2,'*content.medium')),
        itemsBinding: SC.Binding.oneWay(parentViewPath(1,'*items'))
    })
});
