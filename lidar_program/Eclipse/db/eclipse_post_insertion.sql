
-- Add 20K foreign keys to ref table
INSERT INTO BCGS2500K (grid_code_20K)
SELECT grid_code_2500K, SUBSTRING(grid_code_2500K FROM 1 FOR 7),
FROM BCGS2500K;
