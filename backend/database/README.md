# Database Setup

This directory contains the PostgreSQL database schema and seed data for Eco-Compute.

## Files

- `schema.sql` - Complete database schema with tables, indexes, triggers, and views
- `seed.sql` - Sample data for development and testing
- `migrations/` - Alembic migration files (for production deployments)

## Quick Start

### Using Docker

The database is automatically set up when you run `docker-compose up`:

```bash
cd ../..
docker-compose up -d postgres
```

### Manual Setup

If you want to set up PostgreSQL manually:

```bash
# Create database
createdb ecocompute

# Run schema
psql ecocompute < schema.sql

# Load seed data (optional, for development)
psql ecocompute < seed.sql
```

## Database Schema Overview

### Core Tables

1. **teams** - Multi-tenant organizations
2. **apps** - Applications using GenAI
3. **genai_requests** - Every GenAI API call (NO prompts, only metadata)
4. **carbon_metrics** - Pre-aggregated metrics for fast queries
5. **models** - AI model catalog with energy profiles
6. **policies** - Governance rules
7. **alerts** - Threshold notifications
8. **recommendations** - Optimization suggestions
9. **carbon_intensity_regions** - Regional carbon intensity data
10. **users** - Dashboard authentication

### Privacy & Compliance

**IMPORTANT**: The `genai_requests` table does NOT store actual prompts or responses.

- `request_hash`: SHA-256 hash for deduplication only
- Only metadata stored: tokens, model, region, timestamps
- Compliant with data privacy regulations

## Sample Data

The seed file includes:

- 3 teams (Allianz Demo, Customer Success, Development)
- 3 users (admin, analyst, developer) - Password: `demo123`
- 4 applications
- 500 GenAI requests over last 7 days
- 6 AI models (GPT-4, GPT-3.5, Claude, Gemini, Llama)
- 2 policies
- 3 recommendations
- 2 alerts
- 6 carbon intensity regions

## Migrations (Production)

For production deployments, use Alembic for database migrations:

```bash
# Install Alembic
pip install alembic psycopg2-binary

# Initialize (already done)
alembic init migrations

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Connecting from Backend Services

Connection string format:

```
postgresql://username:password@host:port/database
```

Example:

```
DATABASE_URL=postgresql://admin:password@localhost:5432/ecocompute
```

## Indexes

The schema includes optimized indexes for:

- Fast dashboard queries (timestamp-based)
- App-specific filtering
- Model and provider lookups
- Policy evaluation
- Aggregation queries

## Views

Pre-defined views for common queries:

- `v_recent_requests` - Latest requests with app and model details
- `v_daily_metrics` - Daily aggregated metrics

## Backup & Restore

```bash
# Backup
pg_dump ecocompute > backup.sql

# Restore
psql ecocompute < backup.sql
```

## Performance Tips

1. The `carbon_metrics` table is pre-aggregated for fast dashboard queries
2. Use the views for common queries
3. Partition `genai_requests` table by date for large datasets (production)
4. Regular VACUUM and ANALYZE for optimal performance

## Security

- Use strong passwords in production
- Enable SSL connections
- Restrict network access to database
- Regular security updates
- Audit logs for sensitive operations
