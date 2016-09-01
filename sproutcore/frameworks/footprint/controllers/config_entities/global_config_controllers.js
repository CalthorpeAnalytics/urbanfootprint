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

sc_require('controllers/active_controller');
/***
 * globalConfigController binds holds the singleton global config as an array in its content to conform with the other
 * ConfigEntity controllers
 * @type {*}
 */
Footprint.globalConfigController = SC.ArrayController.create({
    // Ensures that Footprint.globalConfigActiveController
    allowsEmptySelection: NO
});

/***
 * References the globalConfig singleton in its content
 * @type {*|void}
 */
Footprint.globalConfigActiveController = Footprint.ActiveController.create({
    listController:Footprint.globalConfigController
});
