import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
from fastapi.security import APIKeyHeader
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

api_key_scheme = APIKeyHeader(name="Authorization")


def create_access_token(data: dict):
    """
    Creates a JWT access token with an expiration time.
    The token includes the provided data and is valid for ACCESS_TOKEN_EXPIRE_MINUTES.
    Returns the encoded JWT as a string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    """
    Creates a JWT refresh token with an expiration time.
    The token includes the provided data and is valid for REFRESH_TOKEN_EXPIRE_DAYS.
    Returns the encoded JWT as a string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, token_type: str = 'access'):
    """
    Verifies and decodes a JWT token.
    Checks if the token type matches ('access' or 'refresh').
    Returns the payload if valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        return None
