from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class NameQuery(BaseModel):
    first_name: str
    last_name: str

class EmployeeInfo(BaseModel):
    ID: int
    first_name: str
    last_name: str
    sheet_name: str

class ResumeRequest(BaseModel):
    template_path: str
    old_resume_path: Optional[str] = None
    old_cover_letter_path: Optional[str] = None
    cover_letter_path: Optional[str] = None  # Alternative name
    skill_matrix_path: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    template_id: Optional[int] = 1  # Change parameter name from template_type to template_id
    
    # Add a method to get the cover letter path from either field
    def get_cover_letter_path(self):
        return self.old_cover_letter_path or self.cover_letter_path

class EmployeeIdQuery(BaseModel):
    employee_id: int






# User models
class UserBase(BaseModel):
    email: EmailStr
    username: str
    
class UserCreate(UserBase):
    password: str
    is_active: bool = True
    
# class UserInDB(UserBase):
#     hashed_password: str
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     is_active: bool = True
    
class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    class Config:
        orm_mode = True 

# models/schema.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserInDB(BaseModel):
    id: str  # This field is missing and causing the error
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.now()
    
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None



class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: Optional[str] = None