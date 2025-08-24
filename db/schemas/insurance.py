from pydantic import BaseModel, EmailStr
from typing import Optional, TypeVar, Generic, List
from datetime import date
from decimal import Decimal


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Account Schemas
class AccountBase(BaseModel):
    email: EmailStr
    role: str


class AccountCreate(AccountBase):
    password: str


class Account(AccountBase):
    ref_personne: int
    
    class Config:
        from_attributes = True


# PersonnePhysique Schemas
class PersonnePhysiqueBase(BaseModel):
    nom_prenom: str
    date_naissance: Optional[date] = None
    lieu_naissance: Optional[str] = None
    code_sexe: Optional[str] = None
    situation_familiale: Optional[str] = None
    num_piece_identite: Optional[str] = None
    lib_secteur_activite: Optional[str] = None
    lib_profession: Optional[str] = None
    ville: Optional[str] = None
    lib_gouvernorat: Optional[str] = None
    ville_gouvernorat: Optional[str] = None


class PersonnePhysique(PersonnePhysiqueBase):
    ref_personne: int
    
    class Config:
        from_attributes = True


# PersonneMorale Schemas
class PersonneMoraleBase(BaseModel):
    raison_sociale: str
    matricule_fiscale: Optional[str] = None
    num_secteur_activite: Optional[str] = None
    lib_activite: Optional[str] = None
    ville: Optional[str] = None
    lib_gouvernorat: Optional[str] = None
    ville_gouvernorat: Optional[str] = None


class PersonneMorale(PersonneMoraleBase):
    ref_personne: int
    
    class Config:
        from_attributes = True


# GarantieContrat Schemas
class GarantieContratBase(BaseModel):
    num_contrat: str
    code_garantie: int
    lib_garantie: Optional[str] = None


class GarantieContrat(GarantieContratBase):
    class Config:
        from_attributes = True


# Contrat Schemas
class ContratBase(BaseModel):
    num_contrat: str
    lib_produit: Optional[str] = None
    effet_contrat: Optional[date] = None
    date_expiration: Optional[date] = None  # Changed from duree_expiration
    prochain_terme: Optional[str] = None
    lib_etat_contrat: Optional[str] = None
    branche: Optional[str] = None
    somme_quittances: Optional[Decimal] = None  # Changed from somme_guittances
    statut_paiement: Optional[str] = None
    capital_assure: Optional[Decimal] = None


class Contrat(ContratBase):
    ref_personne: int
    garanties: list[GarantieContrat] = []
    
    class Config:
        from_attributes = True


# Sinistre Schemas
class SinistreBase(BaseModel):
    num_sinistre: str
    lib_branche: Optional[str] = None
    lib_sous_branche: Optional[str] = None
    lib_produit: Optional[str] = None
    nature_sinistre: Optional[str] = None
    lib_type_sinistre: Optional[str] = None
    taux_responsabilite: Optional[Decimal] = None
    date_survenance: Optional[date] = None
    date_declaration: Optional[date] = None
    date_ouverture: Optional[date] = None
    observation_sinistre: Optional[str] = None
    lib_etat_sinistre: Optional[str] = None
    lieu_accident: Optional[str] = None
    motif_reouverture: Optional[str] = None
    montant_encaisse: Optional[Decimal] = None
    montant_a_encaisser: Optional[Decimal] = None


class Sinistre(SinistreBase):
    num_contrat: str
    # Note: ref_personne is not available directly in sinistres table
    # It's accessible through the contract relationship
    
    class Config:
        from_attributes = True


# User Profile Schema
class UserProfile(BaseModel):
    account: Account
    personal_info: Optional[PersonnePhysique | PersonneMorale] = None
    
    class Config:
        from_attributes = True


# Pagination Schemas
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

# Specific paginated response types
class PaginatedContrats(BaseModel):
    items: List[Contrat]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True

class PaginatedSinistres(BaseModel):
    items: List[Sinistre]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True
