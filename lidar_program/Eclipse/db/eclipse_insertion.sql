-- post-import cleanup to tables

-- Drop gid and existing primary key constraint for 2500k
ALTER TABLE BCGS2500k DROP CONSTRAINT bcgs2500k_pkey CASCADE;
ALTER TABLE BCGS2500k DROP COLUMN gid;

-- Set new primary key for 2500k
ALTER TABLE BCGS2500k ADD PRIMARY KEY (tile_2500k);

-- Drop gid and existing primary key constraint for 20k
ALTER TABLE BCGS20k DROP CONSTRAINT bcgs20k_pkey CASCADE;
ALTER TABLE BCGS20k DROP COLUMN gid;

-- Set new primary key for 20k
ALTER TABLE BCGS20k ADD PRIMARY KEY (tile_20k);

-- Cleanup unwanted columns
-- -- 2500k cleanup
ALTER TABLE BCGS2500k
  DROP COLUMN mptldsplnm,
  DROP COLUMN fcode,
  DROP COLUMN objectid,
  DROP COLUMN area_sqm,
  DROP COLUMN feat_len;

-- -- 20k cleanup
ALTER TABLE BCGS20k
  DROP COLUMN fcode,
  DROP COLUMN objectid,
  DROP COLUMN map_name,
  DROP COLUMN area_sqm,
  DROP COLUMN feat_len;

-- Add any additional columns
ALTER TABLE BCGS2500k ADD COLUMN tile_20k VARCHAR(20);

-- Add 20K values to 2500k reference table
-- Update the tile_20K field in BCGS2500k based on tile_2500k
UPDATE BCGS2500k
SET tile_20K = SUBSTRING(tile_2500k FROM 1 FOR 7)
WHERE tile_20K IS NULL;

-- Update foreign key and NOT NULL constraints in 2500k ref table
ALTER TABLE BCGS2500k ALTER COLUMN tile_20k SET NOT NULL;
ALTER TABLE BCGS2500k ADD CONSTRAINT fk_tile_20k FOREIGN KEY (tile_20k) REFERENCES BCGS20k(tile_20k);
