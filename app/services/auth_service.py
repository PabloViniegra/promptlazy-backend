from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token
from passlib.context import CryptContext
from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.exc import IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes a plain password using bcrypt.
    Returns the hashed password as a string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    Returns True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def register_user(db: Session, email: str, password: str, username: str = None, full_name: str = None):
    """
    Registers a new user with the given email, password, username, and full name.
    Hashes the password before storing it.
    Raises HTTPException if the email is already registered.
    Returns the created User object.
    """
    hashed = hash_password(password)
    user = User(email=email, hashed_password=hashed,
                username=username, full_name=full_name, is_active=True)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return user


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticates a user by email and password.
    Returns the User object if authentication is successful, otherwise None.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_token_pair(user_id: UUID):
    """
    Creates a pair of access and refresh tokens for the given user ID.
    Returns a dictionary with 'access_token' and 'refresh_token'.
    """
    data = {"sub": str(user_id)}
    return {
        "access_token": create_access_token(data),
        "refresh_token": create_refresh_token(data),
    }
