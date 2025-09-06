from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

# Import logging configuration first
from db.core.logging_config import setup_logging

from db.core.config import settings
from db.core.exceptions import AuthenticationError, PermissionError, NotFoundError, ValidationError
from db.routers import (
    auth_router,
    accounts_router,
    contracts_router,
    claims_router,
    persons_router,
    agent_access_router,
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    description="A comprehensive FastAPI application for managing insurance database system with JWT authentication",
    version="1.0.0",
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("🚀 Insurance Management API is starting up...")
    logger.info(f"📋 Project: {settings.project_name}")
    logger.info(f"🔗 Database URL: {settings.database_url}")
    logger.info("📚 API Documentation available at /docs")

# Include routers
app.include_router(
    auth_router,
    prefix=f"{settings.api_v1_str}/auth",
    tags=["Authentication"]
)

app.include_router(
    accounts_router,
    prefix=f"{settings.api_v1_str}/accounts",
    tags=["Accounts"]
)

app.include_router(
    contracts_router,
    prefix=f"{settings.api_v1_str}/contracts",
    tags=["Contracts"]
)

app.include_router(
    claims_router,
    prefix=f"{settings.api_v1_str}/claims",
    tags=["Claims"]
)

app.include_router(
    persons_router,
    prefix=f"{settings.api_v1_str}/persons",
    tags=["Persons"]
)

app.include_router(
    agent_access_router,
    prefix=f"{settings.api_v1_str}/agent",
    tags=["Agent Access"]
)


# Exception handlers
@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(PermissionError)
async def permission_exception_handler(request: Request, exc: PermissionError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.project_name}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.project_name}",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_base": settings.api_v1_str
    }


