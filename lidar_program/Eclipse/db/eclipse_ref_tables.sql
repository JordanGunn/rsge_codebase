-- Populate the SpatialReference table
INSERT INTO SpatialReference (epsg_code, sr_name, description) VALUES
  (4326, 'WGS 84', 'World Geodetic System 1984'),
  (3005, 'BC Albers (CSRS)', 'British Columbia Albers Equal Area Conic Projection'),
  (3153, 'BC Albers (CSRS)', 'British Columbia Albers Equal Area Conic Projection'),
  (3154, 'NAD83(CSRS) / UTM zone 7N', 'North American Datum 1983, Canadian Spatial Reference System, UTM Zone 7 North'),
  (3155, 'NAD83(CSRS) / UTM zone 8N', 'North American Datum 1983, Canadian Spatial Reference System, UTM Zone 8 North'),
  (3156, 'NAD83(CSRS) / UTM zone 9N', 'North American Datum 1983, Canadian Spatial Reference System, UTM Zone 9 North'),
  (3157, 'NAD83(CSRS) / UTM zone 10N', 'North American Datum 1983, Canadian Spatial Reference System, UTM Zone 10 North'),
  (2955, 'NAD83(CSRS) / UTM zone 11N', 'North American Datum 1983, Canadian Spatial Reference System, UTM Zone 11 North');


-- Populate the UTMZone table
INSERT INTO UTMZone (zone_number, spatial_ref_id) VALUES
  (7, 4), -- 1
  (8, 5),
  (9, 6),
  (10, 7),
  (11, 8); -- 5

-- Populate the Epoch table
INSERT INTO Epoch (epoch_year, description, spatial_ref_id) VALUES
  (2002, 'BC Lower Mainland / UTM Zone 7', 4),
  (2002, 'BC Lower Mainland / UTM Zone 8', 5),
  (2002, 'BC Lower Mainland / UTM Zone 9', 6),
  (2002, 'BC Lower Mainland / UTM Zone 10', 7),
  (1997, 'BC Vancouver Island / UTM Zone 9', 6),
  (1997, 'BC Vancouver Island / UTM Zone 10', 7),
  (2002, 'BC Lower Mainland / UTM Zone 11', 8);

-- Populate the NASbox table for demonstration (Optional)
INSERT INTO NASbox (name, location, IPv4_addr) VALUES
  ('NAS1', 'Koraley Cubicle', '127.0.0.1'),
  ('NAS2', 'Scanning Room (Basement)', '127.0.0.1');


-- Populate the ProcessingStatusReference table
INSERT INTO ProcessingStatusReference (status, description) VALUES
  ('Raw', 'Raw data, not yet processed'),
  ('Adjusted', 'Strips calibrated and adjusted'),
  ('Classified', 'Data has been fully classified'),
  ('QualityControlled', 'Passed quality controls'),
  ('Accepted', 'Data has been accepted (Passed QC)'),
  ('Rejected', 'Data has been rejected');


-- Insert into a table with a Geometry column, specifying the SRID
-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
-- INSERT INTO some_table (geom_column) VALUES (ST_SetSRID(ST_GeomFromText('POINT(0 0)'), 4326));


-- You can also populate other tables as needed
-- Populate BCGS2500kGrid with mock data (assuming you'll fill in real grid_geometry data later)
INSERT INTO BCGS2500kGrid (grid_code_2500k, grid_geometry, spatial_ref_id) VALUES
  ('2500k_01', ST_GeogFromText('POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'), 1),
  ('2500k_02', ST_GeogFromText('POLYGON((1 1, 1 2, 2 2, 2 1, 1 1))'), 1);

-- Populate BCGS20kGrid with mock data (assuming you'll fill in real grid_geometry data later)
INSERT INTO BCGS20kGrid (grid_code_20k, grid_geometry, priority, spatial_ref_id) VALUES
  ('20k_01', ST_GeogFromText('POLYGON((2 2, 2 3, 3 3, 3 2, 2 2))'), 1, 1),
  ('20k_02', ST_GeogFromText('POLYGON((3 3, 3 4, 4 4, 4 3, 3 3))'), 2, 1);

-- Populate ProcessingStatus with predefined ENUM values
-- This should be automatically populated as we're using ENUMs for status. If you want to add additional metadata for each status, consider adding another column for that.


