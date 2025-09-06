# Schemas package
from .insurance import (
    Token,
    TokenData,
    LoginRequest,
    Account,
    AccountCreate,
    PersonnePhysique,
    PersonneMorale,
    Contrat,
    GarantieContrat,
    Sinistre,
    UserProfile,
    PaginatedResponse,
    PaginatedContrats,
    PaginatedSinistres,
)

__all__ = [
    "Token",
    "TokenData", 
    "LoginRequest",
    "Account",
    "AccountCreate",
    "PersonnePhysique",
    "PersonneMorale",
    "Contrat", 
    "GarantieContrat",
    "Sinistre",
    "UserProfile",
    "PaginatedResponse",
    "PaginatedContrats",
    "PaginatedSinistres",
]
