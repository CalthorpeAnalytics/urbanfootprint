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


sc_require('views/info_views/medium_info_view');
sc_require('views/info_views/key_info_view');

/***
 * Edits the style data stored in a PresentationMedium.medium or similar
 * Set the content to to
 * A SelectView is populated via the items property to provide a way to copy values from an existing style.
 * The items must be the same type as the content.
 * @type {*}
 */
Footprint.StyleInfoView = Footprint.SelectUpdateInfoView.extend({
    classNames: "footprint-style-info-view".w(),
    title: 'Style',

    contentView:Footprint.InfoView.extend({
        layout: {left: .2, width: .8},
        contentBinding: SC.Binding.oneWay(parentViewPath(1,'*content'))
    })
});
