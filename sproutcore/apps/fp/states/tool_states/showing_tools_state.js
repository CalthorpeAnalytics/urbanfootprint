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
 * The state that manages the projects pane at the top of the application
 * @type {Class}
 */
Footprint.ShowingToolsState = SC.State.design({
    /***
     * Sets the topSectionVisibleViewController based on the active topSection
     * @param context
     */
    doOpenTopSection: function(context) {
        Footprint.topSectionVisibleViewController.setIfChanged('topSectionIsVisible', YES);
        Footprint.topSectionVisibleViewController.setIfChanged('content', context.getPath('selectedItem.value'));
        Footprint.topSectionVisibleViewController.setIfChanged('view', context.getPath('selectedItem.view'));
    },
});
