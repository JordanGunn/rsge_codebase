
-- Enable PostGIS extension if not already enabled
CREATE EXTENSION IF NOT EXISTS postgis;


-- TYPE DEFINITIONS
-- derived product enum
DO $$ BEGIN -- Create type if it doesn't alredy exist
    CREATE TYPE DERIVED_PRODUCT AS ENUM ('DEM', 'DSM', 'CHM');
EXCEPTION
    WHEN DUPLICATE_OBJECT THEN NULL;
END $$;
-- Processing Status enum
DO $$ BEGIN -- Create type if it doesn't alredy exist
    CREATE TYPE PROCESSING_STATUS AS ENUM ('Raw', 'Adjusted', 'Classified', 'QualityControlled', 'Accepted', 'Rejected');
EXCEPTION
    WHEN DUPLICATE_OBJECT THEN NULL;
END $$;


-- CREATE TABLES
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
  epsg_code INTEGER REFERENCES SpatialReference(epsg_code)
);

-- Create UTMZone table with zone_number as primary key
CREATE TABLE IF NOT EXISTS UTMZone (
  zone_number INTEGER PRIMARY KEY,
  epsg_code INTEGER REFERENCES SpatialReference(epsg_code)
);

---- Create BCGS20k table with tile_20k as primary key
--CREATE TABLE IF NOT EXISTS BCGS20k (
--  tile_20k VARCHAR(20) PRIMARY KEY,
--  priority BOOLEAN,
--  geometry GEOGRAPHY,
--  epsg_code INTEGER REFERENCES SpatialReference(epsg_code)
--);

-- Create the Delivery table
CREATE TABLE IF NOT EXISTS Delivery (
  id SERIAL PRIMARY KEY,
  coverage GEOGRAPHY NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  nas_id INTEGER REFERENCES NASBox(id)
);

-- Create the LidarFile table
CREATE TABLE IF NOT EXISTS LidarFile (
  id SERIAL PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  bounding_box GEOGRAPHY NOT NULL,
  nas_id INTEGER REFERENCES NASBox(id),
  delivery_id INTEGER REFERENCES Delivery(id)
);

-- Create the LidarFile table
CREATE TABLE IF NOT EXISTS DerivedProductFile (
  id SERIAL PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  derived_product DERIVED_PRODUCT,
  bounding_box GEOGRAPHY NOT NULL,
  nas_id INTEGER REFERENCES NASBox(id)
);


---- Create the BCGS2500k table
--CREATE TABLE IF NOT EXISTS BCGS2500k (
--  tile_2500k VARCHAR(20) PRIMARY KEY,
--  grid_geometry GEOGRAPHY NOT NULL,
--  tile_20k VARCHAR(20) REFERENCES BCGS20k(tile_20k),
--  lidar_file_id INTEGER REFERENCES LidarFile(id),
--  epsg_code INTEGER REFERENCES SpatialReference(epsg_code)
--);

-- Create the Drive table
CREATE TABLE IF NOT EXISTS Drive (
  id SERIAL PRIMARY KEY,
  receiver_name VARCHAR(255) NOT NULL,
  serial_number VARCHAR(255) NOT NULL,
  nas_id INTEGER REFERENCES NASBox(id),
  delivery_id INTEGER REFERENCES Delivery(id)
);

-- Create the ProcessingStatus table
CREATE TABLE IF NOT EXISTS ProcessingStatus (
  id SERIAL PRIMARY KEY,
  status PROCESSING_STATUS,
  updated_by VARCHAR(255), -- !
  comments VARCHAR(255), -- !
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  lidar_file_id INTEGER REFERENCES LidarFile(id)
);

-- Create the ControlPoint table
CREATE TABLE IF NOT EXISTS ControlPoint (
  id SERIAL PRIMARY KEY,
  point_name VARCHAR(255),
  point_geometry GEOMETRY,
  delivery_id INTEGER REFERENCES Delivery(id),
  epsg_code INTEGER REFERENCES SpatialReference(epsg_code)
);
