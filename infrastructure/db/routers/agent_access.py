from typing import List, Optional, Union
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.dependencies import get_db
from db.services import ContractService, ClaimService, UserService, PersonService
from db.schemas import (
    Contrat, 
    PaginatedContrats, 
    Sinistre, 
    PaginatedSinistres, 
    Account,
    PersonnePhysique,
    PersonneMorale
)
from db.core.exceptions import NotFoundError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Unified response model for complete user info
class CompleteUserInfo(BaseModel):
    account: Account
    profile: Optional[Union[PersonnePhysique, PersonneMorale]] = None
    profile_type: Optional[str] = None  # "physical" or "moral"


@router.get("/user/{ref_personne}/info", response_model=CompleteUserInfo)
async def get_complete_user_info(
    ref_personne: int,
    db: Session = Depends(get_db)
):
    """
    Get complete user information including account and profile data.
    Works for both physical persons and moral persons (companies).
    
    **For AI Agent Use Only - No Authentication Required**
    
    - **ref_personne**: User reference number
    
    Returns:
    - Account information
    - Profile data (PersonnePhysique or PersonneMorale depending on user type)
    - Profile type indicator
    """
    try:
        logger.info(f"Agent accessing complete user info for ref_personne: {ref_personne}")
        user_service = UserService(db)
        person_service = PersonService(db)
        
        # Get account information
        account = user_service.get_account_by_ref(ref_personne)
        if not account:
            raise NotFoundError(f"User with reference {ref_personne} not found")
        
        # Get profile based on user role
        profile = None
        profile_type = None
        
        try:
            if account.role == "physique":
                profile = person_service.get_physical_person_direct(ref_personne)
                profile_type = "physical"
                logger.info(f"Retrieved physical profile for ref_personne: {ref_personne}")
            elif account.role == "morale":
                profile = person_service.get_moral_person_direct(ref_personne)
                profile_type = "moral"
                logger.info(f"Retrieved moral profile for ref_personne: {ref_personne}")
            else:
                logger.warning(f"Unknown role '{account.role}' for ref_personne: {ref_personne}")
        except NotFoundError:
            logger.warning(f"Profile not found for ref_personne: {ref_personne}, role: {account.role}")
            # Continue without profile data
        
        result = CompleteUserInfo(
            account=account,
            profile=profile,
            profile_type=profile_type
        )
        
        logger.info(f"Successfully retrieved complete user info for ref_personne: {ref_personne}")
        return result
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting complete user info for ref_personne {ref_personne}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


@router.get("/user/{ref_personne}/contracts", response_model=PaginatedContrats)
async def get_user_contracts_by_id(
    ref_personne: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """
    Get user's insurance contracts by reference ID with pagination.
    
    **For AI Agent Use Only - No Authentication Required**
    
    - **ref_personne**: User reference number
    - **page**: Page number (starts from 1)
    - **size**: Number of contracts per page (max 100)
    """
    try:
        logger.info(f"Agent accessing contracts for ref_personne {ref_personne}: page={page}, size={size}")
        
        # First verify user exists
        user_service = UserService(db)
        user = user_service.get_account_by_ref(ref_personne)
        if not user:
            raise NotFoundError(f"User with reference {ref_personne} not found")
        
        contract_service = ContractService(db)
        result = contract_service.get_user_contracts(
            ref_personne=ref_personne,
            page=page,
            size=size
        )
        logger.info(f"Successfully retrieved contracts for ref_personne {ref_personne}")
        return result
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting contracts for ref_personne {ref_personne}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


@router.get("/user/{ref_personne}/contracts/{num_contrat}", response_model=Contrat)
async def get_contract_by_id_for_user(
    ref_personne: int,
    num_contrat: str,
    db: Session = Depends(get_db)
):
    """
    Get specific contract details by contract number for a user.
    
    **For AI Agent Use Only - No Authentication Required**
    
    - **ref_personne**: User reference number
    - **num_contrat**: Contract number
    """
    try:
        logger.info(f"Agent accessing contract {num_contrat} for ref_personne {ref_personne}")
        
        # First verify user exists
        user_service = UserService(db)
        user = user_service.get_account_by_ref(ref_personne)
        if not user:
            raise NotFoundError(f"User with reference {ref_personne} not found")
        
        contract_service = ContractService(db)
        contract = contract_service.get_contract_by_number(
            num_contrat=num_contrat,
            ref_personne=ref_personne
        )
        logger.info(f"Successfully retrieved contract {num_contrat} for ref_personne {ref_personne}")
        return contract
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting contract {num_contrat} for ref_personne {ref_personne}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


@router.get("/user/{ref_personne}/claims", response_model=PaginatedSinistres)
async def get_user_claims_by_id(
    ref_personne: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """
    Get user's insurance claims by reference ID with pagination.
    
    **For AI Agent Use Only - No Authentication Required**
    
    - **ref_personne**: User reference number
    - **page**: Page number (starts from 1)
    - **size**: Number of claims per page (max 100)
    """
    try:
        logger.info(f"Agent accessing claims for ref_personne {ref_personne}: page={page}, size={size}")
        
        # First verify user exists
        user_service = UserService(db)
        user = user_service.get_account_by_ref(ref_personne)
        if not user:
            raise NotFoundError(f"User with reference {ref_personne} not found")
        
        claim_service = ClaimService(db)
        result = claim_service.get_user_claims(
            ref_personne=ref_personne,
            page=page,
            size=size
        )
        logger.info(f"Successfully retrieved claims for ref_personne {ref_personne}")
        return result
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting claims for ref_personne {ref_personne}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


@router.get("/user/{ref_personne}/claims/{num_sinistre}", response_model=Sinistre)
async def get_claim_by_id_for_user(
    ref_personne: int,
    num_sinistre: str,
    db: Session = Depends(get_db)
):
    """
    Get specific claim details by claim number for a user.
    
    **For AI Agent Use Only - No Authentication Required**
    
    - **ref_personne**: User reference number
    - **num_sinistre**: Claim number
    """
    try:
        logger.info(f"Agent accessing claim {num_sinistre} for ref_personne {ref_personne}")
        
        # First verify user exists
        user_service = UserService(db)
        user = user_service.get_account_by_ref(ref_personne)
        if not user:
            raise NotFoundError(f"User with reference {ref_personne} not found")
        
        claim_service = ClaimService(db)
        claim = claim_service.get_claim_by_number(
            num_sinistre=num_sinistre,
            ref_personne=ref_personne
        )
        logger.info(f"Successfully retrieved claim {num_sinistre} for ref_personne {ref_personne}")
        return claim
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting claim {num_sinistre} for ref_personne {ref_personne}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )