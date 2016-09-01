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
// Project:   FootprintSandag
// ==========================================================================
/*globals FootprintSandag */

/** @namespace

  My cool new framework.  Describe your framework.

  @extends SC.Object
*/
window.FootprintSandag = SC.Object.create(
  /** @scope FootprintSandag.prototype */ {

  NAMESPACE: 'FootprintSandag',
  VERSION: '0.1.0',

  logoPath: sc_static('images/logo.png'),

  STATIC: sc_static('images/logo.png').replace('images/logo.png', '%@')

});
