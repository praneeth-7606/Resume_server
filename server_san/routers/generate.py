from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
import json
import traceback
from typing import Dict, Any
import config
from models.schema import ResumeRequest
from utils import file_utils, excel_utils
from services import llm_service, data_service
from utils.template_manager import generate_resume, generate_cover_letter, get_available_templates

router = APIRouter(prefix="/generate", tags=["generate"])

@router.get("/templates")
async def list_templates():
    """Get a list of available resume and cover letter templates"""
    try:
        templates = get_available_templates()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving templates: {str(e)}")

@router.post("/resume", response_model=dict)
async def generate_resume_route(request: ResumeRequest, background_tasks: BackgroundTasks):
    """Generate a new resume based on template and input files"""
    # Validate that template exists
    if not os.path.exists(request.template_path):
        raise HTTPException(status_code=400, detail="Template file not found. Please upload a template first.")
    
    try:
        # Extract template text
        template_text = file_utils.extract_text_from_file(request.template_path)
        print("Templete text for input",template_text)
        
        # Step 1: Extract structured JSON from template
        formatted_json_schema = data_service.process_template_json(template_text)
        print("formatted_json_schema",formatted_json_schema)
        
        # Get input files content if available
        old_resume_text = None
        old_cover_letter_text = None
        skill_matrix_json = None
        
        if request.old_resume_path and os.path.exists(request.old_resume_path):
            old_resume_text = file_utils.extract_text_from_file(request.old_resume_path)
            
        
        if request.old_cover_letter_path and os.path.exists(request.old_cover_letter_path):
            old_cover_letter_text = file_utils.extract_text_from_file(request.old_cover_letter_path)
        
        if request.skill_matrix_path and os.path.exists(request.skill_matrix_path):
            # If first name and last name are provided, get specific data
            if request.first_name and request.last_name:
                skill_matrix_data = excel_utils.get_json_by_name(request.first_name, request.last_name)
                if skill_matrix_data:
                    skill_matrix_json = json.dumps(skill_matrix_data)
            else:
                # Use the whole file content with explicit UTF-8 encoding
                with open(request.skill_matrix_path, 'r', encoding='utf-8', errors='replace') as f:
                    skill_matrix_json = f.read()
        print("old_resume_text",old_resume_text)
        print("old_cover_letter_text",old_cover_letter_text)
        print("skill_matrix_json",skill_matrix_json)

        # Step 2: Process the resume data
        resume_data = data_service.process_resume_data(
            formatted_json_schema,
            old_resume_text,
            old_cover_letter_text,
            skill_matrix_json
        )
        
        # Log the template_id coming from the frontend
        print(f"Received template_id: {request.template_id}")
        
        # Get the selected template ID (default to 1 if not specified)
        template_id = request.template_id if request.template_id is not None else 1
            
        # Step 3: Generate the resume PDF with the selected template
        try:
            resume_path = generate_resume(resume_data, template_id)
            
            # Verify the file was created
            if not os.path.exists(resume_path):
                raise Exception("The resume PDF file was not created.")
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            print(traceback.format_exc())
            
            # Create a simple PDF with basic information
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            
            # Get name or fallback
            candidate_name = resume_data.get("name", "Candidate") if isinstance(resume_data, dict) else "Candidate"
            pdf.cell(0, 10, candidate_name, ln=True, align="L")
            
            pdf.set_font("Arial", "", 11)
            pdf.multi_cell(0, 7, "An error occurred while generating the complete resume.")
            pdf.ln(10)
            pdf.multi_cell(0, 7, f"Error details: {str(e)}")
            pdf.ln(10)
            pdf.multi_cell(0, 7, "Please try again or contact support if the issue persists.")
            
            resume_path = os.path.join(config.OUTPUT_DIR, f"Error_Resume.pdf")
            pdf.output(resume_path)
        
        # Step 4: Generate a cover letter with the same template style
        cover_letter_status = "Not generated"
        try:
            candidate_name = resume_data.get("name", "Candidate") if isinstance(resume_data, dict) else "Candidate"
            cover_letter_text = llm_service.generate_cover_letter_from_resume(resume_data)
            
            if not cover_letter_text or len(cover_letter_text.strip()) < 10:
                raise Exception("Generated cover letter text is too short or empty")
                
            cover_letter_path = generate_cover_letter(resume_data, cover_letter_text, template_id)
            
            # Verify the file was created
            if not os.path.exists(cover_letter_path):
                raise Exception("The cover letter PDF file was not created.")
                
            cover_letter_status = "Generated successfully"
        except Exception as e:
            error_detail = str(e)
            cover_letter_status = f"Failed to generate: {error_detail}"
            print(f"Error generating cover letter: {error_detail}")
            print(traceback.format_exc())
            
            # Try to create a simple error cover letter
            try:
                candidate_name = resume_data.get("name", "Candidate") if isinstance(resume_data, dict) else "Candidate"
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, f"{candidate_name} - Cover Letter Error", ln=True, align="L")
                pdf.set_font("Arial", "", 11)
                pdf.multi_cell(0, 7, "An error occurred while generating the cover letter.")
                pdf.ln(5)
                pdf.multi_cell(0, 7, f"Error details: {error_detail}")
                
                cover_letter_path = os.path.join(config.OUTPUT_DIR, f"Error_Cover_Letter.pdf")
                pdf.output(cover_letter_path)
            except:
                # If this fails too, just log it
                print("Failed to generate error cover letter PDF")
        
        return {
            "message": "Resume generated successfully",
            "resume_path": resume_path,
            "cover_letter_status": cover_letter_status,
            "template_used": template_id  # Return the template ID used
        }
    
    except Exception as e:
        error_detail = str(e)
        print(f"Error in generate_resume endpoint: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating resume: {error_detail}")

@router.get("/download/{filename}")
async def download_file(filename: str):
    """Endpoint to download generated files"""
    file_path = os.path.join(config.OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=filename)