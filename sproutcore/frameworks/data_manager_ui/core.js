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

// ==========================================================================
// Project:   QueryUI
// ==========================================================================
/*globals QueryUI, Footprint, DataManagerUI */


/** @namespace

  This object acts as a controller backing the data manager UI components. It could be refactored into
  substate(s) when combined into the real project.

  @extends SC.Object
*/
DataManagerUI = SC.Object.create(
    /** @scope DataManagerUI.prototype */ {

    // TODO: Where should this come from? It's a bit odd to have to set it on a controller.
        store: null
    });

DataManagerUI.views = SC.Page.create({

});
