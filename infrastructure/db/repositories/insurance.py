from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models import Account, PersonnePhysique, PersonneMorale, Contrat, Sinistre
from db.core.security import get_password_hash
import logging

# Configure logging
logger = logging.getLogger(__name__)


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_email(self, email: str) -> Optional[Account]:
        try:
            logger.debug(f"Searching for account with email: {email}")
            account = self.db.query(Account).filter(Account.email == email).first()
            if account:
                logger.debug(f"Account found: ref_personne={account.ref_personne}, role={account.role}")
            else:
                logger.debug(f"No account found for email: {email}")
            return account
        except Exception as e:
            logger.error(f"Database error while searching for email {email}: {e}")
            raise
    
    def get_by_ref_personne(self, ref_personne: int) -> Optional[Account]:
        try:
            logger.debug(f"Searching for account with ref_personne: {ref_personne}")
            account = self.db.query(Account).filter(Account.ref_personne == ref_personne).first()
            if account:
                logger.debug(f"Account found: email={account.email}, role={account.role}")
            else:
                logger.debug(f"No account found for ref_personne: {ref_personne}")
            return account
        except Exception as e:
            logger.error(f"Database error while searching for ref_personne {ref_personne}: {e}")
            raise
    
    def create(self, email: str, password: str, role: str, ref_personne: int) -> Account:
        try:
            logger.debug(f"Creating new account: email={email}, role={role}, ref_personne={ref_personne}")
            hashed_password = get_password_hash(password)
            account = Account(
                ref_personne=ref_personne,
                email=email,
                password_hash=hashed_password,
                role=role
            )
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
            logger.info(f"Account created successfully: {email}")
            return account
        except Exception as e:
            logger.error(f"Error creating account for {email}: {e}")
            self.db.rollback()
            raise
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Account]:
        try:
            logger.debug(f"Fetching accounts: skip={skip}, limit={limit}")
            accounts = self.db.query(Account).offset(skip).limit(limit).all()
            logger.debug(f"Retrieved {len(accounts)} accounts")
            return accounts
        except Exception as e:
            logger.error(f"Error fetching accounts: {e}")
            raise


class PersonnePhysiqueRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_ref_personne(self, ref_personne: int) -> Optional[PersonnePhysique]:
        return self.db.query(PersonnePhysique).filter(
            PersonnePhysique.ref_personne == ref_personne
        ).first()


class PersonneMoraleRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_ref_personne(self, ref_personne: int) -> Optional[PersonneMorale]:
        return self.db.query(PersonneMorale).filter(
            PersonneMorale.ref_personne == ref_personne
        ).first()


class ContratRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_user(self, ref_personne: int, skip: int = 0, limit: int = 100) -> List[Contrat]:
        try:
            logger.debug(f"Fetching contracts for user {ref_personne}: skip={skip}, limit={limit}")
            contracts = self.db.query(Contrat).filter(
                Contrat.ref_personne == ref_personne
            ).offset(skip).limit(limit).all()
            logger.debug(f"Retrieved {len(contracts)} contracts for user {ref_personne}")
            return contracts
        except Exception as e:
            logger.error(f"Error fetching contracts for user {ref_personne}: {e}")
            raise
    
    def get_by_num_contrat(self, num_contrat: str, ref_personne: int) -> Optional[Contrat]:
        try:
            logger.debug(f"Fetching contract {num_contrat} for user {ref_personne}")
            contract = self.db.query(Contrat).filter(
                and_(
                    Contrat.num_contrat == num_contrat,
                    Contrat.ref_personne == ref_personne
                )
            ).first()
            logger.debug(f"Contract {num_contrat} found: {contract is not None}")
            return contract
        except Exception as e:
            logger.error(f"Error fetching contract {num_contrat} for user {ref_personne}: {e}")
            raise
    
    def count_by_user(self, ref_personne: int) -> int:
        try:
            logger.debug(f"Counting contracts for user {ref_personne}")
            count = self.db.query(Contrat).filter(
                Contrat.ref_personne == ref_personne
            ).count()
            logger.debug(f"Contract count for user {ref_personne}: {count}")
            return count
        except Exception as e:
            logger.error(f"Error counting contracts for user {ref_personne}: {e}")
            raise


class SinistreRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_user(self, ref_personne: int, skip: int = 0, limit: int = 100) -> List[Sinistre]:
        try:
            logger.debug(f"Fetching claims for user {ref_personne}: skip={skip}, limit={limit}")
            # Join sinistres with contrats to filter by user
            claims = self.db.query(Sinistre).join(
                Contrat, Sinistre.num_contrat == Contrat.num_contrat
            ).filter(
                Contrat.ref_personne == ref_personne
            ).offset(skip).limit(limit).all()
            logger.debug(f"Retrieved {len(claims)} claims for user {ref_personne}")
            return claims
        except Exception as e:
            logger.error(f"Error fetching claims for user {ref_personne}: {e}")
            raise
    
    def get_by_num_sinistre(self, num_sinistre: str, ref_personne: int) -> Optional[Sinistre]:
        try:
            logger.debug(f"Fetching claim {num_sinistre} for user {ref_personne}")
            # Join sinistres with contrats to filter by user
            claim = self.db.query(Sinistre).join(
                Contrat, Sinistre.num_contrat == Contrat.num_contrat
            ).filter(
                and_(
                    Sinistre.num_sinistre == num_sinistre,
                    Contrat.ref_personne == ref_personne
                )
            ).first()
            logger.debug(f"Claim {num_sinistre} found: {claim is not None}")
            return claim
        except Exception as e:
            logger.error(f"Error fetching claim {num_sinistre} for user {ref_personne}: {e}")
            raise
    
    def count_by_user(self, ref_personne: int) -> int:
        try:
            logger.debug(f"Counting claims for user {ref_personne}")
            # Join sinistres with contrats to count by user
            count = self.db.query(Sinistre).join(
                Contrat, Sinistre.num_contrat == Contrat.num_contrat
            ).filter(
                Contrat.ref_personne == ref_personne
            ).count()
            logger.debug(f"Claim count for user {ref_personne}: {count}")
            return count
        except Exception as e:
            logger.error(f"Error counting claims for user {ref_personne}: {e}")
            raise
