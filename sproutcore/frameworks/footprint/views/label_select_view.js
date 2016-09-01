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

sc_require('views/editable_model_string_view');
sc_require('views/menu_button_view');
sc_require('views/view_mixins/debug_binding_overlay');
sc_require('views/overlay_view');


Footprint.LabelSelectView = SC.PopupButtonView.extend({

    classNames:['footprint-label-select-view', 'theme-button', 'theme-button-gray'],
    localize: YES,
    theme: 'popup',

    /***
     * Call to explicitly remove the popup menu. Normally this happens automatically when the menu loses firstResponder
     * status, but you can call it manually if you need another view to trigger its closing
     */
    removeMenu: function() {
        if (this.get('menu') && this.getPath('menu.isAttached'))
            this.get('menu').remove();
    },
    /***
     * Explicitly make the menu the keyPane
     */
    makeMenuContentFirstResponder: function() {
        if (this.get('menu'))
            this.get('menu').makeContentFirstResponder()
    },

    /***
     * Explicitly select the first item in the menu
     */
    selectFirstMenuItem: function() {
        var selection = this.get('selection');
        if (selection)
        if (this.get('menu'))
            this.get('menu').selectFirstItem();
    },

    deselectAllFromMenu: function() {
        if (this.get('menu'))
            this.get('menu').deselectAll();
        // This should be needed. deselectAll should do it
        this.set('selection', SC.SelectionSet.EMPTY);
    },

    /***
     * Called when the user keys up when the top item is selected. This indicates that
     * the user doesn't want to select anything
    */
    handleKeyUpFromFirstItem: function() {

    },
    /***
     * Called when the user is selected a menu item and hits the enter key
     * The idea of this is when something is selected the user hits enter and the menu closes,
     * returning focus to this view
     */
    handleEnterFromMenu: function() {

    },

    /***
     * Override to fix the arguments to popup, which might meed to be for a PickerPane instead
     * of a MenuPane
     * @param evt
     * @returns {boolean}
     */
    action: function(evt) {
        var menu = this.get('instantiatedMenu') ;

        if (!menu) {
          // @if (debug)
          SC.Logger.warn("SC.PopupButton - Unable to show menu because the menu property is set to %@.".fmt(menu));
          // @endif
          return NO ;
        }

        if (this.get('menuPaneType').kindOf(SC.PickerPane))
            menu.popup(this, this.get('preferType'), this.get('preferMatrix')) ;
        else
            menu.popup(this, this.get('preferMatrix')) ;
        return YES;
    },

    /**
     * Required. the items to select from.
     */
    content: null,
    /***
     * Usually required to sync the selctedItem to a controller. However without a selection you
     * can simply send and action to a state chart when an item is clicked
     */
    selection:null,
    /***
     * Optional recordType to send along with the action when something is clicked
     */
    recordType:null,

    /***
     * Default false since usually a popup just allows one value
     */
    allowsMultipleSelection: NO,
    /***
     * By default, when an item is selected from the menu it sends the action.
     * Disable this to force the user to click or hit enter on the item to send the action
     */
    actOnSelect: YES,
    // Indicates if items in the list can be selected
    // This means they can be highlighted.
    isSelectable: YES,
    // Add a null item to the top of the list, titled by nullTitle
    includeNullItem:NO,
    // Only add a null item if the content is empty (this overrides includeNullItem)
    // This will also make the pull down disabled
    includeNullItemIfEmpty:NO,

    // Tell properties if the content contents change. We should be able to put content.[]
    // on a property but it's buggy
    contentDidChange: function() {
        this.propertyDidChange('nullItemIncluded');
        this.propertyDidChange('menuItems');
    }.observes('*content.[]'),

    nullItemIncluded: function() {
        var contentIsEmpty = this.getPath('content.length') == 0;
        return (!contentIsEmpty && this.get('includeNullItem') && !this.get('includeNullItemIfEmpty')) ||
               (contentIsEmpty && this.get('includeNullItemIfEmpty'));
    }.property('content', 'includeNullItem', 'includeNullItemIfEmpty').cacheable(),

    // The title to use for the null item if includeNullItem is YES or includeNullItemIfEmpty is YES
    // Also used for the button title if no item is selected, unless nullTitleIfEmpty is specified
    // nullTitleIfEmpty will take precedent if non-null if includeNullItemIfEmpty is YES
    nullTitle: null,
    // The title to use to tell users that the list is empty
    nullTitleIfEmpty: null,
    resolvedNullTitle: function() {
       return this.get('nullTitleIfEmpty') || this.get('nullTitle');
    }.property('nullTitle', 'nullTitleIfEmpty').cacheable(),

    // The max height of the popup panel
    maxHeight: 300,
    // Optional menu width that is different than the button width
    menuWidth: null,
    // An icon to use for the button instead of showing the currently selected item
    icon: null,
    // The SC class to use for the popup. Defaults to SC.PickerPane
    menuPaneType: SC.PickerPane,
    // Override the default modality of the menuPane type
    menuIsModal: YES,

    // This is all hacked since firstSelection won't update as it should
    firstSelectedItem:null,
    firstSelectedItemBinding:SC.Binding.oneWay('*selection.firstObject'),
    selectedItem: function() {
        if (this.get('selectionDidUpdate')) {
            this.set('selectionDidUpdate', NO);
        }
        return this.getPath('selection.firstObject');
    }.property('firstSelectedItem').cacheable(),

    /***
     * The selectedItem or selectedItem.get(itemTitleKey), if itemTitleKey is defined
     */
    selectedItemValue: function() {
        var result;
        if (this.get('itemTitleKey')) {
            var selectedItem = this.get('selectedItem');
            if (selectedItem) {
                result = selectedItem.get(this.get('itemTitleKey'));
            }
        }
        else {
            result = this.get('selectedItem')
        }
        return result
    }.property('selectedItem', 'itemTitleKey').cacheable(),

    /***
     * Defaults to the status of the content. Optionally override status with something else
     */
    status: function() {
        return this.get('contentStatus');
    }.property('contentStatus').cacheable(),

    contentStatus: null,
    contentStatusBinding: SC.Binding.oneWay('*content.status'),
    selectedItemStatus: null,
    /***
     * Observe the selectedItem status instead of binding in cased our items don't have statuses
     */
    selectedItemStatusObserver: function() {
        var selectedItem = this.get('selectedItem')
        if (typeof(selectedItem)==='object' && selectedItem.isObject &&
            selectedItem.didChangeFor('selectedItemStatusObserver', 'status')) {
            this.notifyPropertyChange('title');
        }
    }.observes('*selectedItem.status'),

    // The action to take when selecting an item
    selectionAction: null,
    // The optional target of the selectionAction, defaults to null
    selectionTarget: null,

    /**
     * The attribute of each item to display in the menu and label. null for primitives
     */
    itemTitleKey: null,

    // Resolves the attribute value of itemTitleKey on the value.
    title: function () {
        // No title is shown if a buttonIcon is present
        if (this.get('icon'))
            return null;
        var selectedItem = this.get('selectedItem');
        var nullTitle = this.get('resolvedNullTitle');
        return this.get('selectedItemValue') || nullTitle;
    }.property('selectedItem', 'selectedItemValue', 'itemTitleKey', 'resolvedNullTitle').cacheable(),

    itemsStatus: null,
    itemsStatusBinding: SC.Binding.oneWay('*items.status'),
    menuItems: function () {
        if (this.getPath('status') & SC.Record.READY ||
            (this.get('content') && !this.getPath('content.status'))) {
            return (this.get('nullItemIncluded') ?
                    [null] :
                    []).concat(this.get('content') ? this.get('content').toArray() : []);
        }
    }.property('status', 'content').cacheable(),

    /***
     * Optional, used in conjunction with preferMatrix if the pane is an SC.PickerPane
     */
    preferType: null,

    // Use this flag to temporarily disallow accepting the keyPane when we pop open the labelSelectView
    // in response to the user typing text
    _acceptKeyPane: YES,


    menu: function() {
        return this.get('menuPaneType').extend({
            layout: {top: 16, height: 0, left: 0, width: 400},
            maxHeightBinding: SC.Binding.oneWay('*anchor.maxHeight').defaultValue(300),
            anchorBinding: SC.Binding.oneWay('.anchor'),
            // Override if specified on the anchor
            isModalBinding: SC.Binding.oneWay('*anchor.menuIsModal'),
            // We can't send an action without having a root responder on the pane. Don't know why

            /***
             * Don't become the keyPane nor firstResponder unless the user explicitly clicked on this or similar.
             * We don't want to gain focus when it pops up
             */
            didAppendToDocument: function () {
                if (this.getPath('anchor._acceptKeyPane'))
                    sc_super();
            },

            /***
             * Manually select the first item from the list
             */
            selectFirstItem: function() {
                if (this.get('selection'))
                    this.getPath('contentView.scrollView.contentView').select(0);
            },
            /***
             * Deselect all selections
             */
            deselectAll: function() {
                if (this.get('selection'))
                    this.getPath('contentView.scrollView.contentView').deselectAll();
            },
            /***
             * Makes the SourceListView the first responder so that it has focus and keyboard input
             */
            makeContentFirstResponder: function() {
                this.getPath('contentView.scrollView.contentView').becomeFirstResponder();
                this.becomeKeyPane();
            },


            popup: function (anchorViewOrElement, preferType, preferMatrix, pointerOffset) {
                // Depending on the base class, we may or may not have a super. Otherwise assume we have to
                // append the pane ourselves
                this.set('anchor', this._anchorView || anchorViewOrElement);
                if (this.getPath('anchor.menuPaneType.prototype.popup'))
                    sc_super();
                if (this.get('anchor')) {
                    this.adjust('width',
                            // If the menuWidth is specified use it here for the width
                        // Otherwise use the whole view's width, like the button does
                        this._anchorView.get('menuWidth') ?
                            this._anchorView.get('menuWidth') :
                            this._anchorView.getPath('frame.width'));
                }
                if (!this.getPath('anchor.menuPaneType.prototype.popup'))
                    this.append();
            },

            contentBinding: SC.Binding.oneWay('*anchor.menuItems'),
            status: null,
            statusBinding: SC.Binding.oneWay('*anchor.status'),
            selection: null,
            selectionBinding: '*anchor.selection',

            isSelectable: null,
            isSelectableBinding: '*anchor.isSelectable',
            // default to content for primitives, otherwise the titleKey will delegate through content
            itemTitleKeyBinding: SC.Binding.oneWay('*anchor.itemTitleKey'),
            nullItemIncluded: null,
            nullItemIncludedBinding: SC.Binding.oneWay('*anchor.nullItemIncluded'),
            nullTitle: null,
            nullTitleBinding: SC.Binding.oneWay('*anchor.resolvedNullTitle'),
            selectionAction: null,
            selectionActionBinding: SC.Binding.oneWay('*anchor.selectionAction'),
            selectionTarget: null,
            selectionTargetBinding: SC.Binding.oneWay('*anchor.selectionTarget'),
            allowsMultipleSelection: NO,
            allowsMultipleSelectionBinding: SC.Binding.oneWay('*anchor.allowsMultipleSelection'),
            actOnSelect: null,
            actOnSelectBinding: SC.Binding.oneWay('*anchor.actOnSelect'),
            recordType: null,
            recordTypeBinding: SC.Binding.oneWay('*anchor.recordType'),

            contentView: SC.View.extend({
                childViews: ['overlayView', 'scrollView'],

                status: null,
                statusBinding: SC.Binding.oneWay('.parentView.status'),

                overlayView: Footprint.OverlayView.extend({
                    layoutBinding: SC.Binding.oneWay('.parentView.scrollView.layout'),
                    statusBinding: SC.Binding.oneWay('.parentView.status'),
                    showLabel: YES
                }),

                scrollView: SC.ScrollView.extend({
                    content: null,
                    contentBinding: SC.Binding.oneWay('.parentView.parentView.content'),
                    selection: null,
                    selectionBinding: '.parentView.parentView.selection',

                    isSelectable: null,
                    isSelectableBinding: '.parentView.parentView.isSelectable',
                    itemTitleKey: null,
                    itemTitleKeyBinding: SC.Binding.oneWay('.parentView.parentView.itemTitleKey'),
                    nullItemIncluded: null,
                    nullItemIncludedBinding: SC.Binding.oneWay('.parentView.parentView.nullItemIncluded'),
                    nullTitle: null,
                    nullTitleBinding: SC.Binding.oneWay('.parentView.parentView.nullTitle'),
                    action: null,
                    actionBinding: SC.Binding.oneWay('.parentView.parentView.selectionAction'),
                    target: null,
                    targetBinding: SC.Binding.oneWay('.parentView.parentView.selectionTarget'),
                    allowsMultipleSelection: NO,
                    allowsMultipleSelectionBinding: SC.Binding.oneWay('parentView.parentView.allowsMultipleSelection'),
                    actOnSelect: null,
                    actOnSelectBinding: SC.Binding.oneWay('.parentView.parentView.actOnSelect'),
                    recordType: null,
                    recordTypeBinding: SC.Binding.oneWay('.parentView.parentView.recordType'),

                    contentView: SC.SourceListView.extend({
                        classNames: 'footprint-label-select-content-view'.w(),
                        rowHeight: 18,

                        action: null,
                        actionBinding: SC.Binding.oneWay('.parentView.parentView.action').transform(function (value) {
                            return value || 'doPickSelection';
                        }),
                        target: null,
                        targetBinding: SC.Binding.oneWay('.parentView.parentView.target'),
                        allowsMultipleSelection: NO,
                        allowsMultipleSelectionBinding: SC.Binding.oneWay('parentView.parentView.allowsMultipleSelection'),
                        actOnSelectBinding: SC.Binding.oneWay('.parentView.parentView.actOnSelect'),
                        recordType: null,
                        recordTypeBinding: SC.Binding.oneWay('.parentView.parentView.recordType'),

                        contentBinding: SC.Binding.oneWay('.parentView.parentView.content'),
                        selectionBinding: '.parentView.parentView.selection',
                        isSelectableBinding: SC.Binding.oneWay('.parentView.parentView.isSelectable'),
                        itemTitleKey: null,
                        itemTitleKeyBinding: SC.Binding.oneWay('.parentView.parentView.itemTitleKey'),
                        nullItemIncluded: null,
                        nullItemIncludedBinding: SC.Binding.oneWay('.parentView.parentView.nullItemIncluded'),
                        nullTitle: null,
                        nullTitleBinding: SC.Binding.oneWay('.parentView.parentView.nullTitle'),
                        isEnabled: function () {
                            return this.getPath('content') && this.getPath('content.length') > (this.get('nullItemIncluded') ? 1 : 0);
                        }.property('content', 'nullItemIncluded').cacheable(),

                        /***
                         * Override to interpret key up events when the first item is selected to mean
                         * that the user is trying to go back up to the anchor of the menu pane or similar.
                         * Also remove the pane upon hitting enter
                         * @param evt
                         * @returns {boolean}
                         */
                        keyDown: function (evt) {
                            var selectedItem = this.getPath('selection.firstObject');
                            var ret = sc_super();
                            if (evt.keyCode === SC.Event.KEY_UP && this.get('content').indexOf(selectedItem) == 0) {
                                this.getPath('pane.anchor').handleKeyUpFromFirstItem();
                            }
                            else if (evt.keyCode === SC.Event.KEY_RETURN) {
                                this.get('pane').remove();
                                this.getPath('pane.anchor').handleEnterFromMenu();
                            }
                            return ret;
                        },
                        /***
                         * Remove the pane whenever something is explicitly clicked
                         * @param evt
                         * TODO make an exception when a modifier key is down for multi-select
                         */
                        mouseDown: function (evt) {
                            var ret = sc_super();
                            var labelSelectView = this.getPath('pane.anchor');
                            labelSelectView.removeMenu();
                            return ret
                        },

                        frameDidChange: function () {
                            if (!this.getPath('pane.maxHeight'))
                                return;
                            if (this.getPath('frame.height') !== this._height) {
                                this.get('pane').adjust('height', [this.getPath('pane.maxHeight'), this.getPath('frame.height')].min());
                                this.invokeLast(function () {
                                    this.getPath('pane.contentView').notifyPropertyChange('frame');
                                });
                            }
                            this._height = this.getPath('frame.height');
                        }.observes('.frame'),


                        exampleView: SC.View.extend(SC.Control, {
                            classNames: 'footprint-label-select-item-view'.w(),
                            childViews: ['labelView'],

                            itemTitleKey: null,
                            itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),
                            nullTitle: null,
                            nullTitleBinding: SC.Binding.oneWay('.parentView.nullTitle'),

                            labelView: SC.LabelView.extend({
                                classNames: 'footprint-label-select-item-label-view'.w(),
                                layout: {top: 2, left: 5, right: 5, height: 15},
                                contentBinding: SC.Binding.oneWay('.parentView.content'),
                                contentValueKey: null,
                                contentValueKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),
                                nullTitle: null,
                                nullTitleBinding: SC.Binding.oneWay('.parentView.nullTitle'),
                                value: function () {
                                    if (this.get('content') && !this.get('contentValueKey')) {
                                        // content is string case. Otherwise we rely on content+contentValueKey
                                        return this.get('content');
                                    }
                                    return this.get('content') ? this.get('content').getPath(this.get('contentValueKey')) : this.get('nullTitle');
                                }.property('contentValueKey', 'content', 'nullTitle')
                            })
                        })
                    })
                })
            })
        });
    }.property('menuPaneType').cacheable()
});
