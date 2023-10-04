-- Create new user role
CREATE ROLE jordan WITH LOGIN PASSWORD 'password';

-- Grant all privileges on 'eclipse' database to the new role
GRANT ALL PRIVILEGES ON DATABASE eclipse TO jordan;

-- (Optional) Set the role to be the owner of the 'eclipse' database
ALTER DATABASE eclipse OWNER TO jordan;
