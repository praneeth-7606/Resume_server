from pydantic import BaseModel
from typing import List, Optional, Dict, Any

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