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
// Project:   SC.HorizontalListView
// ==========================================================================
/*globals SC */


sc_require('views/list_views/collection_column_delegate');

/** @class

    (Document Your View Here)

 @extends SC.CollectionView
 */
SC.HorizontalListView = SC.CollectionView.extend(SC.CollectionColumnDelegate,
    SC.CollectionRowDelegate,
    /** @scope SC.HorizontalListView.prototype */
    {

        classNames: 'horizontal-list-view',

        acceptsFirstResponder: YES,

        /**
         * If set to YES, the default theme will show alternating columns
         * for the views this HorizontalListView created through exampleView property.
         *
         * @property {Boolean}
         */
        showAlternatingColumns: NO,

        horizontalSpacing: 0,

        itemsPerRow: function() {
            return this.get('length');
        }.property().cacheable(),

        // ..........................................................
        // METHODS
        //
        render: function(context, firstTime) {
            context.setClass('alternating', this.get('showAlternatingColumns'));

            return sc_super();
        },

        // ..........................................................
        // COLLECTION COLUMN DELEGATE SUPPORT
        //
        /**
         Returns the current collectionColumnDelegate.  This property will recompute
         everytime the content changes.
         */
        columnDelegate: function() {
            var del = this.delegate,
                content = this.get('content');
            return this.delegateFor('isCollectionColumnDelegate', del, content);
        }.property('delegate', 'content').cacheable(),

        /**
         @field
         @type Object
         @observes 'delegate'
         @observes 'content'
         */
        rowDelegate: function() {
            var del = this.delegate,
                content = this.get('content');

            return this.delegateFor('isCollectionRowDelegate', del, content);
        }.property('delegate', 'content').cacheable(),

        // ..........................................................
        // COLUMN PROPERTIES
        //

        leftPadding: 0,

        rightPadding: 0,

        /**
         Returns the column width for the specified content index.  This will take
         into account custom column widths and group columns.

         @param {Number} idx content index
         @returns {Number} the column width
         */
        columnWidthForContentIndex: function(idx) {
            var del = this.get('columnDelegate'),
                ret,
                cache,
                content,
                indexes;

            if (del.customColumnWidthIndexes && (indexes = del.get('customColumnWidthIndexes'))) {
                cache = this._hlv_widthCache;
                if (!cache) {
                    cache = this._hlv_widthCache = [];
                    content = this.get('content');
                    indexes.forEach(function(idx) {
                            cache[idx] = del.contentIndexColumnWidth(this, content, idx);
                        },
                        this);
                }

                ret = cache[idx];
                if (ret === undefined) ret = del.get('columnWidth');
            } else ret = del.get('columnWidth');

            return ret;
        },

        /**
         Returns the left offset for the specified content index.  This will take
         into account any custom column widths and group views.

         @param {Number} idx the content index
         @returns {Number} the column offset
         */
        columnOffsetForContentIndex: function(idx) {
            if (idx === 0) return 0; // fastpath
            var del = this.get('columnDelegate'),
                columnWidth = del.get('columnWidth'),
                ret,
                custom,
                cache,
                delta,
                max,
                content;

            ret = idx * columnWidth;

            if (this.get('horizontalSpacing')) {
                ret += idx * this.get('horizontalSpacing');
            }

            if (del.customColumnWidthIndexes && (custom = del.get('customColumnWidthIndexes'))) {

                // prefill the cache with custom columns.
                cache = this._hlv_offsetCache;
                if (!cache) {
                    cache = this._hlv_offsetCache = [];
                    delta = max = 0;
                    custom.forEach(function(idx) {
                            delta += this.columnWidthForContentIndex(idx) - columnWidth;
                            cache[idx + 1] = delta;
                            max = idx;
                        },
                        this);
                    this._schlv_max = max + 1;
                }

                // now just get the delta for the last custom column before the current
                // idx.
                delta = cache[idx];
                if (delta === undefined) {
                    delta = cache[idx] = cache[idx - 1];
                    if (delta === undefined) {
                        max = this._schlv_max;
                        if (idx < max) max = custom.indexBefore(idx) + 1;
                        delta = cache[idx] = cache[max] || 0;
                    }
                }

                ret += delta;
            }

            return ret;
        },

        // ..........................................................
        // SUBCLASS METHODS
        //
        /**
         The layout for a HorizontalListView is computed from the total number of columns
         along with any custom column widths.
         */
        computeLayout: function() {
            // default layout
            var ret = this._schlv_layout;
            if (!ret) ret = this._schlv_layout = {};
            ret.minWidth = this.columnOffsetForContentIndex(this.get('length')) + this.get('leftPadding') + this.get('rightPadding');
            this.set('calculatedWidth', ret.minWidth);
            return ret;
        },

        /**
         Computes the layout for a specific content index by combining the current
         column widths.
         */
        layoutForContentIndex: function(contentIndex) {
            return {
                top: 0,
                bottom: 0,
                left: this.columnOffsetForContentIndex(contentIndex) + this.get('leftPadding'),
                width: this.columnWidthForContentIndex(contentIndex)
            };
        },

        /** @see SC.ListView rowHeightDidChangeForIndexes
         */
        columnWidthDidChangeForIndexes: function(indexes) {
            var len = this.get('length');

            // clear any cached offsets
            this._hlv_widthCache = this._hlv_offsetCache = null;

            // find the smallest index changed; invalidate everything past it
            if (indexes && indexes.isIndexSet) indexes = indexes.get('min');
            this.reload(SC.IndexSet.create(indexes, len-indexes));
            return this;
        },

        /**
         Override to return an IndexSet with the indexes that are at least
         partially visible in the passed rectangle.  This method is used by the
         default implementation of computeNowShowing() to determine the new
         nowShowing range after a scroll.

         Override this method to implement incremental rendering.

         The default simply returns the current content length.

         @param {Rect} rect the visible rect or a point
         @returns {SC.IndexSet} now showing indexes
         */
        contentIndexesInRect: function(rect) {
            var columnWidth = this.get('columnDelegate').get('columnWidth'),
                left = SC.minX(rect),
                right = SC.maxX(rect),
                width = rect.width || 0,
                len = this.get('length'),
                offset,
                start,
                end;

            // estimate the starting column and then get actual offsets until we are
            // right.
            start = (left - (left % columnWidth)) / columnWidth;
            offset = this.columnOffsetForContentIndex(start);

            // go backwards until left of column is before left edge
            while (start > 0 && offset >= left) {
                start--;
                offset -= this.columnWidthForContentIndex(start);
            }

            // go forwards until right of column is after left edge
            offset += this.columnWidthForContentIndex(start);
            while (start < len && offset < left) {
                offset += this.columnWidthForContentIndex(start);
                start++;
            }
            if (start < 0) start = 0;
            if (start >= len) start = len;

            // estimate the final column and then get the actual offsets until we are
            // right. - look at the offset of the _following_ column
            end = start + ((width - (width % columnWidth)) / columnWidth);
            if (end > len) end = len;
            offset = this.columnOffsetForContentIndex(end);

            // walk backwards until left of column is before or at right edge
            while (end >= start && offset >= right) {
                end--;
                offset -= this.columnWidthForContentIndex(end);
            }

            // go forwards until right of column is after right edge
            offset += this.columnWidthForContentIndex(end);
            while (end < len && offset <= right) {
                offset += this.columnWidthForContentIndex(end);
                end++;
            }

            end++; // end should be after start

            if (end < start) end = start;
            if (end > len) end = len;

            // convert to IndexSet and return
            return SC.IndexSet.create(start, end - start);
        },

        /** @private
         Whenever the columnDelegate changes, begin observing important properties
         */
        _hlv_columnDelegateDidChange: function() {
            var last = this._hlv_columnDelegate,
                del  = this.get('columnDelegate'),
                func = this._hlv_columnWidthDidChange,
                func2 = this._hlv_customColumnWidthIndexesDidChange;

            if (last === del) return this; // nothing to do
            this._hlv_columnDelegate = del;

            // last may be null on a new object
            if (last) {
                last.removeObserver('columnWidth', this, func);
                last.removeObserver('customColumnWidthIndexes', this, func2);
            }

            if (!del) {
                throw "Internal Inconsistancy: SC.HorizontalListView must always have CollectionColumnDelegate";
            }

            del.addObserver('columnWidth', this, func);
            del.addObserver('customColumnWidthIndexes', this, func2);
            this._hlv_columnWidthDidChange()._hlv_customColumnWidthIndexesDidChange();
            return this;
        }.observes('columnDelegate'),

        /** @private
         called whenever the columnWidth changes.  If the property actually changed
         then invalidate all column widths.
         */
        _hlv_columnWidthDidChange: function() {
            var del = this.get('columnDelegate'),
                width = del.get('columnWidth'),
                indexes;

            if (width === this._hlv_columnWidth) return this; // nothing to do
            this._hlv_columnWidth = width;

            indexes = SC.IndexSet.create(0, this.get('length'));
            this.columnWidthDidChangeForIndexes(indexes);
            return this ;
        },

        /** @private
         called whenever the customColumnWidthIndexes changes.  If the property
         actually changed then invalidate affected column widths.
         */
        _hlv_customColumnWidthIndexesDidChange: function() {
            var del     = this.get('columnDelegate'),
                indexes = del.get('customColumnWidthIndexes'),
                last    = this._hlv_customColumnWidthIndexes,
                func    = this._hlv_customColumnWidthIndexesContentDidChange;

            // nothing to do
            if ((indexes===last) || (last && last.isEqual(indexes))) return this;

            // if we were observing the last index set, then remove observer
            if (last && this._hlv_isObservingCustomColumnWidthIndexes) {
                last.removeObserver('[]', this, func);
            }

            // only observe new index set if it exists and it is not frozen.
            if (this._hlv_isObservingCustomColumnWidthIndexes = indexes && !indexes.get('isFrozen')) {
                indexes.addObserver('[]', this, func);
            }

            this._hlv_customColumnWidthIndexesContentDidChange();
            return this ;
        },

        /** @private
         Called whenever the customColumnWidthIndexes set is modified.
         */
        _hlv_customColumnWidthIndexesContentDidChange: function() {
            var del     = this.get('rowDelegate'),
                indexes = del.get('customColumnWidthIndexes'),
                last    = this._hlv_customColumnWidthIndexes,
                changed;

            // compute the set to invalidate.  the union of cur and last set
            if (indexes && last) {
                changed = indexes.copy().add(last);
            } else changed = indexes || last ;
            this._hlv_customColumnWidthIndexes = indexes ? indexes.frozenCopy() : null;

            // invalidate
            this.columnWidthDidChangeForIndexes(changed);
            return this ;
        }

    });
