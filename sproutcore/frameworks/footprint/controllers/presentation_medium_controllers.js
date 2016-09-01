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
 * Base class to controller the PresentationMedium instances of a particular presentation
 * You must set the presentationBinding to bind to a particular presentation
 * @type {*}
 */
Footprint.PresentationMediaController = SC.ArrayController.extend(SC.SelectionSupport, {

    orderBy: ['sortPriority DESC', 'name ASC'],

    /**
     * The owning Presentation of the PresentationMedium instances
     */
    presentation:null,

    /**
     * The Presentation's ConfigEntity
     */
    configEntity: null,
    configEntityBinding: '*presentation.config_entity',
    /**
     * status needs to be explicitly set to the content.status, because content is a ManyArray
     * for some reason the controller delegation of status doesn't "keep up" when content changes
     */
    contentStatus: function() {
       return this.getPath('content.status');
    }.property('content').cacheable(),

    db_entities: function() {
        if (this.get('content') && this.get('contentStatus') & SC.Record.READY) {
            return this.get('content').mapProperty('db_entity');
        }
    }.property('content', 'contentStatus').cacheable(),

    tables: function() {
        if (this.get('content') && this.get('contentStatus') & SC.Record.READY) {
            return this.get('content').mapProperty('db_entity.table');
        }
    }.property('content', 'contentStatus').cacheable(),

    /**
     * Groups the db_entities into an SC.Object keyed by unique db_entity key, each valued by an array of one or more DbEntity instances
     */
    dbEntitiesByKey: function() {
        if (this.get('db_entities')) {
            return $.mapToCollectionsObject(
                this.get('db_entities').toArray(),
                function(db_entity) {
                    return db_entity.getPath('key');
                },
                function(db_entity) { return db_entity;},
                function() {
                    return SC.Object.create({
                        toString: function() {
                            return "DbEntitiesByKey";
                        }
                    });
                }
            )
        }
    }.property('db_entities').cacheable(),

    selectedDbEntitiesByKey: function() {
        if (this.get('configEntity'))
            return this.getPath('configEntity.selections.db_entities');
    }.property('configEntity'),

    /**
     * Keeps track of the PresentationMedium instances that are soloing.
     */
    _solos:[],

    /**
     * Sets the items that are soloing and disables the solos of all other items. This does not change the visible property of other items. It's up to the presenter of the items (e.g. the MapView to use isVisible to see if items are hidden due to their own state or because and item is soloing.
     */
    solos: function(propKey, value) {
        if (value===undefined) {
            return this.get('_solos');
        }
        else {
            this.get('content').forEach(function(presentationMedium) {
                // Disable the solo state of all other items by reverting visibility to the visible value
                if (!value.contains(presentationMedium)) {
                    presentationMedium.set('visibility', presentationMedium.get('applicationVisible'))
                }
            }, this);
            this.set('_solos', value);
        }
    }.property('content'),

    /***
     * Returns the visibility state of the presentationMedium, depending on if any items are soloing. If the given instance is soloing or no items are soloing and the given instance is not hidden, the function returns YES
     * @param presentationMedium
     * @returns {*|boolean}
     */
    isVisible: function(presentationMedium) {
        return this.get('solos').contains(presentationMedium) || (this.get('solos').length == 0 && presentationMedium.get('visibility')==Footprint.VISIBLE);
    },

    // TODO dbEntitiesByKey isn't dumping
    toString: function() {
        return "%@:\n%@".fmt(sc_super(), this.toStringAttributes('configEntity presentation content db_entities  selectedDbEntitiesByKey'.w()));
    }
});
