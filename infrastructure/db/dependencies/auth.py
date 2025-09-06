from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.dependencies.database import get_db
from db.services import UserService
from db.core.security import verify_token
from db.core.exceptions import AuthenticationError
from db.models import Account

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Account:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise AuthenticationError("Invalid token")
    
    ref_personne: str = payload.get("sub")
    if ref_personne is None:
        raise AuthenticationError("Invalid token payload")
    
    user_service = UserService(db)
    user = user_service.get_account_by_ref(int(ref_personne))
    
    if user is None:
        raise AuthenticationError("User not found")
    
    return user


def get_current_active_user(
    current_user: Account = Depends(get_current_user)
) -> Account:
    """Get current active user (can be extended with activation checks)."""
    return current_user


def require_admin_role(
    current_user: Account = Depends(get_current_active_user)
) -> Account:
    """Require admin role for accessing certain endpoints."""
    # For now, we'll use a simple check - in a real app you might have dedicated admin roles
    if current_user.role not in ["admin"]:  # Extend this list as needed
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
