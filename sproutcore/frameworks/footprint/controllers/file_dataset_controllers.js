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
// Project:   Footprint.fileSourcesController
// ==========================================================================
sc_require('models/file_source_model');

/** @class
 A list of Footprint.FileDataset records
 A FileDataset represents one of the datasets of a FileDataset
 @extends SC.ObjectController
 */
Footprint.fileDatasetsController = SC.ArrayController.create({
    allowsEmptySelection: NO,
    orderBy: ['id DESC']
});
