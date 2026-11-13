from sqlalchemy import UniqueConstraint

from cyberquest.models import LearnerProfile, User


def test_user_identity_has_provider_subject_uniqueness() -> None:
    constraints = [
        constraint
        for constraint in User.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    assert len(constraints) == 1
    assert {column.name for column in constraints[0].columns} == {
        "identity_provider",
        "external_subject",
    }


def test_learner_profile_is_one_to_one_with_user() -> None:
    assert LearnerProfile.__table__.primary_key.columns.keys() == ["user_id"]
    foreign_keys = list(LearnerProfile.__table__.foreign_keys)
    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "users.id"
