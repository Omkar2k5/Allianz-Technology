# Database Setup Guide

## Prerequisites

- PostgreSQL 15+ installed
- Database credentials configured in `.env`

## Setup Steps

### Option 1: Using psql (Command Line)

```bash
# 1. Create database (if not exists)
psql -U postgres -c "CREATE DATABASE ecocompute;"

# 2. Run schema
psql -U postgres -d ecocompute -f backend/database/schema.sql

# 3. Run seed data
psql -U postgres -d ecocompute -f backend/database/seed.sql

# 4. Run auth migration
psql -U postgres -d ecocompute -f backend/database/migrations/001_add_auth.sql
```

### Option 2: Using pgAdmin or DBeaver

1. Create a new database named `ecocompute`
2. Open Query Tool
3. Run files in order:
   - `backend/database/schema.sql`
   - `backend/database/seed.sql`
   - `backend/database/migrations/001_add_auth.sql`

### Option 3: Using Python Script

```bash
cd backend/database
python setup_db.py
```

## Verify Setup

```sql
-- Check tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check test users
SELECT email, role, first_name, last_name 
FROM users;

-- Check sample data
SELECT COUNT(*) as total_requests FROM genai_requests;
```

## Test Credentials

All test users have password: **demo123**

- `admin@allianz.com` (admin)
- `analyst@allianz.com` (analyst)
- `developer@allianz.com` (developer)

## Troubleshooting

### Connection refused
- Ensure PostgreSQL is running
- Check credentials in `.env`
- Verify port 5432 is not blocked

### Permission denied
- Run as postgres superuser
- Grant necessary permissions

### Table already exists
- Drop existing tables or use `DROP DATABASE ecocompute CASCADE;` and recreate
