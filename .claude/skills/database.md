# Database Patterns

## ORM-Only Rule
**Never** import `sqlite3`, `psycopg2`, or any raw driver. All DB access goes through SQLAlchemy:
```python
from backend.app.database import get_session

with next(get_session()) as db:
    result = db.query(MyModel).filter(MyModel.id == id).first()
```

## Alembic Migration Workflow
1. Edit model in `backend/app/models/db_models.py`.
2. Generate migration:
   ```bash
   cd backend && uv run alembic revision --autogenerate -m "short description"
   ```
3. Review the generated file in `backend/migrations/versions/`.
4. Start the app – migrations run automatically on startup.
5. Commit model + migration file together in the same commit.

## Startup Behavior
| DB state | Action |
|---|---|
| Empty | Create schema + stamp head |
| Exists, untracked | Stamp current head |
| Behind head | Run upgrade |
| Up to date | No-op |

## Environment Variables
| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Override full connection URL |
| `DATABASE_HOST` + `DATABASE_NAME` | PostgreSQL / Azure AD Managed Identity |
| `DATABASE_USER` + `DATABASE_PASSWORD` | PostgreSQL with password |
| (none set) | Falls back to SQLite for local dev |

## Testing
Mock DB calls in unit tests; use in-memory SQLite for integration tests. Always clean up test data.
