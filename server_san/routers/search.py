# from fastapi import APIRouter, HTTPException
# from typing import List
# import config
# from models.schema import NameQuery, EmployeeInfo, EmployeeIdQuery
# from utils import excel_utils

# router = APIRouter(prefix="/search", tags=["search"])

# @router.post("/by-id", response_model=List[dict])
# async def search_by_id(query: EmployeeIdQuery):
#     """Search for a person in the skill matrix by ID"""
#     if not config.sheets_data:
#         raise HTTPException(status_code=400, detail="No skill matrix data loaded. Please upload a skill matrix file first.")
    
#     results = excel_utils.get_json_by_id(query.employee_id)
    
#     if not results:
#         raise HTTPException(status_code=404, detail=f"No employee found with ID {query.employee_id}")
    
#     return results

# @router.post("/by-name", response_model=List[dict])
# async def search_by_name(query: NameQuery):
#     """Search for a person in the skill matrix by name"""
#     if not config.sheets_data:
#         raise HTTPException(status_code=400, detail="No skill matrix data loaded. Please upload a skill matrix file first.")
    
#     results = excel_utils.get_json_by_name(query.first_name, query.last_name)
    
#     # If no results found, try case-insensitive search
#     if not results:
#         # Try case-insensitive search
#         results = []
#         for sheet in config.sheets_data:
#             for record in sheet["Data"]:
#                 # Check both standardized and possible original column names with case insensitivity
#                 fn_keys = ["First_Name", "First Name"] 
#                 ln_keys = ["Last_Name", "Last Name"]
                
#                 fn_match = False
#                 for key in fn_keys:
#                     if key in record and isinstance(record[key], str) and record[key].lower() == query.first_name.lower():
#                         fn_match = True
#                         break
                
#                 ln_match = False
#                 for key in ln_keys:
#                     if key in record and isinstance(record[key], str) and record[key].lower() == query.last_name.lower():
#                         ln_match = True
#                         break
                
#                 if fn_match and ln_match:
#                     # Include sheet name in record for context
#                     record_with_sheet = record.copy()
#                     record_with_sheet["Sheet Name"] = sheet["Sheet Name"]
#                     results.append(record_with_sheet)
    
#     return results

# @router.get("/employees/list", response_model=List[EmployeeInfo])
# async def get_employee_list():
#     """Get the list of all employees from the loaded skill matrix"""
#     if not config.sheets_data:
#         raise HTTPException(status_code=400, detail="No skill matrix data loaded. Please upload a skill matrix file first.")
    
#     employee_list = []
    
#     for sheet in config.sheets_data:
#         sheet_name = sheet["Sheet Name"]
#         for record in sheet["Data"]:
#             # Extract first name and last name considering both standardized and original column names
#             first_name = None
#             for key in ["First_Name", "First Name"]:
#                 if key in record and isinstance(record[key], str):
#                     first_name = record[key]
#                     break
            
#             last_name = None
#             for key in ["Last_Name", "Last Name"]:
#                 if key in record and isinstance(record[key], str):
#                     last_name = record[key]
#                     break
            
#             if first_name and last_name:
#                 employee_list.append(
#                     EmployeeInfo(
#                         ID=record["ID"],
#                         first_name=first_name,
#                         last_name=last_name,
#                         sheet_name=sheet_name
#                     )
#                 )
    
#     return employee_list



from fastapi import APIRouter, HTTPException
from typing import List
import config
from models.schema import NameQuery, EmployeeInfo, EmployeeIdQuery
from utils import excel_utils

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/by-id", response_model=List[dict])
async def search_by_id(query: EmployeeIdQuery):
    """Search for a person in the skill matrix by ID"""
    if not config.sheets_data:
        raise HTTPException(status_code=400, detail="No skill matrix data loaded. Please upload a skill matrix file first.")
    
    results = excel_utils.get_json_by_id(query.employee_id)
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No employee found with ID {query.employee_id}")
    
    return results

@router.post("/by-name", response_model=List[dict])
async def search_by_name(query: NameQuery):
    """Search for a person in the skill matrix by name"""
    if not config.sheets_data:
        raise HTTPException(status_code=400, detail="No skill matrix data loaded. Please upload a skill matrix file first.")
    
    results = excel_utils.get_json_by_name(query.first_name, query.last_name)
    
    # If no results found, try case-insensitive search
    if not results:
        # Try case-insensitive search
        results = []
        for sheet in config.sheets_data:
            for record in sheet["Data"]:
                # Check both standardized and possible original column names with case insensitivity
                fn_keys = ["First_Name", "First Name"] 
                ln_keys = ["Last_Name", "Last Name"]
                
                fn_match = False
                for key in fn_keys:
                    if key in record and isinstance(record[key], str) and record[key].lower() == query.first_name.lower():
                        fn_match = True
                        break
                
                ln_match = False
                for key in ln_keys:
                    if key in record and isinstance(record[key], str) and record[key].lower() == query.last_name.lower():
                        ln_match = True
                        break
                
                if fn_match and ln_match:
                    # Include sheet name in record for context
                    record_with_sheet = record.copy()
                    record_with_sheet["Sheet Name"] = sheet["Sheet Name"]
                    results.append(record_with_sheet)
    
    return results

@router.get("/employees/list", response_model=List[EmployeeInfo])
async def get_employee_list():
    """Get the list of all employees from the loaded skill matrix"""
    if not config.sheets_data:
        # For debugging, log what's in sheets_data
        print(f"sheets_data is empty or not properly loaded: {config.sheets_data}")
        raise HTTPException(status_code=400, detail="No skill matrix data loaded. Please upload a skill matrix file first.")
    
    employee_list = []
    
    for sheet in config.sheets_data:
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
                employee_list.append(
                    EmployeeInfo(
                        ID=record["ID"],
                        first_name=first_name,
                        last_name=last_name,
                        sheet_name=sheet_name
                    )
                )
    
    return employee_list