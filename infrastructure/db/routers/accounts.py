from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.dependencies import get_db, get_current_active_user, require_admin_role
from db.services import UserService
from db.schemas import Account
from db.models import Account as AccountModel

router = APIRouter()


@router.get("/", response_model=List[Account])
async def get_accounts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: AccountModel = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """
    Get all accounts (admin only).
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    """
    user_service = UserService(db)
    accounts = user_service.get_all_accounts(skip=skip, limit=limit)
    return accounts


@router.get("/{ref_personne}", response_model=Account)
async def get_account(
    ref_personne: int,
    current_user: AccountModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific account details.
    Users can only access their own account unless they have admin privileges.
    """
    # Users can only access their own account
    if current_user.ref_personne != ref_personne:
        # In a real application, you might want to check for admin role here
        from db.core.exceptions import PermissionError
        raise PermissionError("You can only access your own account information")
    
    user_service = UserService(db)
    account = user_service.get_account_by_ref(ref_personne)
    
    if not account:
        from db.core.exceptions import NotFoundError
        raise NotFoundError("Account not found")
    
    return account
