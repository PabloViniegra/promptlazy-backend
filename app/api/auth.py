from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, RegisterRequest, Token, TokenRefreshRequest, AccessTokenOnly, UserUpdateRequest
from app.services.auth_service import (
    register_user, authenticate_user, create_token_pair, create_access_token, update_user
)
from app.db.session import SessionLocal
from app.core.security import verify_token
from app.models.user import User
from app.core.security import api_key_scheme

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=Token)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user and returns a pair of access and refresh tokens.
    """
    user = register_user(db, data.email, data.password,
                         data.username, data.full_name)
    tokens = create_token_pair(user.id)
    return tokens


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a pair of access and refresh tokens.
    Raises HTTPException if credentials are invalid.
    """
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    tokens = create_token_pair(user.id)
    return tokens


@router.post("/refresh", response_model=AccessTokenOnly)
def refresh(data: TokenRefreshRequest):
    """
    Generates a new pair of access and refresh tokens using a valid refresh token.
    Raises HTTPException if the refresh token is invalid.
    """
    payload = verify_token(data.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = payload.get("sub")
    access_token = create_access_token({"sub": user_id})
    return {"access_token": access_token}


def get_current_user(
    token: str = Depends(api_key_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency that retrieves the current authenticated user from the access token.
    Raises HTTPException if the token is invalid or the user does not exist.
    """
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer prefix")
    token = token.replace("Bearer ", "")
    payload = verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/me")
def get_current_user_profile(user: User = Depends(get_current_user)):
    """
    Returns the profile information of the currently authenticated user.
    """
    return {"id": user.id, "email": user.email, "username": user.username, "full_name": user.full_name}


@router.put("/me")
def update_current_user(
    update_data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates the profile information of the currently authenticated user.

    - To update password, both 'current_password' and 'new_password' must be provided.
    - Other fields (username, email, full_name) can be updated independently.
    - Only provided fields will be updated.
    """
    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        return {"id": current_user.id, "email": current_user.email,
                "username": current_user.username, "full_name": current_user.full_name}

    updated_user = update_user(db, current_user, update_dict)

    return {
        "id": updated_user.id,
        "email": updated_user.email,
        "username": updated_user.username,
        "full_name": updated_user.full_name,
        "message": "User updated successfully"
    }
