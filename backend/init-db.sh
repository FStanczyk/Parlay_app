#!/bin/bash
set -e

echo "Creating database and user..."

# Create database and user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE parlay_db;
    CREATE USER parlay_user WITH PASSWORD 'parlay_password';
    GRANT ALL PRIVILEGES ON DATABASE parlay_db TO parlay_user;
    ALTER USER parlay_user CREATEDB;
    ALTER USER parlay_user WITH SUPERUSER;
EOSQL

echo "Database and user created successfully!"
