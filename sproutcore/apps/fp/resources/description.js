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



function createDescription() {
    var description = "Neque porro quisquam est, qui doLorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam hendrerit sagittis eros sagittis suscipit. In orci dolor, rutrum sed faucibus nec, rhoncus id nibh. Vivamus tristique mattis venenatis. Curabitur in eros odio. Aenean vel nibh iaculis, faucibus justo at, suscipit turpis. Sed lacinia urna non risus tempus blandit.";


    d3.select('.descriptionBlock')
        .text(description);
}
