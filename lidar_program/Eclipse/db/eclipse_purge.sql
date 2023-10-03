-- DROP ALL TABLES FROM ECLIPSE
DO $$
DECLARE
   table_name text;
BEGIN
   FOR table_name IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename NOT LIKE 'spatial_ref_sys' AND tablename NOT LIKE 'geometry_columns')
   LOOP
      EXECUTE 'DROP TABLE IF EXISTS ' || table_name || ' CASCADE';
   END LOOP;
END $$;