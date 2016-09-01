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



SC.State.reopen({
    /***
     * Overwrite gotoState to throw a real error if the state is not found, instead of just logging an error.
     * We want to be intolerant of missing states.
     * @param value
     * @param context
     */
    gotoState: function(value, context) {
        var state = this.getState(value);

        if (!state) {
            var msg = "can not go to state %@ from state %@. Invalid value.";
            this.stateLogError(msg.fmt(value, this));
            throw Error(msg.fmt(value));
        }

        var from = this.findFirstRelativeCurrentState(state);
        this.get('statechart').gotoState(state, from, false, context);
    }
});
