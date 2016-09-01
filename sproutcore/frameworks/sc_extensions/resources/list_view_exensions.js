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

__author__ = 'calthorpe_analytics'

/***
 * Addresses a bug where row height cache is set before any content is loaded
 * for views that are part of a contentView
 */
SC.ListView.reopen({
    /***
     * Observers the content length and  invalidates rowSize if it changes
     */
    contentSizeObserver: function() {
        if (this.getPath('length')) {
            var indexes = SC.IndexSet.create(0, this.get('length'));
            this.rowSizeDidChangeForIndexes(indexes);
        }
    }.observes('length')
});
