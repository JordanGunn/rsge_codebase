
-- Populate the SpatialReference table
INSERT INTO SpatialReference (epsg_code, sr_name, description) VALUES
  (4326, 'WGS 84', 'World Geodetic System 1984'),
  (3005, 'BC Albers (CSRS)', 'British Columbia Albers Equal Area Conic Projection'),
  (3153, 'BC Albers (CSRS)', 'British Columbia Albers Equal Area Conic Projection'),
  (3154, 'NAD83(CSRS) / UTM zone 7N', 'North American Datum 1983, Canadian Spatial Reference System, UTM Zone 7 North'),
  (3155, 'NAD83(CSRS) / UTM zone 8N', 'North American Datum 1983, Canadian Spatial Reference System, UTM Zone 8 North'),
  (3156, 'NAD83(CSRS) / UTM zone 9N', 'North American Datum 1983, Canadian Spatial Reference System, UTM Zone 9 North'),
  (3157, 'NAD83(CSRS) / UTM zone 10N', 'North American Datum 1983, Canadian Spatial Reference System, UTM Zone 10 North'),
  (2955, 'NAD83(CSRS) / UTM zone 11N', 'North American Datum 1983, Canadian Spatial Reference System, UTM Zone 11 North')
ON CONFLICT (epsg_code) DO NOTHING;
--

-- Populate the UTMZone table
INSERT INTO UTMZone (zone_number, epsg_code) VALUES
  (7, 3154),
  (8, 3155),
  (9, 3156),
  (10, 3157),
  (11, 2955)
ON CONFLICT (zone_number) DO NOTHING;
--

-- Populate the Epoch table
INSERT INTO Epoch (epoch_year, description, epsg_code) VALUES
  (2002, 'BC Lower Mainland / UTM Zone 7', 3154),
  (2002, 'BC Lower Mainland / UTM Zone 8', 3155),
  (2002, 'BC Lower Mainland / UTM Zone 9', 3156),
  (2002, 'BC Lower Mainland / UTM Zone 10', 3157),
  (1997, 'BC Vancouver Island / UTM Zone 9', 3156),
  (1997, 'BC Vancouver Island / UTM Zone 10', 3157),
  (2002, 'BC Lower Mainland / UTM Zone 11', 2955);
--

-- Populate the NASbox table for demonstration (Optional)
INSERT INTO NASbox (name, location, IPv4_addr) VALUES
  ('Vader', 'Koraleys Cubicle', '142.36.252.188'),
  ('Revan', 'Scanning Room (Basement)', '127.0.0.1');
--
