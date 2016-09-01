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



FootprintScagDm.ScagExistingLandUseParcelFeature = Footprint.Feature.extend({

    // land_use_definition and scag_lu are kept synced.
    land_use_definition: SC.Record.toOne('Footprint.ClientLandUseDefinition', {
        isMaster: YES
    }),
    scag_lu: SC.Record.attr(Number),

    landUseDefinitionObserver: function() {
        if ((this.get('status') && SC.Record.READY) && (this.getPath('land_use_definition.status') & SC.Record.READY) ) {
           this.setIfChanged('scag_lu', parseInt(this.getPath('land_use_definition.land_use')));
       }
    }.observes('.land_use_definition', '*land_use_definition.status', '.status'),

    scaguid : SC.Record.attr(Number),
    city : SC.Record.attr(String),
    county : SC.Record.attr(String),
    apn : SC.Record.attr(String),
    acres : SC.Record.attr(Number),
    notes : SC.Record.attr(String),

    // Note that this land use has not foreign key representation
    scag_lu_secondary: SC.Record.attr(Number),

    // Simulate having a foreign key version of scag_lu_secondary to make editing
    // match that of land_use_definition
    land_use_definition_secondary: null,

    // Update land_use_definition_secondary to scag_lu_secondary when the latter changes
    scagLuSecondaryObserver: function() {
        // Search the store for the matching Footprint.ClientLandUseDefinition
        // as long as they have loaded
        if ((this.get('status') & SC.Record.READY) &&
            (Footprint.clientLandUseDefinitionController.get('status') & SC.Record.READY)) {

            if (!this.didChangeFor('scagLuSecondaryTracker', 'scag_lu_secondary', 'status'))
                return;

            var scagLuSecondary = this.get('scag_lu_secondary');
            this.setIfChanged(
                'land_use_definition_secondary',
                scagLuSecondary ?
                    this.get('store').find(Footprint.ClientLandUseDefinition, scagLuSecondary) :
                    null
            );
        }
    }.observes('.scag_lu_secondary', '.status', 'Footprint.clientLandUseDefinitionController.status'),

    // Update scag_lu_secondary to land_use_definition_secondary when the latter changes
    landUseDefinitionSecondaryObserver: function() {
        if (this.get('status') & SC.Record.READY) {
            if (!this.didChangeFor('landUseDefinitionSecondaryTracker', 'land_use_definition_secondary', 'status'))
                return;

            var landUseDefinitionSecondary = this.get('land_use_definition_secondary');
            this.setIfChanged(
                'scag_lu_secondary',
                landUseDefinitionSecondary ?
                    parseInt(this.getPath('land_use_definition_secondary.land_use')) :
                    null
            );

       }
    }.observes('.land_use_definition_secondary', '.status'),
});

FootprintScagDm.ScagGeneralPlanParcelFeature = Footprint.Feature.extend({
    land_use_definition: SC.Record.toOne('Footprint.ClientLandUseDefinition', {
        isMaster: YES
    }),

    landUseDefinitionObserver: function() {
        if ((this.get('status') & SC.Record.READY) && (this.getPath('land_use_definition.status') & SC.Record.READY)) {
           this.setIfChanged('scag_gp_code', this.getPath('land_use_definition.land_use'));
       }
    }.observes('.land_use_definition', '*land_use_definition.status', '.status'),

    zone_code: SC.Record.attr(String),
    general_plan_code: SC.Record.attr(String),
    scag_gp_code: SC.Record.attr(Number),
    apn: SC.Record.attr(String),
    year_adopt: SC.Record.attr(String),
    city_gp_code: SC.Record.attr(String),
    notes: SC.Record.attr(String),
    scag_gp_secondary: SC.Record.attr(Number),
    density: SC.Record.attr(Number),
    low: SC.Record.attr(Number),
    high: SC.Record.attr(Number),

    // Simulate having a foreign key version of scag_lu_secondary to make editing
    // match that of land_use_definition
    land_use_definition_secondary: null,

    // Update land_use_definition_secondary to scag_lu_secondary when the latter changes
    scagGpSecondaryObserver: function() {
        // Search the store for the matching Footprint.ClientLandUseDefinition
        // as long as they have loaded
        if ((this.get('status') & SC.Record.READY) &&
            (Footprint.clientLandUseDefinitionController.get('status') & SC.Record.READY)) {

            if (!this.didChangeFor('scagGpSecondaryTracker', 'scag_gp_secondary', 'status'))
                return;

            var scagGpSecondary = this.get('scag_gp_secondary');
            this.setIfChanged(
                'land_use_definition_secondary',
                scagGpSecondary ?
                    this.get('store').find(Footprint.ClientLandUseDefinition, scagGpSecondary) :
                    null
            );
        }
    }.observes('.scag_gp_secondary', '.status'),

    // Update scag_lu_secondary to land_use_definition_secondary when the latter changes
    landUseDefinitionSecondaryObserver: function() {
        if (this.get('status') & SC.Record.READY) {
            if (!this.didChangeFor('landUseDefinitionSecondaryTracker', 'land_use_definition_secondary', 'status'))
                return;

            var landUseDefinitionSecondary = this.get('land_use_definition_secondary');
            this.setIfChanged(
                'scag_gp_secondary',
                landUseDefinitionSecondary ?
                    parseInt(this.getPath('land_use_definition_secondary.land_use')) :
                    null
            );

       }
    }.observes('.land_use_definition_secondary', '.status'),


});


FootprintScagDm.ScagEntitlementParcelFeature = Footprint.Feature.extend({

    apn: SC.Record.attr(String),
    scaguid12 : SC.Record.attr(Number),
    city: SC.Record.attr(String),
    county: SC.Record.attr(String),
    acres: SC.Record.attr(Number),
    tract_no: SC.Record.attr(String),
    dev_agmt: SC.Record.attr(String),
    address: SC.Record.attr(String),
    date_appro: SC.Record.attr(String),
    date_start: SC.Record.attr(String),
    multi_par: SC.Record.attr(Number),
    proj_type: SC.Record.attr(String),
    pop: SC.Record.attr(Number),
    du_sf: SC.Record.attr(Number),
    du_mf: SC.Record.attr(Number),
    emp: SC.Record.attr(Number),
    emp_type: SC.Record.attr(String),
    emp_sqft: SC.Record.attr(Number),
    proj_phase: SC.Record.attr(String),
    time_limit: SC.Record.attr(String),
    notes: SC.Record.attr(String),
    is_modified: SC.Record.attr(String),

    isModifiedObserver: function() {
        if (this.get('status') & SC.Record.READY) {
           this.setIfChanged('is_modified', 'true');
       }
    }.observes('.approval_status', '.status'),
});

FootprintScagDm.ScagJurisdictionBoundary = Footprint.Feature.extend({
    city_uid: SC.Record.attr(String),
    city: SC.Record.attr(String),
    county: SC.Record.attr(String),
    county_id: SC.Record.attr(Number),
    pop12: SC.Record.attr(Number),
    pop20: SC.Record.attr(Number),
    pop35: SC.Record.attr(Number),
    pop40: SC.Record.attr(Number),
    hh12: SC.Record.attr(Number),
    hh20: SC.Record.attr(Number),
    hh35: SC.Record.attr(Number),
    hh40: SC.Record.attr(Number),
    emp12: SC.Record.attr(Number),
    emp20: SC.Record.attr(Number),
    emp35: SC.Record.attr(Number),
    emp40: SC.Record.attr(Number),
    comment: SC.Record.attr(String),
});

FootprintScagDm.ScagTier2TazFeature = Footprint.Feature.extend({
    fips: SC.Record.attr(Number),
    city: SC.Record.attr(String),
    subregion: SC.Record.attr(String),
    subregion_id: SC.Record.attr(Number),
    county: SC.Record.attr(String),
    county_id: SC.Record.attr(Number),
    tier2: SC.Record.attr(String),
    ct2: SC.Record.attr(String),
    pop12: SC.Record.attr(Number),
    pop20: SC.Record.attr(Number),
    pop35: SC.Record.attr(Number),
    pop40: SC.Record.attr(Number),
    hh12: SC.Record.attr(Number),
    hh20: SC.Record.attr(Number),
    hh35: SC.Record.attr(Number),
    hh40: SC.Record.attr(Number),
    emp12: SC.Record.attr(Number),
    emp20: SC.Record.attr(Number),
    emp35: SC.Record.attr(Number),
    emp40: SC.Record.attr(Number),
    notes: SC.Record.attr(String),
});

FootprintScagDm.ScagScenarioPlanningZones = Footprint.Feature.extend({
    spzid: SC.Record.attr(String),
    city_uid: SC.Record.attr(String),
    city: SC.Record.attr(String),
    notes: SC.Record.attr(String),
});
