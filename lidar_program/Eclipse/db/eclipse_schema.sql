-- Enable PostGIS extension if not already enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- Type Definitions
CREATE TYPE DERIVED_PRODUCT AS ENUM ('DEM', 'DSM', 'CHM');
CREATE TYPE PROCESSING_STATUS AS ENUM ('Raw', 'Adjusted', 'Classified', 'QualityControlled', 'Accepted', 'Rejected');

-- Create the schema for the ECLIPSE project
--
-- Create the NASbox table
CREATE TABLE IF NOT EXISTS NASBox (
  id SERIAL PRIMARY KEY,
  name VARCHAR(20) NOT NULL,
  location VARCHAR(255) NOT NULL,
  IPv4_addr VARCHAR(15) NOT NULL
);

-- Create SpatialReference table with epsg_code as primary key
CREATE TABLE IF NOT EXISTS SpatialReference (
  epsg_code INTEGER PRIMARY KEY,
  sr_name VARCHAR(255) NOT NULL,
  description TEXT
);

-- Create Epoch table with epoch_year as primary key
CREATE TABLE IF NOT EXISTS Epoch (
  id SERIAL PRIMARY KEY,
  epoch_year INTEGER,
  description TEXT,
  spatial_ref_id INTEGER REFERENCES SpatialReference(epsg_code)
);

-- Create UTMZone table with zone_number as primary key
CREATE TABLE IF NOT EXISTS UTMZone (
  zone_number INTEGER PRIMARY KEY,
  spatial_ref_id INTEGER REFERENCES SpatialReference(epsg_code)
);

-- Create BCGS20K table with tile_20K as primary key
CREATE TABLE IF NOT EXISTS BCGS20K (
  tile_20K VARCHAR(20) PRIMARY KEY,
  priority BOOLEAN,
  geometry GEOGRAPHY,
  epsg_code INTEGER REFERENCES SpatialReference(epsg_code)
);

-- Create the BCGS2500K table
CREATE TABLE IF NOT EXISTS BCGS2500k (,
  tile_2500k VARCHAR(20) PRIMARY KEY,
  grid_geometry GEOGRAPHY NOT NULL,
  tile_20K INTEGER REFERENCES BCGS20K(tile_20K),
  lidar_file_id INTEGER REFERENCES LidarFile(id),
  epsg_code INTEGER REFERENCES SpatialReference(epsg_code)
);

-- Create the Drive table
CREATE TABLE IF NOT EXISTS Drive (
  id SERIAL PRIMARY KEY,
  receiver_name VARCHAR(255) NOT NULL,
  serial_number VARCHAR(255) NOT NULL,
  nas_id INTEGER REFERENCES NASBox(id),
  delivery_id INTEGER REFERENCES Delivery(id)
);

-- Create the Delivery table
CREATE TABLE IF NOT EXISTS Delivery (
  id SERIAL PRIMARY KEY,
  coverage GEOGRAPHY NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  drive_id INTEGER REFERENCES Drive(id),
  nas_id INTEGER REFERENCES NASBox(id)
);

-- Create the LidarFile table
CREATE TABLE IF NOT EXISTS LidarFile (
  id SERIAL PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  bounding_box GEOGRAPHY NOT NULL,
  nas_id INTEGER REFERENCES NASBox(id),
  delivery_id INTEGER REFERENCES Delivery(id),
  tile_2500k INTEGER REFERENCES BCGS2500K(tile_2500k),
);

-- Create the ProcessingStatus table
CREATE TABLE IF NOT EXISTS ProcessingStatus (
  id SERIAL PRIMARY KEY,
  status PROCESSING_STATUS,
  updated_by VARCHAR(255), -- !
  comments VARCHAR(255), -- !
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  file_id INTEGER REFERENCES LidarFile(id),
);

-- Create the ControlPoint table
CREATE TABLE IF NOT EXISTS ControlPoint (
  id SERIAL PRIMARY KEY,
  point_name VARCHAR(255),
  point_geometry GEOMETRY,
  delivery_id INTEGER REFERENCES Delivery(id),
  epsg_code INTEGER REFERENCES SpatialReference(epsg_code)
);
