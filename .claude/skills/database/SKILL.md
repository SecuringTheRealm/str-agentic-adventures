---
name: database
description: SQLAlchemy ORM patterns, Alembic migrations, database session management
---

# Database Patterns

## ORM Only
- Use SQLAlchemy ORM for ALL database interactions
- Never use raw sqlite3, psycopg2, or SQL strings
- Models in `backend/app/models/`

## Session Management
- Use FastAPI dependency injection: `db: Session = Depends(get_db)`
- Never call `next(get_session())` — use `Depends` pattern
- Sessions auto-close via the dependency generator

## Alembic Migrations
- Migrations run automatically on startup via `run_migrations()`
- Create new: `cd backend && uv run alembic revision --autogenerate -m "description"`
- Migrations in `backend/alembic/versions/`
- Never call `Base.metadata.create_all()` in application code — let Alembic handle it

## Configuration
- SQLite locally (default): `sqlite:///./str_adventures.db`
- PostgreSQL in production: set `DATABASE_URL` env var
- Never commit `.db` or `.sqlite` files
