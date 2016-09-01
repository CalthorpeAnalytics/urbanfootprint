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
 * Adds universal functionality to SC.PanelPane
 */
Footprint.PanelPane = SC.PanelPane.extend({
    /***
     * Responds to the escape key with by attempting to close the pane with a prompt
     * @param evt
     * @returns {boolean}
     */
    keyUp: function(evt) {
        if (evt.keyCode === SC.Event.KEY_ESCAPE) {
            Footprint.statechart.sendAction('doPromptCancel');
            return YES;
        }
    },
});
