

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from bson import ObjectId
import config
import secrets
from models.schema import UserInDB, User, TokenData
import logging
import traceback
import urllib.parse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# MongoDB connection
client = MongoClient(config.MONGODB_URL)
db = client[config.DATABASE_NAME]
users_collection = db[config.USER_COLLECTION]
blacklist_collection = db["token_blacklist"]
password_reset_collection = db["password_reset_tokens"]

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(username: str):
    user_dict = users_collection.find_one({"username": username})
    if user_dict:
        # Convert _id to string id
        user_dict["id"] = str(user_dict.pop("_id"))
        # Ensure all required fields exist
        if "created_at" not in user_dict:
            user_dict["created_at"] = datetime.utcnow()
        if "is_active" not in user_dict:
            user_dict["is_active"] = True
        
        try:
            return UserInDB(**user_dict)
        except Exception as e:
            logger.error(f"Error creating UserInDB from user data: {str(e)}")
            logger.error(f"User dict: {user_dict}")
    return None

async def get_user_by_email(email: str):
    user_dict = users_collection.find_one({"email": email})
    if user_dict:
        # Convert _id to string id
        user_dict["id"] = str(user_dict.pop("_id"))
        # Ensure all required fields exist
        if "created_at" not in user_dict:
            user_dict["created_at"] = datetime.utcnow()
        if "is_active" not in user_dict:
            user_dict["is_active"] = True
        
        try:
            return UserInDB(**user_dict)
        except Exception as e:
            logger.error(f"Error creating UserInDB from email lookup: {str(e)}")
            logger.error(f"User dict: {user_dict}")
    return None

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def authenticate_user_by_email_or_username(login_id: str, password: str):
    """
    Authenticate user by either email or username
    """
    # First try to authenticate by email (if it looks like an email)
    if "@" in login_id:
        user = await get_user_by_email(login_id)
        if user and verify_password(password, user.hashed_password):
            return user
    
    # If not found or not an email, try username
    user = await get_user(login_id)
    if user and verify_password(password, user.hashed_password):
        return user
    
    return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def is_token_blacklisted(token: str):
    """Check if a token is in the blacklist"""
    return blacklist_collection.find_one({"token": token}) is not None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is blacklisted
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        logger.error("JWT Error during token validation")
        raise credentials_exception
    
    user = await get_user(username=token_data.username)
    if user is None:
        logger.error(f"User not found: {token_data.username}")
        raise credentials_exception
    
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at
    )

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def generate_password_reset_token(email: str):
    """
    Generate a unique token for password reset and store it in the database
    """
    try:
        # Find the user first
        user = await get_user_by_email(email)
        if not user:
            logger.info(f"User not found for email: {email}")
            return None
        
        # Generate a secure random token
        reset_token = secrets.token_urlsafe(32)
        
        # Set expiration time (24 hours from now)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # Create token with JWT as well (dual verification)
        token_data = {
            "sub": "password_reset",
            "email": email,
            "user_id": user.id,
            "exp": (datetime.utcnow() + timedelta(hours=24)).timestamp()
        }
        
        # Generate JWT token - this adds another layer of verification
        jwt_token = jwt.encode(token_data, config.SECRET_KEY, algorithm=config.ALGORITHM)
        
        # Store token in database
        # Delete any existing tokens for this user
        password_reset_collection.delete_many({"user_id": user.id})
        
        # Insert new token - store both the random token and JWT
        password_reset_collection.insert_one({
            "user_id": user.id,
            "email": email,
            "token": reset_token,  # URL-safe random token
            "jwt_token": jwt_token,  # JWT token with payload
            "expires_at": expires_at,
            "created_at": datetime.utcnow(),
            "is_used": False
        })
        
        logger.info(f"Generated reset token for {email}, expires at {expires_at}")
        
        # Return the URL-safe token
        return reset_token
    except Exception as e:
        logger.error(f"Error generating reset token: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def verify_password_reset_token(token: str):
    """
    Verify if the password reset token is valid
    """
    try:
        # Clean the token in case it was URL-encoded
        cleaned_token = urllib.parse.unquote(token)
        logger.info(f"Verifying token: {cleaned_token[:10]}...")
        
        password_reset_collection = db["password_reset_tokens"]
        token_data = password_reset_collection.find_one({"token": cleaned_token})
        
        # Log whether token was found
        if not token_data:
            logger.info("Token not found in database")
            return None
        
        logger.info(f"Token found for user_id: {token_data['user_id']}")
        
        # Check if token is used
        if token_data.get("is_used", False):
            logger.info("Token has already been used")
            return None
        
        # Check if token is expired
        current_time = datetime.utcnow()
        if token_data["expires_at"] < current_time:
            time_diff = current_time - token_data["expires_at"]
            logger.info(f"Token expired {time_diff} ago")
            return None
        
        logger.info("Token is valid")
        return token_data
    except Exception as e:
        logger.error(f"Error in verify_password_reset_token: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def reset_password(token: str, new_password: str):
    """
    Reset password using the reset token
    """
    try:
        # Clean the token in case it was URL-encoded
        cleaned_token = urllib.parse.unquote(token)
        
        # Verify token
        token_data = await verify_password_reset_token(cleaned_token)
        if not token_data:
            logger.error("Token verification failed during password reset")
            return False
        
        # Get user
        user_id = token_data["user_id"]
        
        # Get the user to confirm they exist
        user_obj = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user_obj:
            logger.error(f"User not found with ID: {user_id}")
            return False
        
        # Update password
        hashed_password = get_password_hash(new_password)
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"hashed_password": hashed_password}}
        )
        
        if result.modified_count == 0:
            logger.error(f"Failed to update password for user ID: {user_id}")
            return False
        
        # Mark token as used
        password_reset_collection.update_one(
            {"token": cleaned_token},
            {"$set": {"is_used": True}}
        )
        
        logger.info(f"Password successfully reset for user ID: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        logger.error(traceback.format_exc())
        return False

async def create_user(user_data):
    try:
        # Only check if email already exists, not username
        existing_email = users_collection.find_one({"email": user_data.email})
        if existing_email:
            logger.info(f"Email already exists: {user_data.email}")
            return None
        
        # Create new user
        user_dict = user_data.dict()
        user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        user_dict["created_at"] = datetime.utcnow()
        
        # Ensure is_active is set
        if "is_active" not in user_dict:
            user_dict["is_active"] = True
        
        result = users_collection.insert_one(user_dict)
        new_user = users_collection.find_one({"_id": result.inserted_id})
        
        if new_user:
            new_user["id"] = str(new_user.pop("_id"))
            return User(
                id=new_user["id"],
                username=new_user["username"],
                email=new_user["email"],
                is_active=new_user["is_active"],
                created_at=new_user["created_at"]
            )
        return None
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        logger.error(traceback.format_exc())
        raise