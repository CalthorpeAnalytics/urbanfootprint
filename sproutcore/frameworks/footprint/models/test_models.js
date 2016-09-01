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

// Space to test modeling framework

 Footprint.Foo = Footprint.ChildRecord.extend(
 {
     name: SC.Record.attr('String')
 });

 Footprint.Bar = Footprint.ChildRecord.extend(
 {
     name: SC.Record.attr('String')
 });

 Footprint.FooBar = Footprint.Record.extend({
     name: SC.Record.attr('String'),
     foo: SC.Record.toOne('Footprint.Foo', {
         nested: true
     }),
     bar: SC.Record.toOne('Footprint.Bar', {
         nested: true
     })
 });
