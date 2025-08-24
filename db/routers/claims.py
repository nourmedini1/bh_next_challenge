from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from db.dependencies import get_db, get_current_active_user
from db.services import ClaimService
from db.schemas import Sinistre, PaginatedSinistres
from db.models import Account
from db.core.exceptions import NotFoundError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=PaginatedSinistres)
async def get_user_claims(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: Account = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's insurance claims with pagination.
    
    - **page**: Page number (starts from 1)
    - **size**: Number of claims per page (max 100)
    """
    try:
        logger.info(f"Getting claims for user {current_user.ref_personne}: page={page}, size={size}")
        claim_service = ClaimService(db)
        result = claim_service.get_user_claims(
            ref_personne=current_user.ref_personne,
            page=page,
            size=size
        )
        logger.info(f"Successfully retrieved claims for user {current_user.ref_personne}")
        return result
    except Exception as e:
        logger.error(f"Error getting claims for user {current_user.ref_personne}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


@router.get("/{num_sinistre}", response_model=Sinistre)
async def get_claim_details(
    num_sinistre: str,
    current_user: Account = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific insurance claim.
    Users can only access their own claims.
    
    - **num_sinistre**: Claim number
    """
    try:
        logger.info(f"Getting claim details {num_sinistre} for user {current_user.ref_personne}")
        claim_service = ClaimService(db)
        claim = claim_service.get_claim_details(
            num_sinistre=num_sinistre,
            ref_personne=current_user.ref_personne
        )
        logger.info(f"Successfully retrieved claim {num_sinistre} for user {current_user.ref_personne}")
        return claim
    except NotFoundError as e:
        logger.warning(f"Claim {num_sinistre} not found for user {current_user.ref_personne}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting claim {num_sinistre} for user {current_user.ref_personne}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
