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

### Migration Best Practices

- **Always create migration scripts** for schema changes
- **Test migrations on realistic data** before deploying
- **Make migrations reversible** when possible
- **Document breaking changes** and required data transformations
- **Version migrations sequentially** to maintain consistency

### Migration File Organization

- Place migration files in dedicated `migrations/` directory
- Use timestamp-based naming: `YYYYMMDD_HHMMSS_description.sql`
- Include both up and down migration scripts
- Maintain a migration history table in the database

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