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


sc_require('views/info_views/style_picker_view');

Footprint.BuiltFormStylePickerView = Footprint.StylePickerView.extend({
    // The BuiltForm
    content: null,
    // The BuiltForm has a convenient computed property to access the id Style
    styleBinding: SC.Binding.oneWay('*content.idStyle'),
    // Editing of BuiltForms is disabled
    isEnabled: NO,
    // isEnabledBinding: SC.Binding.oneWay('.style').bool(),
    isVisibleBinding: SC.Binding.oneWay('.isEnabled').bool()
});
