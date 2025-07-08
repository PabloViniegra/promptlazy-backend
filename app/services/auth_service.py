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


def update_user(db: Session, user: User, update_data: dict):
    """
    Updates user information based on the provided data.
    If updating password, verifies the current password first.
    Returns the updated user object.
    Raises HTTPException if:
    - Current password is required but not provided when updating password
    - Current password is incorrect
    - New email is already registered
    - New username is already taken
    """
    if 'new_password' in update_data:
        if not update_data.get('current_password'):
            raise HTTPException(
                status_code=400,
                detail="Current password is required to change password"
            )
        if not verify_password(update_data['current_password'], user.hashed_password):
            raise HTTPException(
                status_code=400,
                detail="Incorrect current password"
            )
        user.hashed_password = hash_password(update_data['new_password'])
        update_data.pop('new_password')
        update_data.pop('current_password')

    for field, value in update_data.items():
        if value is not None and hasattr(user, field):
            setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        db.rollback()
        if 'email' in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        elif 'username' in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )
        raise HTTPException(status_code=400, detail="Update failed")

    return user


def create_token_pair(user_id: UUID):
    """
    Creates a pair of access and refresh tokens for the given user ID.
    Returns a dictionary with 'access_token' and 'refresh_token'.
    """
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token({"sub": str(user_id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
