--
-- UrbanFootprint v1.5
-- Copyright (C) 2017 Calthorpe Analytics
--
-- This file is part of UrbanFootprint version 1.5
--
-- UrbanFootprint is distributed under the terms of the GNU General
-- Public License version 3, as published by the Free Software Foundation. This
-- code is distributed WITHOUT ANY WARRANTY, without implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
-- Public License v3 for more details; see <http://www.gnu.org/licenses/>.
--
--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = irvine_datasets, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: scag_2012_landuse_codes; Type: TABLE; Schema: irvine_datasets; Owner: calthorpe; Tablespace:
--

CREATE TABLE scag_2012_landuse_codes (
    landuse_id integer,
    landuse_description character varying,
    landuse_type character varying
);


ALTER TABLE irvine_datasets.scag_2012_landuse_codes OWNER TO calthorpe;

--
-- Data for Name: scag_2012_landuse_codes; Type: TABLE DATA; Schema: irvine_datasets; Owner: calthorpe
--

COPY scag_2012_landuse_codes (landuse_id, landuse_description, landuse_type) FROM stdin;
1000	Urban or Built-Up	Urban or Built-Up
1100	Residential	Mixed Residential
1110	Single Family Residential	Single Family Residential
1111	High-Density Single Family Residential	Single Family Residential
1112	Low-Density Single Family Residential	Single Family Residential
1113	Rural Residential	Single Family Residential
1120	Multi-Family Residential (Medium-High Density Residential) 	Multi-Family Residential
1121	Mixed Multi-Family Residential	Multi-Family Residential
1122	Duplexes, Triplexes and 2- or 3-Unit Condominiums and Townhouses 	Multi-Family Residential
1123	Low-Rise Apartments, Condominiums, and Townhouses	Multi-Family Residential
1124	Medium-Rise Apartments and Condominiums 	Multi-Family Residential
1125	High-Rise Apartments and Condominiums 	Multi-Family Residential
1130	Mobile Homes and Trailer Parks	Mobile Homes and Trailer Parks
1131	Trailer Parks and Mobile Home Courts, High-Density	Mobile Homes and Trailer Parks
1132	Mobile Home Courts and Subdivisions, Low-Density	Mobile Homes and Trailer Parks
1140	Mixed Residential (single and multiple residential)	Mixed Residential
1200	Commercial and Services	Commercial and Services
1210	General Office Use	General Office
1211	Low- and Medium-Rise Major Office Use	General Office
1212	High-Rise Major Office Use	General Office
1213	Skyscrapers	General Office
1220	Retail Stores and Commercial Services	Commercial and Services
1221	Regional Shopping Center	Commercial and Services
1222	Retail Centers (Non-Strip With Contiguous Interconnected Off-Street Parking)	Commercial and Services
1223	Retail Strip Development	Commercial and Services
1230	Other Commercial	Commercial and Services
1231	Commercial Storage	Commercial and Services
1232	Commercial Recreation	Commercial and Services
1233	Hotels and Motels	Commercial and Services
1240	Public Facilities	Facilities
1241	Government Offices	Facilities
1242	Police and Sheriff Stations	Facilities
1243	Fire Stations	Facilities
1244	Major Medical Health Care Facilities	Facilities
1245	Religious Facilities	Facilities
1246	Other Public Facilities	Facilities
1247	Public Parking Facilities	Facilities
1250	Special Use Facilities	Facilities
1251	Correctional Facilities	Facilities
1252	Special Care Facilities	Facilities
1253	Other Special Use Facilities	Facilities
1260	Educational Institutions	Education
1261	Pre-Schools/Day Care Centers	Education
1262	Elementary Schools	Education
1263	Junior or Intermediate High Schools	Education
1264	Senior High Schools	Education
1265	Colleges and Universities	Education
1266	Trade Schools and Professional Training Facilities	Education
1270	Military Installations	Military Installations
1271	Base (Built-up Area)	Military Installations
1272	Vacant Area	Military Installations
1273	Air Field	Military Installations
1274	Former Base (Built-up Area)	Military Installations
1275	Former Base Vacant Area	Military Installations
1276	Former Base Air Field	Military Installations
1300	Industrial	Industrial
1310	Light Industrial	Industrial
1311	Manufacturing, Assembly, and Industrial Services	Industrial
1312	Picture and Television Production Lots	Industrial
1313	Packing Houses and Grain Elevators	Industrial
1314	Research and Development	Industrial
1320	Heavy Industrial	Industrial
1321	Manufacturing	Industrial
1322	Petroleum Refining and Processing	Industrial
1323	Open Storage	Industrial
1324	Major Metal Processing	Industrial
1325	Chemical Processing	Industrial
1330	Extraction	Industrial
1331	Mineral Extraction - Other Than Oil and Gas	Industrial
1332	Mineral Extraction - Oil and Gas	Industrial
1340	Wholesaling and Warehousing	Industrial
1400	Transportation, Communications, and Utilities	Transportation, Communications, and Utilities
1410	Transportation	Transportation, Communications, and Utilities
1411	Airports	Transportation, Communications, and Utilities
1412	Railroads	Transportation, Communications, and Utilities
1413	Freeways and Major Roads	Transportation, Communications, and Utilities
1414	Carpool and Rideshare Facilities	Transportation, Communications, and Utilities
1415	Bus Terminals and Transit Centers	Transportation, Communications, and Utilities
1416	Truck Terminals	Transportation, Communications, and Utilities
1417	Harbor Facilities	Transportation, Communications, and Utilities
1418	Navigation Aids	Transportation, Communications, and Utilities
1420	Communication Facilities	Transportation, Communications, and Utilities
1430	Utility Facilities	Transportation, Communications, and Utilities
1431	Electrical Power Facilities	Transportation, Communications, and Utilities
1432	Solid Waste Disposal Facilities	Transportation, Communications, and Utilities
1433	Liquid Waste Disposal Facilities	Transportation, Communications, and Utilities
1434	Water Storage Facilities	Transportation, Communications, and Utilities
1435	Natural Gas and Petroleum Facilities	Transportation, Communications, and Utilities
1436	Water Transfer Facilities 	Transportation, Communications, and Utilities
1437	Improved Flood Waterways and Structures	Transportation, Communications, and Utilities
1438	Mixed Utilities	Transportation, Communications, and Utilities
1440	Maintenance Yards 	Transportation, Communications, and Utilities
1441	Bus Yards	Transportation, Communications, and Utilities
1442	Rail Yards	Transportation, Communications, and Utilities
1450	Mixed Transportation	Transportation, Communications, and Utilities
1460	Mixed Transportation and Utility	Transportation, Communications, and Utilities
1500	Mixed Commercial and Industrial	Mixed Commercial and Industrial
1600	Mixed Residential and Commercial Services	Mixed Residential and Commercial
1700	Under Construction	Under Construction
1800	Open Space and Recreation	Open Space and Recreation
1810	Golf Courses 	Open Space and Recreation
1820	Local Parks and Recreation	Open Space and Recreation
1830	State and National Parks and Recreation	Open Space and Recreation
1840	Cemeteries	Open Space and Recreation
1850	Wildlife Preserves and Sanctuaries	Open Space and Recreation
1860	Specimen Gardens and Arboreta	Open Space and Recreation
1870	Beach Parks 	Open Space and Recreation
1880	Other Open Space and Recreation 	Open Space and Recreation
1900	Urban Vacant (developable)	Vacant
2000	Agriculture	Agriculture
2100	Cropland and Improved Pasture Land	Agriculture
2110	Irrigated Cropland and Improved Pasture Land	Agriculture
2120	Non-Irrigated Cropland and Improved Pasture Land	Agriculture
2200	Orchards and Vineyards	Agriculture
2300	Nurseries	Agriculture
2400	Dairy, Intensive Livestock, and Associated Facilities	Agriculture
2500	Poultry Operations	Agriculture
2600	Other Agriculture	Agriculture
2700	Horse Ranches	Agriculture
3000	Vacant (developable)	Vacant
3100	Vacant Undifferentiated	Vacant
3200	Abandoned Orchards and Vineyards	Vacant
3300	Vacant With Limited Improvements	Vacant
3400	Beaches (vacant)	Vacant
4000	Water	Water
4100	Water, Undifferentiated	Water
4200	Harbor Water Facilities	Water
4300	Marina Water Facilities	Water
4400	Water Within a Military Installation	Water
4500	Area of Inundation (High Water) (1990 Database only)	Water
8888	Undevelopable or protected Land 	Undevelopable or Protected Land
9999	No Photo Coverage/Not in Update Study Area	Unknown
\.


--
-- PostgreSQL database dump complete
--
