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
 * The pane used to export PresentationMedia that are a combination of a DbEntity and a medium (such as a style)
 * @type {*}
 */
Footprint.PresentationMediumExportView = SC.PickerPane.extend({
    classNames:'footprint-presentation-medium-export-view'.w(),
    contentView: SC.View.extend({
        childViews:['saveDialog'],

        // TODO Save dialog with export type and output location
        saveDialog: SC.View.extend()
    })
});
