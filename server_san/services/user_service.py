from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from models.schema import UserCreate, User, UserInDB
from database import get_db, SessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash a password for storing
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a stored password against a provided password
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_username(username: str) -> Optional[User]:
    """
    Get a user by username from the database
    """
    db = SessionLocal()
    try:
        # Implement this with your database model
        # Example: user = db.query(UserModel).filter(UserModel.username == username).first()
        # Return None if no user is found
        
        # This is a temporary workaround until you implement your database model
        from models.database_models import UserModel
        user_model = db.query(UserModel).filter(UserModel.username == username).first()
        
        if not user_model:
            return None
        
        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            full_name=user_model.full_name,
            is_active=user_model.is_active,
            created_at=user_model.created_at
        )
    finally:
        db.close()

def create_user(user_data: UserCreate) -> Optional[User]:
    """
    Create a new user in the database
    """
    db = SessionLocal()
    try:
        hashed_password = get_password_hash(user_data.password)
        
        # Implement this with your database model
        # Example: 
        from models.database_models import UserModel
        
        db_user = UserModel(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            created_at=db_user.created_at
        )
    except IntegrityError:
        db.rollback()
        return None
    finally:
        db.close()

def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password
    """
    user = get_user_by_username(username)
    if not user:
        return None
    
    # Get the hashed password from the database
    db = SessionLocal()
    try:
        from models.database_models import UserModel
        user_model = db.query(UserModel).filter(UserModel.username == username).first()
        if not user_model:
            return None
        
        if not verify_password(password, user_model.hashed_password):
            return None
        
        return user
    finally:
        db.close()