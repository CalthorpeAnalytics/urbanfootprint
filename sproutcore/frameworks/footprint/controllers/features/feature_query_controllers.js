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


sc_require('controllers/features/feature_controllers');
sc_require('controllers/layer_selection_controllers');

/***
 * Provides a list of the available fields of the Feature class of the current layer as fully-qualified strings,
 * and optionally adds in the join table fields if one exists. This is a base class that can be extended
 * for particular DbEntities
 */
Footprint.AvailableFieldsController = Footprint.FeatureFieldsController.extend(Footprint.SearchFilterMixin, {
    allowsMultipleSelection:NO,

    // Prepend the DbEntity name to the list
    prependDbEntity: YES,
    dbEntities:null,

    /***
     * The TemplateFeature of the currently joined DbEntity
     */
    joinedTemplateFeatures: null,
    /***
     * The TemplateFeature of the DbEntity that is active in the query, currently always the last item
     */
    activeQueryTemplateFeature: null,
    activeQueryTemplateFeatureStatus: null,

    joinedTemplateFeaturesStatus: function() {
        return (this.get('joinedTemplateFeatures') || []).mapProperty('status').max() || SC.Record.EMPTY;
    }.property('joinedTemplateFeatures').cacheable(),

    templateFeaturesObserver: function() {
        SC.ObservableExtensions.propertyItemsAndStatusObservation(
            'joinedTemplateFeaturesObserving',
            this,
            'joinedTemplateFeatures',
            this,
            'joinedTemplateFeaturesStatusDidChange');
    }.observes('*joinedTemplateFeatures.[]'),
    joinedTemplateFeaturesStatusDidChange: function() {
        this.propertyDidChange('joinedTemplateFeaturesStatus');
    },

    /***
     * Adds the join and active DbEntity fields if either exist
     * They might be the same DbEntity
     */
    extraFields: function() {
        if (!(this.getPath('joinedTemplateFeaturesStatus') & SC.Record.READY))
            return;
        return (this.get('joinedTemplateFeatures') || []).uniq().filter(function(templateFeature) {
            // Make sure our joinedTemplateFeatures don't match the main one.
            return templateFeature != this.get('templateFeature');
        }, this).map(function(template_feature) {
            return (template_feature.get('feature_fields') || []).map(function(field) {
                return '%@.%@'.fmt(template_feature.getPath('db_entity.key'), field);
            });
        }).flatten();
    }.property('templateFeature', 'joinedTemplateFeatures', 'joinedTemplateFeaturesStatus').cacheable()
});

/***
 * The available fields and join fields for the active layer
 */
Footprint.availableFieldsWithJoinsController = Footprint.AvailableFieldsController.create({
    // The active DbEntity
    dbEntityBinding: SC.Binding.oneWay('Footprint.dbEntityActiveController.content'),
    // The DbEntities that are joined
    dbEntitiesBinding: SC.Binding.oneWay('Footprint.joinedDbEntitiesController.content'),
    templateFeatureBinding: SC.Binding.oneWay('Footprint.templateFeatureActiveController.content'),
    templateFeatureStatusBinding: SC.Binding.oneWay('Footprint.templateFeatureActiveController.status'),
    joinTemplateFeatureBinding: SC.Binding.oneWay('Footprint.joinedTemplateFeatureActiveController.content'),
    activeQueryTemplateFeatureBinding: SC.Binding.oneWay('Footprint.activeQueryTemplateFeatureActiveController.content'),
    /***
     * The TemplateFeature of the joined DbEntity and that of the active query DbEntity
     * are what we want to show as availabe from the dropdown.
     */
    joinedTemplateFeatures: function() {
        return [this.get('joinTemplateFeature') || null, this.get('activeQueryTemplateFeature') || null].compact().uniq();
    }.property('joinTemplateFeature', 'activeQueryTemplateFeature').cacheable(),

    // Binding here instead of the base class prevents a strange infinite loop
    statusBinding: SC.Binding.oneWay('.templateFeatureStatus'),

    /***
     * We can filter based on content, the available fields of the main and join Feature classes,
     * the collection of equality symbols
     * the collection of categorical values
     * the collection of conjunctions and groupers,
     */
    filteredItemsProperties: ['content', 'equalitySymbols', 'categoricalValues', 'conjunctions'],
    /***
     * Override to return different results based on the searchString
     */
    filteredItemsPropertyResolver: function() {
        // TODO filter properties based on searchContext
        return this.get('filteredItemsProperties');
    }.property('searchString', 'searchContext', 'filteredItemsProperties').cacheable(),
});
Footprint.equalitySymbolsController = Footprint.ArrayController.create(Footprint.SearchFilterMixin, {
    content: ['=', '!=', '>', '<', '>=', '<=', 'BEGINS_WITH', 'ENDS_WITH', 'CONTAINS']
});
Footprint.conjunctionsController = Footprint.ArrayController.create(Footprint.SearchFilterMixin, {
    content: ['AND', 'OR', '(', ')']
});

/***
 * Keeps track of the foreground Layers that may be selected by the user for a join
 * @type {SC.SelectionSupport}
 */
Footprint.joinLayersController = SC.ArrayController.create(SC.SelectionSupport, SC.ArrayStatus, {
    allowsMultipleSelection:YES,
    layerLibrary:null,
    layerLibraryBinding: SC.Binding.oneWay('Footprint.scenarioLayerLibraryApplicationController.content'),
    contentBinding: SC.Binding.oneWay('Footprint.layersForegroundController.content'),
    orderBy: ['name ASC'],
    /*
     * When the selection is updated, update the active layerSelection
     */
    selectionObserver: function() {
        if (this.getPath('selection') && this.didChangeFor('selectionObserver', 'selection')) {
            var dbEntityKeys = this.getPath('selection').mapProperty('dbEntityKey').filter(function(dbEntityKey) {
                return dbEntityKey != 'None';
            });
            // This soils the record, so don't set to empty if already empty
            if (Footprint.layerSelectionEditController.getPath('joins.length') > 0 ||
                dbEntityKeys.get('length') > 0) {
                Footprint.layerSelectionEditController.setIfChanged('joins', dbEntityKeys);
            } else {
                // This controller is loaded automatically when the Join changes
                // but there is nothing to unload it so clear it here
                Footprint.joinedTemplateFeaturesController.set('content', null);
            }
        }
    }.observes('.selection'),

    /*
     * When the layer_selection updates, change the selection
     */
    layerSelectionObserver: function() {
        if (this.get('content') && Footprint.layerSelectionEditController.get('status') & SC.Record.READY) {
            var joins = Footprint.layerSelectionEditController.getPath('joins');
            var layers = this.get('content').filter(function(layer) {
                return (joins || []).contains(layer.get('dbEntityKey'));
            });
            if (!SC.Set.create(layers).isEqual(SC.Set.create(this.get('selection'))))
                this.selectObjects(layers);
            this.updateSelectionAfterContentChange();
        }
    }.observes('.content',
            'Footprint.layerSelectionEditController.status',
            'Footprint.layerSelectionEditController.content',
            'Footprint.layerSelectionEditController.joins'
    ).cacheable()
});

Footprint.approvalQueriesController = Footprint.ArrayController.create({

    allowsEmptySelection:NO,
    activeRecordBinding: SC.Binding.oneWay('.parentView.layerSelection'),
    layer: null,
    layerBinding: SC.Binding.oneWay('Footprint.layerActiveController.content'),
    user: null,
    userBinding: SC.Binding.oneWay('Footprint.userController*content.firstObject'),

    activeView: 'Footprint.ApprovalView',

    // Used as a local constant for now
    description: function() {
        return 'Approval';
    }.property().cacheable(),

    content: function() {
        if (!this.get('layer') || !this.get('user'))
            return [];
        var layerSelections = Footprint.store.find(SC.Query.local(
            Footprint.LayerSelection, {
                conditions: 'user = {user} AND layer = {layer} AND description = {description} AND id = {id}',
                user: this.get('user'), layer: this.get('layer'), description: this.get('description'), id: null,
                orderBy: 'storeKey' // order of creation
            }));
        return layerSelections.get('length') > 0 ? layerSelections : Footprint.store.createRecords(Footprint.LayerSelection, [
            {
                layer: this.getPath('layer.id'),
                user: this.getPath('user.id'),
                description: 'Results',
                name: 'No Query Selected',
                query_strings: {
                    filter_string: null
                }
            },
            {
                layer: this.getPath('layer.id'),
                user: this.getPath('user.id'),
                description: 'Pending Edits',
                name: 'Load Edited Features - Pending',
                query_strings: {
                    filter_string: 'approval_status = "pending"'
                }
            },
            {
                layer: this.getPath('layer.id'),
                user: this.getPath('user.id'),
                description: 'Approved Edits',
                name: 'Load Edited Features - Approved',
                query_strings: {
                    filter_string: 'approval_status = "approved"'
                }
            },
            {
                layer: this.getPath('layer.id'),
                user: this.getPath('user.id'),
                description: 'Rejected Edits',
                name: 'Load Edited Features - Rejected',
                query_strings: {
                    filter_string: 'approval_status = "rejected"'
                }
            }
        ]);
    }.property('layer', 'user').cacheable()
});

Footprint.QueryAttributeExtractorMixin = {
    attributeParts: function() {
        var searchContext = this.get('searchContext');
        var tokenTree = searchContext.get('tokenTree');
        var tokenTreeFragment = searchContext.get('tokenTreeFragment');
        var tokenTreeBeforeFragment = searchContext.get('tokenTreeBeforeFragment');
        // From the tokenTree or rightmost clause or failing that the
        var clause = (tokenTree ?
            [rightSideClause(tokenTree, null, -1)['leftSide'], rightSideClause(tokenTree, null, -2)['leftSide']] :
            ((tokenTreeBeforeFragment && tokenTreeFragment) ?
                [tokenTreeFragment, tokenTreeFragment['leftSide'], tokenTreeBeforeFragment] : [])
        ).find(function(tokenTree) {

            return tokenTree && tokenTree['tokenType']=='PROPERTY';
        });
        if (!clause)
            return null;
        var tokenValue = clause['tokenValue'];
        return tokenValue && tokenValue.split('.');
    }.property('searchContext').cacheable()
};

/***
 * The TemplateFeature of the active DbEntity in the query. The active DbEntity is whatever
 * the last attribute of the query string is. Usually this will already be loaded
 * as the TemplateFeature of the main DbEntity of the Join one, but the load might be triggered
 * if the user types in a DbEntity that isn't loaded yet.
 */
Footprint.queryActiveTemplateFeature = SC.ObjectController.create(Footprint.QueryAttributeExtractorMixin, {
    searchContext: null,
    searchContextBinding: SC.Binding.oneWay('Footprint.availableFieldsWithJoinsController.searchContext'),
    dbEntities: null,
    dbEntitiesBinding: SC.Binding.oneWay('Footprint.dbEntitiesController.content'),
    content: function() {
        if (!this.get('searchContext'))
            return null;
        var parts = this.get('attributeParts');
        if (parts && parts.get('length')==2) {
            var dbEntityKey = parts.get('firstObject');
            var dbEntity = (this.get('dbEntities') || []).filterProperty('key', dbEntityKey).get('firstObject');
            if (dbEntity) {
                // Try to find the TemplateFeature in the store. It should be loaded
                return Footprint.store.find(SC.Query.local(
                    Footprint.TemplateFeature, {
                        conditions: 'db_entity = {dbEntity}',
                        dbEntity: dbEntity
                    })).get('firstObject');
            }
        }
        return null;
    }.property('searchContext').cacheable(),
});

/***
 * Stores the active DbEntity and its attribute of a query string. When either of the pair
 * change i
 */
Footprint.queryActiveAttribute = SC.ObjectController.create(Footprint.QueryAttributeExtractorMixin, {
    searchContext: null,
    searchContextBinding: SC.Binding.oneWay('Footprint.availableFieldsWithJoinsController.searchContext'),
    templateFeature: null,
    templateFeatureBinding: SC.Binding.oneWay('Footprint.queryActiveTemplateFeature.content').defaultValue(null),
    content: function() {
        if (!this.getPath('searchContext') || !this.get('templateFeature'))
            return null;
        var parts = this.get('attributeParts');
        if (parts && parts.get('length')==2) {
            var attribute = parts.get('lastObject');
            // Return the attribute if it matches a feature_field. It should unless
            // the user typed something that doesn't exist
            return this.getPath('templateFeature.feature_fields').find(function(field) {
                return field == attribute;
            });
        }
        return null;
    }.property('templateFeature', 'searchContext').cacheable(),

    // The LoadingFeatureAttributeState expects db_entity and attribute
    db_entity: null,
    db_entityBinding: SC.Binding.oneWay('*templateFeature.db_entity'),
    attribute: null,
    attributeBinding: SC.Binding.oneWay('.content'),

    contentObserver: function() {
        if (!this.didChangeFor('contentObserving', 'db_entity', 'attribute'))
            return;
        if (this.get('db_entity') && this.get('attribute')) {
            // Tell the statechart to load th FeatureAttribute for this DbEntity/attribute combo
            Footprint.statechart.sendEvent('doLoadQueryFeatureAttribute', this);
        }
        else {
            Footprint.statechart.sendEvent('doClearQueryFeatureAttribute', this);
        }
    }.observes('.db_entity', '.attribute')
});


/***
 * Holds the FeatureAttribute corresponding to the Footprint.queryActiveAttribute
 */
Footprint.queryFeatureAttributesController = Footprint.ArrayController.create({

});
Footprint.queryFeatureAttributeActiveController = SC.ArrayController.create(Footprint.SearchFilterMixin, {
    contentBinding: SC.Binding.oneWay('Footprint.queryFeatureAttributesController*firstObject.unique_values'),
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.queryFeatureAttributesController.status')
});
