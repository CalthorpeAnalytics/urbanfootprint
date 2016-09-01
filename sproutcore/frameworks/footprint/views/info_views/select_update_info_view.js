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



/*
 * Base class for editing a model object which adds the ability to select the assigned object from a list
 */

Footprint.SelectUpdateInfoView = Footprint.InfoView.extend({

    classNames: "footprint-update-info-view".w(),
    childViews:'titleView contentView'.w(),
    // Bind this to propagate items to the selectView
    items:null,
    // Bind this to propagate the objectPath to the selectView
    objectPath:null
});
