import os

import pytest
from sqlalchemy import create_engine, inspect


def test_initial_migration_creates_expected_postgresql_schema() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL is required for PostgreSQL migration verification")
    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        assert {"alembic_version", "users", "learner_profiles"} <= tables
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        assert {"id", "identity_provider", "external_subject", "created_at"} <= user_columns
        profile_fks = inspector.get_foreign_keys("learner_profiles")
        assert any(fk["referred_table"] == "users" for fk in profile_fks)
        unique_constraints = inspector.get_unique_constraints("users")
        assert any(
            set(constraint["column_names"]) == {"identity_provider", "external_subject"}
            for constraint in unique_constraints
        )
    finally:
        engine.dispose()
