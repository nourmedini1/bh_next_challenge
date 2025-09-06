from typing import Optional, List
from sqlalchemy.orm import Session
from db.repositories import (
    AccountRepository,
    PersonnePhysiqueRepository,
    PersonneMoraleRepository,
    ContratRepository,
    SinistreRepository,
)
from db.schemas import UserProfile, PaginatedContrats, PaginatedSinistres
from db.models import Account, PersonnePhysique, PersonneMorale, Contrat, Sinistre
from db.core.security import verify_password, create_access_token
from db.core.exceptions import AuthenticationError, NotFoundError, PermissionError
import math
import logging

# Configure logging
logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = AccountRepository(db)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Account]:
        try:
            logger.debug(f"Attempting to authenticate user with email: {email}")
            account = self.account_repo.get_by_email(email)
            
            if not account:
                logger.warning(f"No account found for email: {email}")
                return None
            
            logger.debug(f"Account found: ref_personne={account.ref_personne}, role={account.role}")
            
            if not verify_password(password, account.password_hash):
                logger.warning(f"Password verification failed for email: {email}")
                return None
            
            logger.info(f"User authenticated successfully: {email}")
            return account
            
        except Exception as e:
            logger.error(f"Error during user authentication for {email}: {e}")
            raise
    
    def create_token_for_user(self, account: Account) -> str:
        try:
            logger.debug(f"Creating token for user: ref_personne={account.ref_personne}")
            token_data = {
                "sub": str(account.ref_personne),
                "email": account.email,
                "role": account.role
            }
            token = create_access_token(data=token_data)
            logger.info(f"Token created successfully for user: {account.email}")
            return token
        except Exception as e:
            logger.error(f"Error creating token for user {account.email}: {e}")
            raise


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = AccountRepository(db)
        self.physique_repo = PersonnePhysiqueRepository(db)
        self.morale_repo = PersonneMoraleRepository(db)
    
    def get_user_profile(self, ref_personne: int) -> Optional[UserProfile]:
        account = self.account_repo.get_by_ref_personne(ref_personne)
        if not account:
            return None
        
        personal_info = None
        if account.role == "physique":
            personal_info = self.physique_repo.get_by_ref_personne(ref_personne)
        elif account.role == "morale":
            personal_info = self.morale_repo.get_by_ref_personne(ref_personne)
        
        return UserProfile(account=account, personal_info=personal_info)
    
    def get_account_by_ref(self, ref_personne: int) -> Optional[Account]:
        return self.account_repo.get_by_ref_personne(ref_personne)
    
    def get_all_accounts(self, skip: int = 0, limit: int = 100) -> List[Account]:
        return self.account_repo.get_all(skip, limit)


class PersonService:
    def __init__(self, db: Session):
        self.db = db
        self.physique_repo = PersonnePhysiqueRepository(db)
        self.morale_repo = PersonneMoraleRepository(db)
    
    def get_physical_person(self, ref_personne: int, current_user_ref: int) -> PersonnePhysique:
        if ref_personne != current_user_ref:
            raise PermissionError("You can only access your own profile")
        
        person = self.physique_repo.get_by_ref_personne(ref_personne)
        if not person:
            raise NotFoundError("Physical person not found")
        
        return person
    
    def get_moral_person(self, ref_personne: int, current_user_ref: int) -> PersonneMorale:
        if ref_personne != current_user_ref:
            raise PermissionError("You can only access your own profile")
        
        person = self.morale_repo.get_by_ref_personne(ref_personne)
        if not person:
            raise NotFoundError("Moral person not found")
        
        return person
    
    def get_physical_person_direct(self, ref_personne: int) -> PersonnePhysique:
        """Get physical person without authentication checks - for agent access only"""
        person = self.physique_repo.get_by_ref_personne(ref_personne)
        if not person:
            raise NotFoundError("Physical person not found")
        
        return person
    
    def get_moral_person_direct(self, ref_personne: int) -> PersonneMorale:
        """Get moral person without authentication checks - for agent access only"""
        person = self.morale_repo.get_by_ref_personne(ref_personne)
        if not person:
            raise NotFoundError("Moral person not found")
        
        return person


class ContractService:
    def __init__(self, db: Session):
        self.db = db
        self.contrat_repo = ContratRepository(db)
    
    def get_user_contracts(self, ref_personne: int, page: int = 1, size: int = 20) -> PaginatedContrats:
        try:
            logger.debug(f"Getting contracts for user {ref_personne}: page={page}, size={size}")
            skip = (page - 1) * size
            contracts = self.contrat_repo.get_by_user(ref_personne, skip, size)
            total = self.contrat_repo.count_by_user(ref_personne)
            pages = math.ceil(total / size)
            
            logger.info(f"Retrieved {len(contracts)} contracts for user {ref_personne} (page {page}/{pages})")
            return PaginatedContrats(
                items=contracts,
                total=total,
                page=page,
                size=size,
                pages=pages
            )
        except Exception as e:
            logger.error(f"Error getting contracts for user {ref_personne}: {e}")
            raise
    
    def get_contract_details(self, num_contrat: str, ref_personne: int) -> Contrat:
        contract = self.contrat_repo.get_by_num_contrat(num_contrat, ref_personne)
        if not contract:
            raise NotFoundError("Contract not found or you don't have permission to access it")
        
        return contract
    
    def get_contract_by_number(self, num_contrat: str, ref_personne: int) -> Contrat:
        """Get contract by number for a specific user - for agent access"""
        contract = self.contrat_repo.get_by_num_contrat(num_contrat, ref_personne)
        if not contract:
            raise NotFoundError("Contract not found")
        
        return contract


class ClaimService:
    def __init__(self, db: Session):
        self.db = db
        self.sinistre_repo = SinistreRepository(db)
    
    def get_user_claims(self, ref_personne: int, page: int = 1, size: int = 20) -> PaginatedSinistres:
        try:
            logger.debug(f"Getting claims for user {ref_personne}: page={page}, size={size}")
            skip = (page - 1) * size
            claims = self.sinistre_repo.get_by_user(ref_personne, skip, size)
            total = self.sinistre_repo.count_by_user(ref_personne)
            pages = math.ceil(total / size)
            
            logger.info(f"Retrieved {len(claims)} claims for user {ref_personne} (page {page}/{pages})")
            return PaginatedSinistres(
                items=claims,
                total=total,
                page=page,
                size=size,
                pages=pages
            )
        except Exception as e:
            logger.error(f"Error getting claims for user {ref_personne}: {e}")
            raise
    
    def get_claim_details(self, num_sinistre: str, ref_personne: int) -> Sinistre:
        claim = self.sinistre_repo.get_by_num_sinistre(num_sinistre, ref_personne)
        if not claim:
            raise NotFoundError("Claim not found or you don't have permission to access it")
        
        return claim
    
    def get_claim_by_number(self, num_sinistre: str, ref_personne: int) -> Sinistre:
        """Get claim by number for a specific user - for agent access"""
        claim = self.sinistre_repo.get_by_num_sinistre(num_sinistre, ref_personne)
        if not claim:
            raise NotFoundError("Claim not found")
        
        return claim
