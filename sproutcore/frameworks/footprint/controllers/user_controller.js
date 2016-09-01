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
// Project:   Footprint.userController
// ==========================================================================
/*globals Footprint */

/***
 * User controller expects a single item list or single Footprint.User record set to its content property
 * @extends {SC.ArrayController}
 */
Footprint.userController = SC.ArrayController.create({
    setCookie: function(duration) {
        var cookie = this.findCookie() ||
            SC.Cookie.create({
            name: 'user.api_key',
            value: Footprint.userController.getPath('firstObject.api_key')
        });
        if (duration) {
            var d = new Date();
            d.setTime(d.getTime() + duration);
            cookie.expires = d;
        }
        else
            cookie.expires = null;
        cookie.write();
    },
    destroyCookie: function() {
        var cookie = this.findCookie();
        if (cookie) {
            cookie.destroy();
        }

        var djangoCookie = SC.Cookie.find('sessionid');
        if (djangoCookie) {
            djangoCookie.destroy();
        }
    },
    findCookie: function() {
        return SC.Cookie.find('user.api_key');
    }
});
