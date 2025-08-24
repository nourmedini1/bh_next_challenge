from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.dependencies import get_db, get_current_active_user
from db.services import AuthService, UserService
from db.schemas import Token, LoginRequest, UserProfile
from db.models import Account
from db.core.exceptions import AuthenticationError
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    - **username**: User email address
    - **password**: User password
    """
    try:
        logger.info(f"Login attempt for username: {form_data.username}")
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(form_data.username, form_data.password)
        
        if not user:
            logger.warning(f"Authentication failed for username: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = auth_service.create_token_for_user(user)
        logger.info(f"Login successful for user: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login for {form_data.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )


@router.post("/login-json", response_model=Token)
async def login_json(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with JSON payload and return JWT token.
    
    - **email**: User email address
    - **password**: User password
    """
    try:
        logger.info(f"JSON login attempt for email: {login_data.email}")
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            logger.warning(f"JSON authentication failed for email: {login_data.email}")
            raise AuthenticationError("Incorrect email or password")
        
        access_token = auth_service.create_token_for_user(user)
        logger.info(f"JSON login successful for user: {login_data.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during JSON login for {login_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: Account = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user profile including personal information.
    """
    try:
        logger.debug(f"Getting profile for user: {current_user.email}")
        user_service = UserService(db)
        profile = user_service.get_user_profile(current_user.ref_personne)
        
        if not profile:
            logger.error(f"Profile not found for user: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        logger.debug(f"Profile retrieved successfully for user: {current_user.email}")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile error: {str(e)}"
        )
