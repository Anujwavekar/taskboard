from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest


class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


# Used when the email doesn't exist, so login takes the same time either way
DUMMY_HASH = hash_password("dummy-password")


def create_user(db: Session, data: SignupRequest) -> User:
    existing = db.scalar(select(User).where(User.email == data.email))
    if existing:
        raise EmailAlreadyExistsError()

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Two signups with the same email at the same moment: the DB unique rule wins
        db.rollback()
        raise EmailAlreadyExistsError()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: LoginRequest) -> User:
    user = db.scalar(select(User).where(User.email == data.email))
    password_hash = user.password_hash if user else DUMMY_HASH
    password_ok = verify_password(data.password, password_hash)

    # Same error for "no such email" and "wrong password"
    if user is None or not password_ok:
        raise InvalidCredentialsError()
    return user