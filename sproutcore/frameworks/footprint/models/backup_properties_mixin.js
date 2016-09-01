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


Footprint.BackupProperties = {
    /**
     * Return an object containing a backup of the properties
     * @returns SC.Object object containing properties to backup
     */
    backupProperties: function() {
        var backup = SC.Object.create();
        for (var i = 0; i < this.properties.length; i++) {
            var p = this.properties[i];
            backup.set(p, this.get(p));
        }
        return backup;
    },

    /**
     * Restores properties from a backup crated by backupProperties().
     */
    restoreProperties: function(backup) {
        for (var i = 0; i < this.properties.length; i++) {
            var p = this.properties[i];
            this.set(p, backup.get(p));
        }
        return;
    }
}
