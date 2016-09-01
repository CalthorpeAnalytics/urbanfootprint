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


FootprintSandag.SandagDelegate = Footprint.DefaultDelegate.extend({
    dbEntityKeyToFeatureRecordType: function() {
        return SC.Object.create({
//            scenario_c_boundary: Footprint.SandagScenarioCBoundaryFeature,
//            scenario_b_boundary: Footprint.SandagScenarioBBoundaryFeature,
            '2050_rtp_transit_network': Footprint.Sandag2050RtpTransitNetworkFeature,
            '2050_rtp_transit_stops': Footprint.Sandag2050RtpTransitStopFeature
        }, sc_super())
    }.property('parentDelegate').cacheable()
});
