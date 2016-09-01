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


Footprint.PresentationsController = SC.ArrayController.extend({
});

/***
 * Base class to manage the presentations of a particular type (e.g. maps or results) of matching particular key set in the instantiations
 * @type {*}
 */
Footprint.PresentationController = SC.ObjectController.extend({

    // Set the key to the particular presentation of interest
    key: null,

    presentations:null,
    presentationsStatus:null,
    presentationsStatusBinding:SC.Binding.oneWay('*presentations.status'),

    /**
     * Represents the presentation of the bound configEntity that matches the bound key
     */
    // This would work if the presentationStatus READY_CLEAN didn't precede the items being READY_CLEAN
    content: function() {
        if (this.get('presentations') && (this.getPath('presentationsStatus') & SC.Record.READY)) {
            return this.get('presentations').filter(function(presentation, i) {
                return presentation.get('key') == this.get('key');
            }, this)[0];
        }
        else
            return null;
    }.property('presentations', 'presentationsStatus', 'key').cacheable(),

    // TODO what is this for?
    keys: null
});



/***
 * Aggregates content from the subclasses of the controllers defined above. Assign this to a the content of a
 * LibraryController subclass and use that LibraryController for library views
 * @type {*}
 */
Footprint.LibraryContent = SC.Object.extend({
    init: function() {
        sc_super();
        this.bind('*presentationController.presentation', '.presentation');
        this.bind('*presentationController.keys', '.keys');
        this.bind('*presentationMediaController.content', '.items');
        this.bind('*presentationMediaController.dbEntitiesByKey', '.dbEntitiesByKey');
        this.bind('*presentationMediaController.selectedDbEntitiesByKey', '.selectedDbEntitiesByKey');
    },

    // A Footprint.PresentationController instance that binds a Presentation
    presentationController:null,
    // A Footprint.PresentationMediaController instance that binds the Presentation's PresentationMedium instances
    presentationMediaController:null,

    // The active ConfigEntity
    configEntity:null,
    // Bound on init to the presentationController.presentation
    presentation:null,

    /***
     * All the PresentationMedium instances of the Presentation
     */
    items:null,

    /***
     * Bound on init to the presentationMediaController.dbEntitiesByKey. This is an SC.Object with attributes
     * that are the keys of the DbEntities with array values that are the matching DbEntities
     */
    dbEntitiesByKey: null,
    /***
     * Bound on init to the presentationMediaController.selectedDbEntitiesByKey. This is an SC.Object with
     * attributes that are the keys of the DbEntities with a single DbEntity for a value that represents
     * the one or only DbEntity with that key that is marked selected
     * TODO no longer relevant. DbEntity keys are not shared within a ConfigEntity
     */
    selectedDbEntitiesByKey: null,
    /***
     * All of the keys assigned to all the DbEntities
     */
    keys:null,

    tables:null,
    /***
     * This is bound to the active Scenario. In the future it should be bound to the more general active ConfigEntity
     */
    configEntityBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content').single()
});

/***
 * Base class to extend to bind to a currently active PresentationMedium of a Presentation.
 * You must bind content to the list of PresentationMedium instances when subclassing.
 * @type {*}
 */
Footprint.PresentationMediumActiveController = Footprint.ActiveController.extend({
});

/***
 * Used for buffered editing of a PresentationMedium
 * You must set objectControllerBinding to the PresentationMediumActiveController whose presentationMedium is to be edited
 * @type {*}
 */
Footprint.PresentationMediumEditController = SC.ObjectController.extend({

    // Used to create new instances
    recordType: Footprint.PresentationMedium
});

Footprint.MediaController = SC.ArrayController.extend(Footprint.ArrayContentSupport, {
});
