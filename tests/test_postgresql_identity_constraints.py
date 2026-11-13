"""Exercise identity constraints against the migrated PostgreSQL schema."""

import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from cyberquest.models import LearnerProfile, User


@pytest.fixture()
def db_session():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL is required for PostgreSQL persistence tests")
    engine = create_engine(database_url)
    try:
        with Session(engine) as session:
            yield session
            session.rollback()
    finally:
        engine.dispose()


def test_postgresql_rejects_duplicate_external_identity(db_session: Session) -> None:
    provider = f"test-provider-{uuid4()}"
    subject = f"subject-{uuid4()}"
    db_session.add(
        User(identity_provider=provider, external_subject=subject)
    )
    db_session.commit()

    db_session.add(
        User(identity_provider=provider, external_subject=subject)
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_postgresql_rejects_orphan_learner_profile(db_session: Session) -> None:
    db_session.add(LearnerProfile(user_id=uuid4(), display_name="Orphan"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_postgresql_cascades_user_deletion_to_profile(db_session: Session) -> None:
    user = User(
        identity_provider=f"test-provider-{uuid4()}",
        external_subject=f"subject-{uuid4()}",
    )
    db_session.add(user)
    db_session.flush()
    user_id = user.id
    db_session.add(LearnerProfile(user_id=user_id, display_name="Test learner"))
    db_session.commit()

    db_session.execute(delete(User).where(User.id == user_id))
    db_session.commit()

    assert db_session.get(LearnerProfile, user_id) is None
