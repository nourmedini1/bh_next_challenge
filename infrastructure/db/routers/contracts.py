from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from db.dependencies import get_db, get_current_active_user
from db.services import ContractService
from db.schemas import Contrat, PaginatedContrats
from db.models import Account
from db.core.exceptions import NotFoundError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=PaginatedContrats)
async def get_user_contracts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: Account = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's insurance contracts with pagination.
    
    - **page**: Page number (starts from 1)
    - **size**: Number of contracts per page (max 100)
    """
    try:
        logger.info(f"Getting contracts for user {current_user.ref_personne}: page={page}, size={size}")
        contract_service = ContractService(db)
        result = contract_service.get_user_contracts(
            ref_personne=current_user.ref_personne,
            page=page,
            size=size
        )
        logger.info(f"Successfully retrieved contracts for user {current_user.ref_personne}")
        return result
    except Exception as e:
        logger.error(f"Error getting contracts for user {current_user.ref_personne}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


@router.get("/{num_contrat}", response_model=Contrat)
async def get_contract_details(
    num_contrat: str,
    current_user: Account = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific contract including guarantees.
    Users can only access their own contracts.
    
    - **num_contrat**: Contract number
    """
    try:
        logger.info(f"Getting contract details {num_contrat} for user {current_user.ref_personne}")
        contract_service = ContractService(db)
        contract = contract_service.get_contract_details(
            num_contrat=num_contrat,
            ref_personne=current_user.ref_personne
        )
        logger.info(f"Successfully retrieved contract {num_contrat} for user {current_user.ref_personne}")
        return contract
    except NotFoundError as e:
        logger.warning(f"Contract {num_contrat} not found for user {current_user.ref_personne}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting contract {num_contrat} for user {current_user.ref_personne}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
