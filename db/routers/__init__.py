# Routers package
from .auth import router as auth_router
from .accounts import router as accounts_router
from .contracts import router as contracts_router
from .claims import router as claims_router
from .persons import router as persons_router
from .agent_access import router as agent_access_router

__all__ = [
    "auth_router",
    "accounts_router",
    "contracts_router",
    "claims_router",
    "persons_router",
    "agent_access_router",
]
