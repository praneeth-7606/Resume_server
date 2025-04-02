
from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks, Request
from bson import ObjectId
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import config
from models.schema import UserCreate, User, Token,ChangePasswordRequest
from services import auth_service
from pymongo import MongoClient
import logging
from pydantic import BaseModel
from typing import Optional
from services.auth_service import generate_password_reset_token, verify_password_reset_token, reset_password
from services.email_service import send_password_reset_email

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a SINGLE router for all auth endpoints
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}},
)

# MongoDB connection for token blacklist
client = MongoClient(config.MONGODB_URL)
db = client[config.DATABASE_NAME]
blacklist_collection = db["token_blacklist"]
users_collection = db[config.USER_COLLECTION]

# Define schema models
class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    password: str

@router.post("/signup", response_model=User)
async def signup(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if username already exists
        existing_user = users_collection.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        existing_email = users_collection.find_one({"email": user_data.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create the new user
        new_user = await auth_service.create_user(user_data)
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        return new_user
    except HTTPException:
        # Re-raise HTTP exceptions as is
        raise
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login to obtain JWT token"""
    try:
        # Try to authenticate with username or email
        # Note: The form_data.username field might actually contain an email
        user = await auth_service.authenticate_user_by_email_or_username(form_data.username, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        # Re-raise HTTP exceptions as is
        raise
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(auth_service.get_current_active_user), token: str = Depends(auth_service.oauth2_scheme)):
    """Logout and invalidate the current token"""
    try:
        # Add token to blacklist
        blacklist_collection.insert_one({"token": token})
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(auth_service.get_current_active_user)):
    """Get current user information"""
    try:
        return current_user
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Add the password reset endpoints to the SAME router
# @router.post("/forgot-password")
# async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks, req: Request):
#     """
#     Request a password reset link
#     """
#     try:
#         logger.info(f"Forgot password request for email: {request.email}")
        
#         # Generate password reset token
#         token = await generate_password_reset_token(request.email)
#         logger.info(f"Token generated: {token is not None}")
        
#         # If user not found, still return success (for security)
#         if not token:
#             return {"detail": "If your email is registered, you will receive a password reset link"}
        
#         # Create reset URL
#         reset_url = f"{req.base_url}reset-password?token={token}"
#         logger.info(f"Reset URL created: {reset_url}")
        
#         # Send reset email in background
#         try:
#             background_tasks.add_task(
#                 send_password_reset_email,
#                 request.email,
#                 reset_url
#             )
#             logger.info("Email task added to background tasks")
#         except Exception as email_err:
#             logger.error(f"Email service error: {str(email_err)}")
#             # Still return success to user (for security)
        
#         return {"detail": "Password reset link has been sent to your email"}
#     except Exception as e:
#         logger.error(f"Forgot password error: {str(e)}")
#         # Include traceback for more detailed error information
#         import traceback
#         logger.error(traceback.format_exc())
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Internal server error: {str(e)}"
#         )



@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks, req: Request):
    """
    Request a password reset link
    """
    try:
        logger.info(f"Processing password reset request for: {request.email}")
        
        # Generate password reset token
        token = await generate_password_reset_token(request.email)
        
        # If user not found, still return success (for security)
        if not token:
            logger.info(f"No user found for email: {request.email}, returning generic success")
            return {"detail": "If your email is registered, you will receive a password reset link"}
        
        # Create a properly formatted reset URL with your frontend address
        frontend_url = "http://localhost:3000"  # Your React frontend URL
        reset_url = f"{frontend_url}/reset-password?token={token}"
        
        logger.info(f"Generated reset URL for {request.email}")
        
        # Send reset email in background
        background_tasks.add_task(
            send_password_reset_email,
            request.email,
            reset_url
        )
        
        return {"detail": "Password reset link has been sent to your email"}
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
@router.get("/verify-reset-token")
async def verify_reset_token(token: str):
    """
    Verify if a reset token is valid
    """
    try:
        token_data = await verify_password_reset_token(token)
        if not token_data:
            return JSONResponse(
                content={"valid": False, "detail": "Invalid or expired token"},
                status_code=400
            )
        
        return {"valid": True, "email": token_data["email"]}
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return JSONResponse(
            content={"valid": False, "detail": "Error verifying token"},
            status_code=500
        )
@router.post("/reset-password")
async def password_reset(request: ResetPasswordRequest):
    """
    Reset password with token
    """
    # Validate password
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Reset password
    success = await reset_password(request.token, request.password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    return {"detail": "Password has been reset successfully"}




# Updated verify-reset-token endpoint for your auth router

@router.get("/verify-reset-token")
async def verify_reset_token(token: str):
    """
    Verify if a reset token is valid
    """
    try:
        logger.info(f"Verifying token: {token[:10]}...")
        
        # Ensure we're properly handling the token
        if not token or len(token) < 10:
            logger.warning("Token is missing or too short")
            return JSONResponse(
                content={"valid": False, "detail": "Invalid token format"},
                status_code=200
            )
            
        token_data = await verify_password_reset_token(token)
        
        if not token_data:
            logger.warning("Token verification failed: Invalid or expired token")
            return JSONResponse(
                content={"valid": False, "detail": "Invalid or expired token"},
                status_code=200
            )
        
        # Token is valid
        logger.info(f"Token verification successful for email: {token_data['email']}")
        return JSONResponse(
            content={"valid": True, "email": token_data["email"]},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            content={"valid": False, "detail": f"Error verifying token: {str(e)}"},
            status_code=200
        )


# Add this temporary endpoint for debugging
@router.get("/debug-tokens")
async def debug_tokens(token: Optional[str] = None):
    """
    Debug endpoint to check token database
    """
    password_reset_collection = db["password_reset_tokens"]
    
    if token:
        # Look for a specific token
        token_data = password_reset_collection.find_one({"token": token})
        if token_data:
            # Convert ObjectId to string for JSON serialization
            token_data["_id"] = str(token_data["_id"])
            token_data["user_id"] = str(token_data["user_id"])
            # Don't return the full token for security
            token_data["token"] = token_data["token"][:10] + "..." 
            return {"found": True, "token_data": token_data}
        else:
            return {"found": False, "message": "Token not found in database"}
    else:
        # Get count of tokens
        count = password_reset_collection.count_documents({})
        return {"token_count": count}







@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,  # Use the Pydantic model
    current_user: User = Depends(auth_service.get_current_active_user)
):
    try:
        # Debug information
        logger.info(f"Change password request received for user: {current_user.username}")
        
        # Extract data from request - now using the model
        current_password = password_data.current_password
        new_password = password_data.new_password
        
        # Validate request data
        if not current_password or not new_password:
            raise HTTPException(status_code=400, detail="Current password and new password are required")
        
        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
        # Get user from database by username or email
        # Try to find by username first
        user = users_collection.find_one({"username": current_user.username})
        if not user:
            # Try email as fallback
            user = users_collection.find_one({"email": current_user.email})
            if not user:
                logger.warning(f"User not found with username: {current_user.username}")
                raise HTTPException(status_code=404, detail="User not found")
        
        # Verify current password
        if not auth_service.verify_password(current_password, user["hashed_password"]):
            logger.warning(f"Incorrect password attempt for user: {current_user.username}")
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Hash the new password
        hashed_password = auth_service.get_password_hash(new_password)
        
        # Update the password in the database
        result = users_collection.update_one(
            {"_id": user["_id"]}, 
            {"$set": {"hashed_password": hashed_password}}
        )
        
        if result.modified_count == 0:
            logger.error(f"Failed to update password for user: {current_user.username}")
            raise HTTPException(status_code=500, detail="Failed to update password")
        
        logger.info(f"Password successfully updated for user: {current_user.username}")
        return {"detail": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")