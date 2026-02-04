-- Create database (run this as postgres superuser)
-- CREATE DATABASE ecocompute;

-- Connect to ecocompute database and run the following:

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Run the main schema
\i schema.sql

-- Run the seed data
\i seed.sql

-- Run auth migration
\i migrations/001_add_auth.sql
