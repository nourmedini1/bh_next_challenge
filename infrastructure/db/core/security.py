from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from db.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        logger.debug(f"Attempting to verify password for user")
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Password verification result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error during password verification: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Generate hash for a password."""
    try:
        logger.debug("Generating password hash")
        hash_result = pwd_context.hash(password)
        logger.debug("Password hash generated successfully")
        return hash_result
    except Exception as e:
        logger.error(f"Error generating password hash: {e}")
        raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    try:
        logger.debug(f"Creating access token for data: {data}")
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        logger.debug("Access token created successfully")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        logger.debug("Attempting to verify JWT token")
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        logger.debug(f"Token verified successfully, payload: {payload}")
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None
