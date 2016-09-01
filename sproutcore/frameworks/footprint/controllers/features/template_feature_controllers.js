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
 * Contains the current Template Feature. This is a fake Feature of the DbEntity that gives meta class info
 * It is set whenever the DbEntity changes
 */
Footprint.templateFeaturesController = SC.ArrayController.create({

});
Footprint.templateFeatureActiveController = SC.ObjectController.create({
    contentBinding: SC.Binding.oneWay('Footprint.templateFeaturesController*content.firstObject'),
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.templateFeaturesController.status')
});


/***
 * Stores all Primary DbEntity Template Features. These are the template Features of all the Primary Geography DbEntities
 * of the current Scenario and its parent ConfigEntities. There might be one for the current project and region,
 * for instance. There must be at least one. Primary Geography DbEntities are used to preconfigure joins between
 * DbEntities.
 */
Footprint.primaryDbEntityTemplateFeaturesController = SC.ArrayController.create({
});

/***
 * Contains the TemplateFeatures of newly uploaded FeatureTables.
 * It contains the those of the FeatureTable of one or more uploaded files.
 */
Footprint.newTemplateFeaturesController = SC.ArrayController.create({

});
Footprint.newTemplateFeatureActiveController = SC.ObjectController.create({
    contentBinding: SC.Binding.oneWay('Footprint.templateFeaturesController*content.firstObject'),
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.templateFeaturesController.status')
});

/***
 * Holds the TemplateFeatures of the DbEntities in Footprint.JoinedDbEntitiesController
 */
Footprint.joinedTemplateFeaturesController = SC.ArrayController.create({

});
/***
 * We currenty just expect on joined DbEntity, so this holds its TemplateFeature
 */
Footprint.joinedTemplateFeatureActiveController = SC.ObjectController.create({
    contentBinding: SC.Binding.oneWay('Footprint.joinedTemplateFeaturesController.firstObject').defaultValue(null),
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.joinedTemplateFeaturesController.status')
});

/***
 * Holds the Template feature of the active DbEntity of a query clause, which is always the last one
 */
Footprint.activeQueryTemplateFeaturesController = SC.ArrayController.create({
});
Footprint.activeQueryTemplateFeatureActiveController = SC.ObjectController.create({
    contentBinding: SC.Binding.oneWay('Footprint.activeQueryTemplateFeaturesController.firstObject'),
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.activeQueryTemplateFeaturesController.status')
});
