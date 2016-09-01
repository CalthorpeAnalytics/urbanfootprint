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

/***
 * The pane used to edit the settings of a create or existing BuiltFormSet and the DbEntity to which it is associated (if any). The saving order of this will have to first save a created DbEntity and then the BuiltFormSet if a DbEntity is being created here
 * @type {*}
 */
Footprint.BuiltFormSetInfoView = Footprint.InfoPane.extend({
    layout: { top:0, left: 0, width:400, height:400 },
    classNames: "footprint-built-form-set-info-view".w(),

    recordType: Footprint.BuiltFormSet,

    contentView: Footprint.InfoView.extend({
        // TODO look at git history and redo this
    })
});
