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

// SC.Store (for autonomous nested stores)
SC.Store.reopen({
  chainAutonomousStore: function(attrs, newStoreClass) {
    var newAttrs = attrs ? SC.clone( attrs ) : {};
    var source  = this._getDataSource();

    newAttrs.dataSource = source;
    return this.chain( newAttrs, newStoreClass );
  }
});

// SC.NestedStore (for autonomous nested stores)
SC.NestedStore.reopen({
  chainAutonomousStore: function(attrs, newStoreClass) {
    throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  },
  commitRecords: function(recordTypes, ids, storeKeys) {
    if( this.get( "dataSource" ) )
      return sc_super();
    else
      throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  },
  commitRecord: function(recordType, id, storeKey) {
    if( this.get( "dataSource" ) )
      return sc_super();
    else
      throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  },
  cancelRecords: function(recordTypes, ids, storeKeys) {
    if( this.get( "dataSource" ) )
      return sc_super();
    else
      throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  },
  cancelRecord: function(recordType, id, storeKey) {
    if( this.get( "dataSource" ) )
      return sc_super();
    else
      throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  },
  dataSourceDidCancel: function(storeKey) {
    if( this.get( "dataSource" ) )
      return sc_super();
    else
      throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  },
  dataSourceDidComplete: function(storeKey, dataHash, newId) {
    if( this.get( "dataSource" ) )
      return sc_super();
    else
      throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  },
  dataSourceDidDestroy: function(storeKey) {
    if( this.get( "dataSource" ) )
      return sc_super();
    else
      throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  },
  dataSourceDidError: function(storeKey, error) {
    if( this.get( "dataSource" ) )
      return sc_super();
    else
      throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  },
  pushRetrieve: function(recordType, id, dataHash, storeKey) {
    if( this.get( "dataSource" ) )
      return sc_super();
    else
      throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  },
  pushDestroy: function(recordType, id, storeKey) {
    if( this.get( "dataSource" ) )
      return sc_super();
    else
      throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  },
  pushError: function(recordType, id, error, storeKey) {
    if( this.get( "dataSource" ) )
      return sc_super();
    else
      throw SC.Store.NESTED_STORE_UNSUPPORTED_ERROR;
  }

});
