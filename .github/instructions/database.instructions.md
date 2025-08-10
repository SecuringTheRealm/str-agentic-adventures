---
applyTo: "**/migrations/**,**/database/**,**/*database*,**/*db*"
---

# Database and Migration Guidelines

Apply the [general coding guidelines](./general-coding.instructions.md) to all database-related code.

## Database File Management

### File Cleanup and Version Control

- **NEVER commit database files** (*.db, *.sqlite, *.sqlite3) to version control
- **ALWAYS remove generated database files** before committing code
- Use `.gitignore` to prevent accidental database file commits
- Delete test databases and cache files during cleanup

### Database File Patterns to Avoid

- SQLite database files: `*.db`, `*.sqlite`, `*.sqlite3`
- Database journals: `*.db-journal`, `*.sqlite-journal`
- Database WAL files: `*.db-wal`, `*.sqlite-wal`
- Database SHM files: `*.db-shm`, `*.sqlite-shm`
- Backup files: `*.db.backup`, `*.sqlite.bak`

## Schema Management

### Alembic Migration System

- **MANDATORY: Use Alembic for all schema changes** - Never modify database models without creating migrations
- **Automatic migration runner on startup** - The application automatically checks and runs migrations
- **Migration file organization**: Stored in `backend/migrations/versions/`
- **Naming convention**: Alembic auto-generates timestamps like `9a6d5baf6502_initial_database_schema.py`

### Migration Best Practices

- **Always create migration scripts** for any model changes using `alembic revision --autogenerate -m "description"`
- **Test migrations on realistic data** before deploying to production
- **Make migrations reversible** when possible by implementing proper `downgrade()` functions
- **Document breaking changes** and required data transformations in migration comments
- **Review auto-generated migrations** - Alembic may miss some changes or generate suboptimal SQL

### Migration Workflow

1. **Make model changes** in `app/models/db_models.py`
2. **Generate migration**: `cd backend && uv run alembic revision --autogenerate -m "description"`
3. **Review generated migration** in `migrations/versions/` directory
4. **Test migration**: Start the application - migrations run automatically
5. **Commit both model changes and migration files** together

### Database Environment Configuration

- **PostgreSQL (Production)**: Set `DATABASE_HOST`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`
- **Azure AD Authentication**: Set `DATABASE_HOST` and `DATABASE_NAME` without user/password for Managed Identity
- **SQLite (Development)**: Default fallback when no PostgreSQL env vars are set
- **Custom URL**: Set `DATABASE_URL` to override automatic configuration

### Migration File Organization

- **Location**: `backend/migrations/versions/`
- **Auto-generated naming**: Alembic uses revision hashes + description
- **Migration history**: Tracked in `alembic_version` table
- **Startup behavior**: 
  - Empty DB → Create schema + stamp with head revision
  - Existing DB without tracking → Stamp with current head
  - Tracked DB behind head → Run upgrade migrations
  - Up-to-date DB → No action required

## Database Development Practices

### Local Development

- Use environment variables for database connections
- Provide database seeding scripts for development setup
- Include database schema documentation
- Use connection pooling for production environments

### Testing Database Interactions

- **Mock database calls** in unit tests
- Use **in-memory databases** for integration tests
- **Clean up test data** after each test run
- **Isolate test transactions** to prevent data pollution

### Data Persistence Patterns

- Use **Pydantic models** for data validation in Python
- Implement **proper serialization** for complex data types
- Use **SQLAlchemy** for all database interactions in Python
- Follow **repository pattern** for data access abstraction

## Performance and Optimization

### Query Optimization

- Index frequently queried columns
- Use database-specific optimization features
- Monitor query performance in production
- Implement query caching where appropriate

### Connection Management

- Use connection pooling for high-traffic applications
- Implement proper connection cleanup
- Handle connection timeouts gracefully
- Monitor connection pool metrics

## Security Considerations

### Data Protection

- **Encrypt sensitive data** at rest and in transit
- **Sanitize all user inputs** to prevent SQL injection
- **Use parameterized queries** for all database operations
- **Implement proper access controls** and user permissions

### Configuration Security

- **Store connection strings** in environment variables
- **Never commit database credentials** to version control
- **Use Azure Key Vault** for production secrets
- **Rotate database credentials** regularly

## Environment-Specific Configurations

### Development Environment

- Use local database instances for development
- Provide easy setup scripts for new developers
- Include sample data for testing features
- Document local database setup procedures

### Testing Environment

- Use separate test databases
- Implement database reset procedures
- Provide test data factories
- Clean up test data automatically

### Production Environment

- Use managed database services when possible
- Implement proper backup and recovery procedures
- Monitor database performance and health
- Set up alerting for database issues

## Data Migration Procedures

### Large Data Migrations

- Plan migrations during low-traffic periods
- Implement progress tracking for long-running migrations
- Test migrations on production-like data volumes
- Have rollback procedures ready

### Breaking Changes

- Communicate breaking changes to all stakeholders
- Provide migration guides for dependent services
- Implement backward compatibility when possible
- Plan deprecation timelines for old schemas

## Monitoring and Maintenance

### Database Health Monitoring

- Monitor database performance metrics
- Set up alerts for critical issues
- Track storage usage and growth patterns
- Monitor connection pool utilization

### Regular Maintenance

- Schedule regular database maintenance windows
- Update database statistics regularly
- Archive or purge old data according to retention policies
- Keep database software updated with security patches

## Documentation Requirements

### Database Documentation

- Document all database schemas and relationships
- Maintain up-to-date ERD (Entity Relationship Diagrams)
- Document stored procedures and functions
- Include data dictionary for all tables and columns

### Migration Documentation

- Document the purpose of each migration
- Include rollback procedures and considerations
- Note any manual steps required for deployment
- Maintain migration dependency documentation

## Integration with Application Code

### Code Organization

- Separate database logic from business logic
- Use dependency injection for database connections
- Implement proper error handling for database operations
- Use transactions appropriately for data consistency

### API Integration

- Validate all data before database operations
- Implement proper error responses for database failures
- Use database connection pooling in API servers
- Handle database timeouts gracefully in API responses