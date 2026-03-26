"""Tests for Alembic migration integrity."""

import os
import subprocess
from pathlib import Path

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..")


def test_single_alembic_head() -> None:
    """Verify that only one Alembic head revision exists (no branch divergence)."""
    result = subprocess.run(
        ["uv", "run", "alembic", "heads"],  # noqa: S607
        capture_output=True,
        text=True,
        cwd=BACKEND_DIR,
    )
    assert result.returncode == 0, f"alembic heads failed: {result.stderr}"
    heads = [line for line in result.stdout.strip().split("\n") if line.strip()]
    assert len(heads) == 1, f"Expected 1 head, got {len(heads)}: {heads}"


def test_upgrade_downgrade_cycle(tmp_path: Path) -> None:
    """Run alembic upgrade head then downgrade base on a fresh SQLite DB."""
    db_url = f"sqlite:///{tmp_path}/test.db"
    env = {**os.environ, "DATABASE_URL": db_url}

    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],  # noqa: S607
        capture_output=True,
        text=True,
        cwd=BACKEND_DIR,
        env=env,
    )
    assert result.returncode == 0, f"Upgrade failed: {result.stderr}"

    result = subprocess.run(
        ["uv", "run", "alembic", "downgrade", "base"],  # noqa: S607
        capture_output=True,
        text=True,
        cwd=BACKEND_DIR,
        env=env,
    )
    assert result.returncode == 0, f"Downgrade failed: {result.stderr}"


def test_current_matches_models(tmp_path: Path) -> None:
    """Verify alembic check reports no pending migrations after upgrading to head."""
    db_url = f"sqlite:///{tmp_path}/test.db"
    env = {**os.environ, "DATABASE_URL": db_url}

    # Apply all migrations first
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],  # noqa: S607
        capture_output=True,
        text=True,
        cwd=BACKEND_DIR,
        env=env,
    )
    assert result.returncode == 0, f"Upgrade failed: {result.stderr}"

    # Check that models match the migrated schema
    result = subprocess.run(
        ["uv", "run", "alembic", "check"],  # noqa: S607
        capture_output=True,
        text=True,
        cwd=BACKEND_DIR,
        env=env,
    )
    assert result.returncode == 0, (
        f"alembic check detected pending migrations: {result.stdout}{result.stderr}"
    )
