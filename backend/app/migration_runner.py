"""Migration runner for automatic database schema updates."""

import logging
import os
from typing import Any

from alembic import command, config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from app.database import DATABASE_URL, engine

logger = logging.getLogger(__name__)


def get_alembic_config() -> config.Config:
    """Get Alembic configuration."""
    # Get the directory containing this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the backend directory where alembic.ini is located
    backend_dir = os.path.dirname(current_dir)
    alembic_ini_path = os.path.join(backend_dir, "alembic.ini")

    if not os.path.exists(alembic_ini_path):
        raise FileNotFoundError(
            f"Alembic configuration not found at {alembic_ini_path}"
        )

    cfg = config.Config(alembic_ini_path)
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    return cfg


def has_alembic_version_table() -> bool:
    """Check if the alembic_version table exists."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return "alembic_version" in tables
    except Exception as e:
        logger.warning(f"Error checking for alembic_version table: {e}")
        return False


def is_database_empty() -> bool:
    """Check if the database is completely empty (no tables)."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return len(tables) == 0
    except Exception as e:
        logger.warning(f"Error checking if database is empty: {e}")
        return True


def get_current_revision() -> str | None:
    """Get the current database revision."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            row = result.fetchone()
            return row[0] if row else None
    except Exception as e:
        logger.warning(f"Error getting current revision: {e}")
        return None


def get_head_revision() -> str | None:
    """Get the head revision from migration scripts."""
    try:
        cfg = get_alembic_config()
        script_dir = ScriptDirectory.from_config(cfg)
        return script_dir.get_current_head()
    except Exception as e:
        logger.warning(f"Error getting head revision: {e}")
        return None


def run_migrations() -> None:
    """
    Run database migrations automatically on startup.

    Logic:
    1. If no alembic_version table exists and database is empty -> run create_all
    2. If no alembic_version table exists but database has tables -> stamp with current head
    3. If alembic_version exists but is behind head -> run upgrade
    4. Otherwise -> do nothing
    """
    try:
        logger.info("Checking database migration status...")

        # Check if this is a fresh database
        if is_database_empty():
            logger.info("Database is empty, creating initial schema...")
            from app.database import init_db

            init_db()

            # Stamp the database with the current head revision
            cfg = get_alembic_config()
            command.stamp(cfg, "head")
            logger.info("Database initialized and stamped with current migration head")
            return

        # Check if alembic version table exists
        if not has_alembic_version_table():
            logger.info(
                "Existing database found without migration tracking, stamping with current head..."
            )
            cfg = get_alembic_config()
            command.stamp(cfg, "head")
            logger.info("Database stamped with current migration head")
            return

        # Check if migrations need to be run
        current_rev = get_current_revision()
        head_rev = get_head_revision()

        if current_rev is None:
            logger.warning("Could not determine current database revision")
            return

        if head_rev is None:
            logger.warning("Could not determine head revision from migration scripts")
            return

        if current_rev == head_rev:
            logger.info(f"Database is up to date (revision: {current_rev})")
            return

        logger.info(f"Database needs upgrade: {current_rev} -> {head_rev}")
        cfg = get_alembic_config()
        command.upgrade(cfg, "head")
        logger.info("Database migration completed successfully")

    except Exception as e:
        logger.error(f"Error running database migrations: {e}")
        # Don't raise the exception to allow the application to continue
        # In production, you might want to fail fast instead


def create_initial_migration() -> None:
    """Create the initial migration if none exists."""
    try:
        cfg = get_alembic_config()
        script_dir = ScriptDirectory.from_config(cfg)

        # Check if any migrations exist
        revisions = list(script_dir.walk_revisions())
        if revisions:
            logger.info("Migration files already exist")
            return

        logger.info("Creating initial migration...")
        command.revision(cfg, autogenerate=True, message="Initial database schema")
        logger.info("Initial migration created")

    except Exception as e:
        logger.error(f"Error creating initial migration: {e}")
