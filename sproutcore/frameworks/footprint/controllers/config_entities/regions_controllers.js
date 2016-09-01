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


sc_require('controllers/controllers');
sc_require('resources/config_entity_delegator');
sc_require('controllers/config_entities/global_config_controllers');
sc_require('controllers/config_entities/global_config_controllers');

/***
 * regionsController organizes the regions as a simple list for region selection and add/remove.
 * We only include regions that do not have regions as children
 * @type {*}
 */
Footprint.regionsController = Footprint.ArrayController.create(Footprint.ArrayContentSupport, {
    globalConfig: null,
    globalConfigBinding: SC.Binding.oneWay('Footprint.globalConfigActiveController.content'),

    /***
     * All loaded regions
     */
    allRegions: function() {
        var globalConfig = this.get('globalConfig');
        return globalConfig ? globalConfig.get('store').find(Footprint.Region) : [];
    }.property('globalConfig').cacheable(),

    /***
     * Content is Regions that have Projects for children
     */
    content: function() {
        var regions = this.get('allRegions');
        return (regions || []).filter(function(region) {
            return !region.getPath('children.length') ||
                region.getPath('children.firstObject').instanceOf(Footprint.Project);
        });
    }.property().cacheable()
});

/***
 * regionActiveController keeps track of the active Region
 * @type {*}
 */
Footprint.regionActiveController = Footprint.ActiveController.create(Footprint.ConfigEntityDelegator, {
    listController: Footprint.regionsController,
    // TODO: Work out a way to structure this less hackily.
    clientPath: function() {
        if (this.getPath('content.client'))
            var clientKey = this.getPath('content.client').toLowerCase();
            if (!clientKey) return null;
            return window['Footprint%@'.fmt(clientKey.camelize().capitalize())];
    }.property('content').cacheable()
});

/***
 * A separate controller from the regionActiveController so that a region can be added or edited without necessarily being the region in context for the rest of the application
 * @type {*}
 */
Footprint.regionEditController = SC.ObjectController.create({
    // Used to create new instances
    recordType: Footprint.Region,
    // The bound object controller, which interacts with its content record directly, rather than via a nested store
    objectControllerBinding:SC.Binding.oneWay('Footprint.regionActiveController')
});
