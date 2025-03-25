import pandas as pd
import io
from typing import List, Dict, Any
import config

def load_skill_matrix(file_path: str) -> List[dict]:
    """Load and process skill matrix Excel file from path"""
    config.sheets_data = []
    
    # Load Excel file
    xls = pd.ExcelFile(file_path)
    record_id = 1  # Unique number for each entry
    
    # Process all sheets from the second one onward
    for sheet_name in xls.sheet_names[1:]:  # Skip the first sheet
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Standardize column names to ensure consistency
        if len(df.columns) >= 4:
            # Create standardized column names
            std_columns = ['First_Name', 'Last_Name', 'Experience', 'Expertise'] + list(df.columns[4:])
            
            # Map original columns to standardized names
            column_mapping = {original: standard for original, standard in zip(df.columns, std_columns)}
            df = df.rename(columns=column_mapping)
        
        # Convert each sheet's data to a list of dictionaries with unique numbers
        records = []
        for _, row in df.iterrows():
            record = {"ID": record_id}  # Assign a unique ID
            record.update(row.to_dict())  # Convert row data to dictionary
            records.append(record)
            record_id += 1  # Increment unique ID
        
        sheet_dict = {
            "Sheet Name": sheet_name,
            "Data": records
        }
        
        config.sheets_data.append(sheet_dict)
    
    return config.sheets_data

def load_skill_matrix_from_bytes(file_content: bytes) -> List[dict]:
    """Load and process skill matrix Excel file from bytes"""
    # Clear existing data
    config.sheets_data = []
    
    # Load Excel file from bytes
    xls = pd.ExcelFile(io.BytesIO(file_content))
    record_id = 1  # Unique number for each entry
    
    # Debug output
    print(f"Processing Excel file with sheets: {xls.sheet_names}")
    
    # Process all sheets from the second one onward
    for sheet_name in xls.sheet_names[1:]:  # Skip the first sheet
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Standardize column names to ensure consistency
        if len(df.columns) >= 4:
            # Create standardized column names
            std_columns = ['First_Name', 'Last_Name', 'Experience', 'Expertise'] + list(df.columns[4:])
            
            # Map original columns to standardized names
            column_mapping = {original: standard for original, standard in zip(df.columns, std_columns)}
            df = df.rename(columns=column_mapping)
        
        # Convert each sheet's data to a list of dictionaries with unique numbers
        records = []
        for _, row in df.iterrows():
            record = {"ID": record_id}  # Assign a unique ID
            record.update(row.to_dict())  # Convert row data to dictionary
            records.append(record)
            record_id += 1  # Increment unique ID
        
        sheet_dict = {
            "Sheet Name": sheet_name,
            "Data": records
        }
        
        config.sheets_data.append(sheet_dict)
    
    return config.sheets_data

def get_json_by_name(first_name: str, last_name: str) -> List[dict]:
    """Search for records by first and last name"""
    results = []
    for sheet in config.sheets_data:
        for record in sheet["Data"]:
            # Check both standardized and possible original column names with case insensitivity
            fn_keys = ["First_Name", "First Name"] 
            ln_keys = ["Last_Name", "Last Name"]
            
            fn_match = False
            for key in fn_keys:
                if key in record and isinstance(record[key], str) and record[key].lower() == first_name.lower():
                    fn_match = True
                    break
            
            ln_match = False
            for key in ln_keys:
                if key in record and isinstance(record[key], str) and record[key].lower() == last_name.lower():
                    ln_match = True
                    break
            
            if fn_match and ln_match:
                # Include sheet name in record for context
                record_with_sheet = record.copy()
                record_with_sheet["Sheet Name"] = sheet["Sheet Name"]
                results.append(record_with_sheet)
    
    return results

def get_json_by_id(employee_id: int) -> List[dict]:
    """Search for records by employee ID"""
    results = []
    for sheet in config.sheets_data:
        for record in sheet["Data"]:
            if "ID" in record and record["ID"] == employee_id:
                # Include sheet name in record for context
                record_with_sheet = record.copy()
                record_with_sheet["Sheet Name"] = sheet["Sheet Name"]
                results.append(record_with_sheet)
                # Since ID should be unique, we can break after finding the match
                return results
    
    return results