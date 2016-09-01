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
 * Called by applications to setup the default Footprint theme
 */
Footprint.setupTheme = function() {
    Footprint.Theme = SC.AceTheme.create({
        name: 'footprint'
    });

    // SproutCore needs to know that your app's theme exists
    SC.Theme.addTheme(Footprint.Theme);

    // Setting it as the default theme makes every pane SproutCore
    // creates default to this theme unless otherwise specified.
    SC.defaultTheme = 'footprint';

    var ellipsesLabelRenderDelegate = Footprint.Theme.labelRenderDelegate.extend({
        needsEllipsis: YES
    });
    Footprint.Theme.ellipsesLabelRenderDelegate = ellipsesLabelRenderDelegate;
    Footprint.Theme.themes['source-list'].ellipsesLabelRenderDelegate = ellipsesLabelRenderDelegate;
};
