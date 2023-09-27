-- Enable PostGIS extension if not already enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- Type Definitions
CREATE TYPE DERIVED_PRODUCT AS ENUM ('DEM', 'DSM', 'CHM');
CREATE TYPE PROCESSING_STATUS AS ENUM ('Raw', 'Adjusted', 'Classified', 'QualityControlled', 'Accepted', 'Rejected');


-- Create the schema for the ECLIPSE project
--
-- Create the NASbox table
CREATE TABLE NASbox (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  location VARCHAR(255) NOT NULL,
  IPv4_addr VARCHAR(255) NOT NULL
);

-- Create the SpatialReference table
CREATE TABLE SpatialReference (
  epsg_code INTEGER PRIMARY KEY,
  sr_name VARCHAR(255) NOT NULL,
  description VARCHAR(255)
);

-- Create the Epoch table
CREATE TABLE Epoch (
  id SERIAL PRIMARY KEY,
  epoch_year INTEGER,
  description VARCHAR(255),
  spatial_ref_id INTEGER REFERENCES SpatialReference(id)
);

-- UTMZone
CREATE TABLE UTMZone (
    zone_number INTEGER PRIMARY KEY,
    spatial_ref_id INTEGER REFERENCES SpatialReference(id)
);

-- Create the BCGS20kGrid table
CREATE TABLE BCGS2500kGrid (,
  grid_code_2500k VARCHAR(11) PRIMARY KEY,
  grid_geometry GEOGRAPHY NOT NULL,
  grid_20k_id INTEGER REFERENCES BCGS20kGrid(id),
  lidar_file_id INTEGER REFERENCES LidarFile(id),
  spatial_ref_id INTEGER REFERENCES SpatialReference(id)
);

-- Create the BCGS20kGrid table
CREATE TABLE BCGS20kGrid (
  grid_code_20k CHAR(8) PRIMARY KEY,
  grid_geometry GEOGRAPHY NOT NULL,
  priority INTEGER
  spatial_ref_id INTEGER REFERENCES SpatialReference(id)
);

-- Create the Drive table
CREATE TABLE Drive (
  id SERIAL PRIMARY KEY,
  receiver_name VARCHAR(255) NOT NULL,
  serial_number VARCHAR(255) NOT NULL,
  nas_id INTEGER REFERENCES NASbox(id)
  delivery_id INTEGER REFERENCES Delivery(id)
);

-- Create the Delivery table
CREATE TABLE Delivery (
  id SERIAL PRIMARY KEY,
  coverage GEOGRAPHY NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  drive_id INTEGER REFERENCES Drive(id),
  nas_id INTEGER REFERENCES NASbox(id)
);

-- Create the LidarFile table
CREATE TABLE LidarFile (
  id SERIAL PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  bounding_box GEOGRAPHY NOT NULL,
  nas_id INTEGER REFERENCES NASbox(id),
  delivery_id INTEGER REFERENCES Delivery(id),
  grid_2500k_id INTEGER REFERENCES BCGS2500kGrid(id),
);

-- Create the DerivedProduct table
CREATE TABLE DerivedProductFile (
  id SERIAL PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  type DERIVED_PRODUCT,
  grid20k_id INTEGER REFERENCES BCGS20kGrid(id),
  nas_id INTEGER REFERENCES NASbox(id)
);

-- Create the ProcessingStatus table
CREATE TABLE ProcessingStatus (
  id SERIAL PRIMARY KEY,
  status PROCESSING_STATUS,
  updated_by VARCHAR(255), -- !
  comments VARCHAR(255), -- !
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  file_id INTEGER REFERENCES LidarFile(id),
);

-- Create the ControlPoint table
CREATE TABLE ControlPoint (
  id SERIAL PRIMARY KEY,
  point_name VARCHAR(255),
  point_geometry GEOMETRY,
  spatial_ref_id INTEGER REFERENCES SpatialReference(id)
  delivery_id INTEGER REFERENCES Delivery(id)
);
