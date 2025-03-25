import json
import os
from typing import List, Dict, Any, Optional
import config
# from utils import file_utils
from utils import *
from services import llm_service

def create_prompts():
    """Create default prompt files if they don't exist"""
    llm1_path = os.path.join(config.PROMPTS_DIR, "LLM1.txt")
    if not os.path.exists(llm1_path):
        with open(llm1_path, "w") as f:
            f.write("""
You are an AI assistant that extracts structured information from resumes.
Your task is to analyze the provided resume text and extract key details into a well-structured JSON format.

The JSON structure should include:
{
  "name": "Full Name",
  "designation": "Job Title/Role",
  "objective": "Professional summary/objective statement",
  "education": ["Degree 1", "Degree 2"],
  "skills": ["Skill 1", "Skill 2", "Skill 3"],
  "project_details": {
    "project1": {
      "name": "Project Name",
      "role": "Role in Project",
      "description": "Brief description of the project",
      "technology": "Technologies used",
      "role_played": "Responsibilities and contributions"
    },
    "project2": {
      "name": "Project Name",
      "role": "Role in Project",
      "description": "Brief description of the project",
      "technology": "Technologies used",
      "role_played": "Responsibilities and contributions"
    }
  }
}

Follow these guidelines:
1. Extract information ONLY from the provided text.
2. Do not invent or add details that aren't present in the original text.
3. Format the output as valid JSON that strictly adheres to the structure above.
4. If certain information is missing, use empty strings or arrays rather than omitting fields.
5. Include at least 2-3 projects if available in the resume.
6. Organize skills in a logical manner, grouping similar skills together.
7. Be concise but comprehensive in extracting information.
8. Ensure all JSON is properly formatted and valid.
            """)

def process_template_json(template_text: str) -> Dict:
    """Process template and extract JSON schema"""
    try:
        template_json_str = llm_service.LLM_CALL_1(template_text)
        
        # Clean up the JSON string to ensure it's valid
        template_json_str = template_json_str.replace('```json', '').replace('```', '').strip()
        
        try:
            print("template_json_str",template_json_str)
            print("type of the json schema",type(template_json_str))
            formatted_json_schema = json.loads(template_json_str)
            print("Type of the formatted Json after loads:",type(formatted_json_schema))
            
            return formatted_json_schema
        except json.JSONDecodeError as e:
            # If template JSON parsing fails, use a default schema
            print(f"Error parsing template JSON: {e}, using default schema")
            return {
                "name": "",
                "designation": "",
                "objective": "",
                "education": [],
                "skills": [],
                "project_details": {}
            }
    except Exception as e:
        print(f"Error in LLM_CALL_1: {str(e)}")
        # Use default schema if LLM call fails
        return {
            "name": "",
            "designation": "",
            "objective": "",
            "education": [],
            "skills": [],
            "project_details": {}
        }

def process_resume_data(
    formatted_json_schema: Dict,
    old_resume_text: Optional[str] = None,
    old_cover_letter_text: Optional[str] = None,
    skill_matrix_json: Optional[str] = None
) -> Dict:
    """Process input data and generate resume JSON based on available inputs"""
    try:
        # Call appropriate LLM function based on available inputs
        if old_resume_text and old_cover_letter_text and skill_matrix_json:
            # All three inputs available
            resume_content = llm_service.LLM_CALL_8(formatted_json_schema, old_resume_text, old_cover_letter_text, skill_matrix_json)
            print("Resume content after LLM_CALL_8",resume_content)
        elif old_resume_text and skill_matrix_json:
            # Old resume and skill matrix
            resume_content = llm_service.LLM_CALL_2(formatted_json_schema, old_resume_text, skill_matrix_json)
            print("Resume content after LLM_CALL_2",resume_content)
        elif old_cover_letter_text and skill_matrix_json:
            # Cover letter and skill matrix
            resume_content = llm_service.LLM_CALL_3(formatted_json_schema, old_cover_letter_text, skill_matrix_json)
            print("Resume content after LLM_CALL_3",resume_content)
        elif old_resume_text and old_cover_letter_text:
            # Old resume and cover letter
            resume_content = llm_service.LLM_CALL_4(formatted_json_schema, old_resume_text, old_cover_letter_text)
            print("Resume content after LLM_CALL_4",resume_content)
        elif old_resume_text:
            # Only old resume
            resume_content = llm_service.LLM_CALL_5(formatted_json_schema, old_resume_text)
            print("Resume content after LLM_CALL_5",resume_content)
        elif old_cover_letter_text:
            # Only cover letter
            resume_content = llm_service.LLM_CALL_6(formatted_json_schema, old_cover_letter_text)
            print("Resume content after LLM_CALL_6",resume_content)
        elif skill_matrix_json:
            # Only skill matrix
            resume_content = llm_service.LLM_CALL_7(formatted_json_schema, skill_matrix_json)
            print("Resume content after LLM_CALL_7",resume_content)
        else:
            # No inputs provided
            return {
                "name": "Candidate",
                "designation": "Professional",
                "objective": "Experienced professional seeking new opportunities.",
                "education": ["Education details not provided"],
                "skills": ["Skills not provided"],
                "project_details": {
                    "project1": {
                        "name": "Project",
                        "role": "Team Member",
                        "description": "Project description not provided",
                        "technology": "Technologies not provided",
                        "role_played": "Role details not provided"
                    }
                }
            }
            
        # Ensure we have valid JSON
        try:
            resume_data = json.loads(resume_content)
            return resume_data
        except json.JSONDecodeError as e:
            # Clean up the JSON if necessary
            print(f"Error parsing generated JSON: {e}, attempting to clean")
            clean_json = resume_content.replace('```json', '').replace('```', '').strip()
            try:
                resume_data = json.loads(clean_json)
                return resume_data
            except json.JSONDecodeError:
                # If still failing, create minimal valid JSON
                print("Error parsing cleaned JSON, using minimal data")
                # Extract name from resume if available
                name = "Candidate"
                if old_resume_text:
                    for line in old_resume_text.split('\n'):
                        if line.strip() and len(line.strip()) < 50:  # Simple heuristic to find a name
                            name = line.strip()
                            break
                
                return {
                    "name": name,
                    "designation": "Professional",
                    "objective": "Experienced professional seeking new opportunities.",
                    "education": ["Education details not extracted"],
                    "skills": ["Skills not extracted"],
                    "project_details": {
                        "project1": {
                            "name": "Project",
                            "role": "Team Member",
                            "description": "Project description not extracted",
                            "technology": "Technologies not extracted",
                            "role_played": "Role details not extracted"
                        }
                    }
                }
    except Exception as e:
        print(f"Error in processing resume data: {str(e)}")
        # Create minimal valid JSON if processing fails
        name = "Candidate"
        if old_resume_text:
            for line in old_resume_text.split('\n'):
                if line.strip() and len(line.strip()) < 50:
                    name = line.strip()
                    break
                
        return {
            "name": name,
            "designation": "Professional",
            "objective": "Experienced professional seeking new opportunities.",
            "education": ["Education details not extracted"],
            "skills": ["Skills not extracted"],
            "project_details": {
                "project1": {
                    "name": "Project",
                    "role": "Team Member",
                    "description": "Project description not extracted",
                    "technology": "Technologies not extracted",
                    "role_played": "Role details not extracted"
                }
            }
        }