from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.dependencies import get_db, get_current_active_user
from db.services import PersonService
from db.schemas import PersonnePhysique, PersonneMorale
from db.models import Account

router = APIRouter()


@router.get("/physical/{ref_personne}", response_model=PersonnePhysique)
async def get_physical_person(
    ref_personne: int,
    current_user: Account = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get physical person profile.
    Users can only access their own profile.
    
    - **ref_personne**: Person reference number
    """
    person_service = PersonService(db)
    person = person_service.get_physical_person(
        ref_personne=ref_personne,
        current_user_ref=current_user.ref_personne
    )
    return person


@router.get("/moral/{ref_personne}", response_model=PersonneMorale)
async def get_moral_person(
    ref_personne: int,
    current_user: Account = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get moral person (company) profile.
    Users can only access their own profile.
    
    - **ref_personne**: Person reference number
    """
    person_service = PersonService(db)
    person = person_service.get_moral_person(
        ref_personne=ref_personne,
        current_user_ref=current_user.ref_personne
    )
    return person
