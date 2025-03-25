from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
from typing import List
import config
from utils import file_utils, excel_utils

router = APIRouter(prefix="/upload", tags=["uploads"])

@router.post("/resume", response_model=dict)
async def upload_resume(file: UploadFile = File(...)):
    """Upload and process a resume or template file"""
    # Check file extension
    filename = file.filename
    file_extension = filename.split('.')[-1].lower()
    
    if file_extension not in ['pdf', 'docx', 'txt']:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or TXT files.")
    
    # Save the file
    file_path = os.path.join(config.OUTPUT_DIR, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Extract text from the file
    try:
        extracted_text = file_utils.extract_text_from_file(file_path)
        return {
            "filename": filename,
            "file_path": file_path,
            "status": "success",
            "message": "File uploaded and processed successfully"
        }
    except Exception as e:
        # If there's an error, remove the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/skill-matrix", response_model=dict)
async def upload_skill_matrix(file: UploadFile = File(...)):
    """Upload and process a skill matrix Excel file"""
    # Check file extension
    filename = file.filename
    file_extension = filename.split('.')[-1].lower()
    
    if file_extension not in ['xlsx', 'xls']:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload Excel files only.")
    
    # Save the file
    file_path = os.path.join(config.OUTPUT_DIR, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Process the Excel file
    try:
        sheet_data = excel_utils.load_skill_matrix(file_path)
        
        # Count total records across all sheets
        total_records = sum(len(sheet["Data"]) for sheet in sheet_data)
        
        return {
            "filename": filename,
            "file_path": file_path,
            "status": "success",
            "sheets_processed": len(sheet_data),
            "total_records": total_records,
            "message": "Skill matrix uploaded and processed successfully"
        }
    except Exception as e:
        # If there's an error, remove the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing skill matrix: {str(e)}")

@router.post("/extract-employees", response_model=dict)
async def extract_employees(skillMatrix: UploadFile = File(...)):
    """Extract employees from uploaded skill matrix file"""
    # Check file extension
    filename = skillMatrix.filename
    file_extension = filename.split('.')[-1].lower()
    
    if file_extension not in ['xlsx', 'xls']:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload Excel files only.")
    
    # Read the file content
    content = await skillMatrix.read()
    
    try:
        # Process the Excel file from bytes
        sheets_data = excel_utils.load_skill_matrix_from_bytes(content)
        
        # Debug output
        print(f"Loaded {len(sheets_data)} sheets with data")
        print(f"Global sheets_data now has {len(config.sheets_data)} sheets")
        
        # Extract employee list
        employees = []
        
        for sheet in sheets_data:
            sheet_name = sheet["Sheet Name"]
            for record in sheet["Data"]:
                # Extract first name and last name considering both standardized and original column names
                first_name = None
                for key in ["First_Name", "First Name"]:
                    if key in record and isinstance(record[key], str):
                        first_name = record[key]
                        break
                
                last_name = None
                for key in ["Last_Name", "Last Name"]:
                    if key in record and isinstance(record[key], str):
                        last_name = record[key]
                        break
                
                if first_name and last_name:
                    employees.append({
                        "ID": record["ID"],
                        "first_name": first_name,
                        "last_name": last_name,
                        "sheet_name": sheet_name,
                        "full_name": f"{first_name} {last_name}"
                    })
        
        return {
            "success": True,
            "employees": employees,
            "message": f"Successfully extracted {len(employees)} employees from skill matrix"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting employees: {str(e)}")