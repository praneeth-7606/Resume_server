from fpdf import FPDF


import os
import json
import re
import traceback
from .template_2 import generate_resume_2
#from .template_manager import generate_cover_letter_2
import config
# from utils.template_pdf import generate_resume_2, generate_cover_letter_2
import os
import config



def generate_resume(data, template_type=1):
    """
    Generate a resume with the specified template
    
    Args:
        data: Resume data (dict or JSON string)
        template_type: 1 for standard, 2 for new template
        
    Returns:
        Path to the generated PDF
    """
    try:
        if template_type == 2:
            # Get the filename without generating the file yet
            if isinstance(data, dict):
                name = data.get('name', 'Resume')
            else:
                try:
                    data_dict = json.loads(data)
                    name = data_dict.get('name', 'Resume')
                except:
                    name = 'Resume'
                    
            # Generate with template 2
            filename = generate_resume_2(data)
            
            # Move the file to the output directory if needed
            if os.path.dirname(filename) != config.OUTPUT_DIR:
                new_path = os.path.join(config.OUTPUT_DIR, os.path.basename(filename))
                os.rename(filename, new_path)
                return new_path
            return filename
        else:
            # Use the original template
            return generate_resume_1(data)
    except Exception as e:
        print(f"Error generating resume with template {template_type}: {str(e)}")
        raise

def generate_cover_letter(data, cover_letter_text, template_type=1):
    """
    Generate a cover letter with the specified template
    
    Args:
        data: Resume/candidate data (dict or JSON string)
        cover_letter_text: Text for the cover letter
        template_type: 1 for standard, 2 for new template
        
    Returns:
        Path to the generated PDF
    """
    try:
        if template_type == 2:
            # Get the candidate name
            if isinstance(data, dict):
                name = data.get('name', 'Candidate')
            else:
                try:
                    data_dict = json.loads(data)
                    name = data_dict.get('name', 'Candidate')
                except:
                    name = 'Candidate'
            
            # Generate with template 2
            filename = generate_cover_letter_2(data, cover_letter_text)
            
            # Move the file to the output directory if needed
            if os.path.dirname(filename) != config.OUTPUT_DIR:
                new_path = os.path.join(config.OUTPUT_DIR, os.path.basename(filename))
                os.rename(filename, new_path)
                return new_path
            return filename
        else:
            # Use the original template
            if isinstance(data, dict):
                name = data.get('name', 'Candidate')
            else:
                name = 'Candidate'
            return generate_cover_letter_pdf(cover_letter_text, name)
    except Exception as e:
        print(f"Error generating cover letter with template {template_type}: {str(e)}")
        raise

class PDF(FPDF):
    def header(self):
        """Adds a logo if available."""
        try:
            self.image(config.LOGO_PATH, 160, 8, 35)
        except:
            pass  # Skip if logo is not found
        self.set_font("Arial", "B", 12)
        self.ln(10)
        
    def chapter_title(self, title):
        self.set_text_color(0, 0, 180)
        self.set_font("Arial", "B", 11)
        self.cell(0, 8, self.clean_text(title), ln=True, align="L")
        self.ln(4)
        self.set_text_color(0, 0, 0)
            
    def add_project_table(self, project):
        """Creates a vertical-style project details table."""
        col_widths = [60, 120]  # Adjusted column width for better text fitting
        row_height = 8

        self.set_font("Arial", "B", 10)
        # Use either name or project_name field
        project_name = project.get('name', project.get('project_name', 'N/A'))
        self.cell(0, 6, f"{self.clean_text(project_name)}", ln=True)
        self.ln(3)
        self.set_font("Arial", "", 9)

        def add_row(label, text):
            if text:
                text = self.clean_text(text)
                text_height = (self.get_string_width(text) // col_widths[1] + 1) * row_height
                self.cell(col_widths[0], row_height, label, border=1, align="C")
                self.multi_cell(col_widths[1], row_height, text, border=1)
                self.ln(0)  # Ensure proper spacing

        # Create fields mapping that can handle both naming conventions
        fields = [
            ("Project Name", project.get("name", project.get("project_name", "N/A"))),
            ("Description", project.get("description", "N/A")),
            ("Role", project.get("role", "N/A")),
            ("Technology", project.get("technology", "N/A")),
            ("Role Played", project.get("role_played", "N/A")),
        ]

        for label, text in fields:
            add_row(label, text)

        self.ln(5)  # Extra space after each project table

    def cell(self, w, h=0, txt='', border=0, ln=0, align='', fill=False, link=''):
        txt = self.clean_text(txt)
        super().cell(w, h, txt, border, ln, align, fill, link)

    def multi_cell(self, w, h, txt, border=0, align='J', fill=False):
        txt = self.clean_text(txt)
        super().multi_cell(w, h, txt, border, align, fill)

    def clean_text(self, text):
        if not isinstance(text, str):
            text = str(text)
        text = re.sub(r"[""]", '"', text)
        text = re.sub(r"['']", "'", text)
        return text.encode("latin-1", "replace").decode("latin-1")


def generate_resume_1(data_json: str) -> str:
    """Generates the resume PDF with precise formatting."""
    try:
        # Handle both string and dictionary input types
        if isinstance(data_json, str):
            try:
                data = json.loads(data_json)
            except json.JSONDecodeError:
                # If JSON parsing fails, create minimal data
                data = {
                    "name": "Candidate",
                    "designation": "Professional",
                    "summarized_objective": "Resume data could not be parsed correctly."
                }
        else:
            data = data_json

        # Ensure data has all required keys
        required_keys = ["name", "designation", "education", "skills", "project_details"]
        for key in required_keys:
            if key not in data:
                data[key] = [] if key in ["education", "skills", "project_details"] else {}
                if key in ["name", "designation"]:
                    data[key] = "Not Provided"
        
        pdf = PDF()
        pdf.set_margins(15, 15, 15)
        pdf.add_page()
        pdf.logo_path = config.LOGO_PATH  # Always use the config logo path

        if "name" in data and data["name"]:
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 8, pdf.clean_text(data["name"]), ln=True, align="L")
        
        if "designation" in data and data["designation"]:
            pdf.set_font("Arial", "I", 12)
            pdf.cell(0, 8, pdf.clean_text(data["designation"]), ln=True, align="L")
        
        pdf.set_line_width(0.5)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(8)
        
        if "summarized_objective" in data and data["summarized_objective"]:
            pdf.chapter_title("PROFESSIONAL SUMMARY")
            pdf.set_font("Arial", "", 9)
            pdf.multi_cell(0, 7, pdf.clean_text(data["summarized_objective"]))
            pdf.ln(5)
        
        if "education" in data and data["education"]:
            pdf.chapter_title("EDUCATION")
            pdf.set_font("Arial", "", 9)
            pdf.multi_cell(0, 6, pdf.clean_text("".join(data["education"])))
            pdf.ln(5)
        
        if "skills" in data and data["skills"]:
            pdf.chapter_title("SKILLS")
            pdf.set_font("Arial", "", 9)
            pdf.multi_cell(0, 6, pdf.clean_text(", ".join(data["skills"])))
            pdf.ln(8)
        
        # Modified project_details handling to work with both list and dict formats
        if "project_details" in data:
            pdf.chapter_title("PROJECT DETAILS")
            
            # Handle projects whether they're in a list or dictionary
            projects = []
            if isinstance(data["project_details"], dict):
                projects = data["project_details"].values()
            elif isinstance(data["project_details"], list):
                projects = data["project_details"]
                
            for project in projects:
                if isinstance(project, dict) and project:
                    # Map field names if needed (project_name → name)
                    project_data = {}
                    if "project_name" in project and "name" not in project:
                        project_data["name"] = project["project_name"]
                    else:
                        project_data["name"] = project.get("name", "N/A")
                        
                    # Copy other fields directly
                    project_data["description"] = project.get("description", "N/A")
                    project_data["role"] = project.get("role", "N/A") 
                    project_data["technology"] = project.get("technology", "N/A")
                    project_data["role_played"] = project.get("role_played", "N/A")
                    
                    pdf.add_project_table(project_data)
        
        # Use a sanitized name for the output filename
        safe_name = pdf.clean_text(data.get('name', 'Resume')).replace(' ', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '._- ')
        filename = os.path.join(config.OUTPUT_DIR, f"{safe_name}_Resume.pdf")
        
        pdf.output(filename)
        return filename
    
    except Exception as e:
        print(f"Error in generate_resume_1: {str(e)}")
        
        # Create a fallback PDF with error information
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Resume Generation Error", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 7, f"An error occurred while generating the resume: {str(e)}")
            pdf.ln(5)
            pdf.multi_cell(0, 7, "Please try again or contact support.")
            
            error_filename = os.path.join(config.OUTPUT_DIR, "Resume_Generation_Error.pdf")
            pdf.output(error_filename)
            return error_filename
        except:
            # If even the error PDF fails, return a path that doesn't exist (will be caught in calling code)
            return os.path.join(config.OUTPUT_DIR, "resume_generation_failed.pdf")

def generate_cover_letter_pdf(cover_letter_text: str, candidate_name: str) -> str:
    """Generates a PDF file from the cover letter text."""
    try:
        # Safety check for candidate name
        if not candidate_name or not isinstance(candidate_name, str):
            candidate_name = "Candidate"
        
        # Sanitize candidate name for the filename
        safe_name = ''.join(c for c in candidate_name if c.isalnum() or c in '._- ')
        safe_name = safe_name.replace(' ', '_')
        
        pdf = PDF()
        pdf.set_margins(15, 15, 15)
        pdf.add_page()
        
        # Header with candidate name
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 8, f"{pdf.clean_text(candidate_name)} - Cover Letter", ln=True, align="L")
        
        # Horizontal Line
        pdf.set_line_width(0.5)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(8)
        
        # Cover letter content
        pdf.set_font("Arial", "", 11)
        
        # Split text into paragraphs and add to PDF
        paragraphs = cover_letter_text.split("\n\n")
        for paragraph in paragraphs:
            if paragraph.strip():
                pdf.multi_cell(0, 7, pdf.clean_text(paragraph.strip()))
                pdf.ln(4)
        
        # Save the cover letter
        filename = os.path.join(config.OUTPUT_DIR, f"{safe_name}_Cover_Letter.pdf")
        pdf.output(filename)
        return filename
    
    except Exception as e:
        print(f"Error in generate_cover_letter_pdf: {str(e)}")
        
        # Create a fallback PDF with error information
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Cover Letter Generation Error", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 7, f"An error occurred while generating the cover letter: {str(e)}")
            pdf.ln(5)
            pdf.multi_cell(0, 7, "Please try again or contact support.")
            
            error_filename = os.path.join(config.OUTPUT_DIR, "Cover_Letter_Generation_Error.pdf")
            pdf.output(error_filename)
            return error_filename
        except:
            # If even the error PDF fails, return a path that doesn't exist (will be caught in calling code)
            return os.path.join(config.OUTPUT_DIR, "cover_letter_generation_failed.pdf")