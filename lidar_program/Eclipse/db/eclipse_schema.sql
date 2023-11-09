-- Enable PostGIS extension if not already enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- TYPE DEFINITIONS
--
-- derived product enum
DO $$ BEGIN -- Create type if it doesn't already exist
    CREATE TYPE DERIVED_PRODUCT AS ENUM (
      'DEM', 'DSM', 'CHM'
    );
EXCEPTION
    WHEN DUPLICATE_OBJECT THEN NULL;
END $$;

-- Processing Status enum
DO $$ BEGIN -- Create type if it doesn't alredy exist
    CREATE TYPE PROCESSING_STATUS AS ENUM (
      'Raw', 'Adjusted', 'Classified',
      'QualityControlled', 'Accepted', 'Rejected'
    );
EXCEPTION
    WHEN DUPLICATE_OBJECT THEN NULL;
END $$;


-- CREATE TABLES
--
-- Create the NASbox table
CREATE TABLE IF NOT EXISTS NASBox (
  id SERIAL PRIMARY KEY,
  name VARCHAR(20) NOT NULL,
  location VARCHAR(255) NOT NULL,
  capacity_gb NUMERIC(4, 2) NOT NULL,
  IPv4_addr VARCHAR(15) NOT NULL
);

-- Create SpatialReference table with epsg_code as primary key
CREATE TABLE IF NOT EXISTS SpatialReference (
  epsg_code INTEGER PRIMARY KEY,
  proj_name VARCHAR(255) NOT NULL,
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

-- Create the Delivery table
CREATE TABLE IF NOT EXISTS Delivery (
  id SERIAL PRIMARY KEY,
  receiver_name VARCHAR(255),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the LidarFile table
CREATE TABLE IF NOT EXISTS Lidar (
  id SERIAL PRIMARY KEY,
  file_name VARCHAR(255),
  file_path VARCHAR(255),
  file_size VARCHAR(255),
  x_min NUMERIC(10, 3),
  x_max NUMERIC(10, 3),
  y_min NUMERIC(10, 3),
  y_max NUMERIC(10, 3),
  lidar_type CHAR,
  version REAL,
  epsg_code INTEGER REFERENCES SpatialReference(epsg_code),
  nas_id INTEGER REFERENCES NASBox(id),
  delivery_id INTEGER REFERENCES Delivery(id)
);

-- Create the LidarClassified table
-- -- tile_2500k reference added in 'eclipse_insertion.sql' script
CREATE TABLE IF NOT EXISTS LidarClassified (
  id SERIAL PRIMARY KEY REFERENCES Lidar(id),
  bounding_box POLYGON
);

-- Create the LidarRaw table
CREATE TABLE IF NOT EXISTS LidarRaw (
  id SERIAL PRIMARY KEY REFERENCES Lidar(id),
  convex_hull POLYGON,
  file_source_id INTEGER
);

-- Create the DerivedProduct table
-- -- tile_20k reference added in 'eclipse_insertion.sql' script
CREATE TABLE IF NOT EXISTS DerivedProduct (
  id SERIAL PRIMARY KEY,
  derived_product_type DERIVED_PRODUCT,
  file_name VARCHAR(255),
  file_path VARCHAR(255),
  file_size VARCHAR(255),
  x_min NUMERIC(10, 3),
  x_max NUMERIC(10, 3),
  y_min NUMERIC(10, 3),
  y_max NUMERIC(10, 3),
  bounding_box POLYGON,
  epsg_code INTEGER REFERENCES SpatialReference(epsg_code),
  nas_id INTEGER REFERENCES NASBox(id)
);

-- Create the Drive table
CREATE TABLE IF NOT EXISTS Drive (
  id SERIAL PRIMARY KEY,
  serial_number VARCHAR(255) NOT NULL,
  storage_total_gb NUMERIC(4, 2) NOT NULL,
  storage_used_gb NUMERIC(4, 2) NOT NULL,
  file_count INTEGER,
  nas_id INTEGER REFERENCES NASBox(id),
  delivery_id INTEGER REFERENCES Delivery(id)
);

-- Create the ProcessingStatus table
CREATE TABLE IF NOT EXISTS ProcessingStatus (
  id SERIAL PRIMARY KEY,
  status PROCESSING_STATUS,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed_by VARCHAR(255), -- !
  comments VARCHAR(255), -- !
  lidar_id INTEGER REFERENCES Lidar(id)
);

-- Create the ControlPoint table
--CREATE TABLE IF NOT EXISTS ControlPoint (
--  id SERIAL PRIMARY KEY,
--  point_name VARCHAR(255),
--  point_geometry POINT,
--  delivery_id INTEGER REFERENCES Delivery(id),
--  epsg_code INTEGER REFERENCES SpatialReference(epsg_code)
--);
