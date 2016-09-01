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


Footprint.LabelView = SC.LabelView.extend({
  localize: YES,
  // Parameters to pass to the localized string.
  // I don't know why SC.LabelView doesn't have this
  valueParameters: null,

  /**
    The value that will actually be displayed.

    This property is dynamically computed by applying localization,
    string conversion and other normalization utilities.

    @type String
  */
  displayTitle: function() {
    var value, formatter;

    value = this.get('value') ;

    // 1. apply the formatter
    formatter = this.getDelegateProperty('formatter', this.displayDelegate) ;
    if (formatter) {
      var formattedValue = (SC.typeOf(formatter) === SC.T_FUNCTION) ?
          formatter(value, this) : formatter.fieldValueForObject(value, this) ;
      if (!SC.none(formattedValue)) value = formattedValue ;
    }

    // 2. If the returned value is an array, convert items to strings and
    // join with commas.
    if (SC.typeOf(value) === SC.T_ARRAY) {
      var ary = [];
      for(var idx=0, idxLen = value.get('length'); idx< idxLen;idx++) {
        var x = value.objectAt(idx) ;
        if (!SC.none(x) && x.toString) x = x.toString() ;
        ary.push(x) ;
      }
      value = ary.join(',') ;
    }

    // 3. If value is not a string, convert to string. (handles 0)
    if (!SC.none(value) && value.toString) value = value.toString() ;

    // UPDATE from base class
    // 4. Localize
    if (value && this.getDelegateProperty('localize', this.displayDelegate))
      value = SC.String.loc.apply(SC.String.loc, [value].concat(this.get('valueParameters') || []));
    // END Update from base class

    return value;
    // UPDATE, add valueParameters here
  }.property('value', 'localize', 'formatter', 'valueParameters').cacheable(),
})
