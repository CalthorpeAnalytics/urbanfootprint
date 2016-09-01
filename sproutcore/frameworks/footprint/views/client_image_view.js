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


Footprint.ClientImageView = SC.ImageView.extend({
    classNames:'client-image'.w(),
    imagePath: null,
    useCanvas:NO,
    client: null,
    clientPath: null,
    value: function () {
        var client = this.get('client');
        var client_path = this.get('clientPath');
        if (client && client_path) {
            var image_path = 'images/%@_%@'.fmt(client, this.get('imagePath')).toLowerCase();
            return client_path.STATIC.fmt(image_path);
        }
    }.property('client', 'clientPath', 'imagePath').cacheable()
});
