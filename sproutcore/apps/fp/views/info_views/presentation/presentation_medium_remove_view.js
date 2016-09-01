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
 * The pane used to edit the settings of a new or existing PresentationMedium and the DbEntity to which it is associated (if any). The saving order of this will have to first save a created DbEntity and then the PresentationMedium if a DbEntity is being created here
 * @type {*}
 */
Footprint.PresentationMediumRemoveView = SC.PickerPane.extend({
    classNames:'footprint-presentation-medium-remove-view'.w(),
    layout:{width:200, height:200},
    // Use Browser positioning
    useStaticLayout:YES,
    contentView: SC.View.extend({
        childViews:['nameView', 'deleteView'],
        nameView: Footprint.EditableModelStringView.extend({
            classNames: ['footprint-editable-content-view'],
            valueBinding: 'Footprint.presentationMediumEditController.db_entity.name'
        }),
        // The query for the DbEntity if relevant (if the DbEntity represents a query or a database view)
        deleteView: Footprint.EditableModelStringView.extend({
            classNames: ['footprint-editable-content-view'],

        })
    })
});
