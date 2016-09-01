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
 * Adds a mouseEntered and mouseExited function to any view to display its bindings and the
 * current value of those bindings in a popup window.
***/
Footprint.DebugBindingOverlay = {
    _matchesKeys: function(evt) {
        return evt.metaKey && evt.ctrlKey && evt.getCharString()=='b';
    },
    keyUp: function(evt) {
        if (this._debugPane && this._debugPane.get('isAttached'))
            this._debugPane.remove();
    },
    keyDown: function(evt) {
        // If the metaKey was pressed. This is the command key on Macintosh or the ? key on PCs
        if (this._matchesKeys(evt)) {
            this._debugPane = this._debugPane || SC.PickerPane.create({
                layout: { width: 800, height: 200 },
                // Override popup to create a reference to the anchor view
                popup: function (anchorViewOrElement, preferType, preferMatrix, pointerOffset) {
                    sc_super();
                    if (this._anchorView) {
                        this.set('anchor', this._anchorView);
                    }
                },
                contentView: SC.ScrollView.extend({
                    contentView: SC.SourceListView.extend({
                        anchorBinding: SC.Binding.oneWay('.parentView.parentView.parentView.anchor'),
                        // Content is the list of binding properties
                        contentBinding: SC.Binding.oneWay('.anchor').transform(function(value) {
                            return value && value._bindings;
                        }),
                        /***
                         * Displays a toString version of each binding
                         */
                        exampleView: SC.LabelView.extend({
                            anchor: null,
                            anchorBinding: SC.Binding.oneWay('.parentView.anchor'),
                            value: function() {
                                if (this.get('content') && this.get('anchor')) {
                                    var binding = this.get('anchor')[this.get('content')];
                                    return 'Binding: %@. Current Value: %@'.fmt(
                                        binding.toString(),
                                        binding._transformedBindingValue ?
                                            binding._transformedBindingValue.toString() :
                                            (typeof(binding) === 'undefined' ? 'undefined' : 'null')
                                    )
                                }
                                else {
                                    return "Loading binding %@...".fmt(this.get('content'))
                                }
                            }.property('content', 'anchor').cacheable()
                        })
                    })

                })
            })
            if (!this._debugPane.get('isAttached'))
                this._debugPane.popup(this);
        }
    }
}
