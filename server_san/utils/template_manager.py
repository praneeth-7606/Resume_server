


"""
Template manager module to handle different PDF resume and cover letter templates.
"""

import os
import json
from typing import Dict, Any, Callable, Optional, List
import config

# Import all template functions
from .templete_1 import generate_resume_1, generate_cover_letter_pdf
from .template_2 import generate_resume_2
from .templete_3 import generate_resume_3, generate_cover_letter_3


# Define the new template function for template 4
def generate_resume_4(data):
    """
    Creative Portfolio template with colorful layout and visual emphasis
    
    This template features:
    - Colorful header with accent colors
    - Modern typography
    - Emphasized skills and portfolio sections
    """
    # Convert data to dict if it's a JSON string
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            data = {"name": "Candidate", "designation": "Professional"}
    
    # Use the FPDF library to create a new PDF
    from fpdf import FPDF
    
    class CreativePortfolioPDF(FPDF):
        def __init__(self):
            super().__init__()
            self.accent_color = (142, 68, 173)  # Purple accent color
            self.accent_color_light = (187, 143, 206)  # Light purple for backgrounds
        
        def header(self):
            # Add colorful header
            self.set_fill_color(*self.accent_color)
            self.rect(0, 0, 210, 30, 'F')
            
            # Add name in white
            self.set_font('Helvetica', 'B', 20)
            self.set_text_color(255, 255, 255)
            self.cell(0, 20, data.get('name', 'Candidate'), 0, 1, 'C')
            
            # Add designation below name
            if data.get('designation'):
                self.set_font('Helvetica', 'I', 12)
                self.cell(0, 10, data.get('designation', ''), 0, 1, 'C')
            
            # Reset text color
            self.set_text_color(0, 0, 0)
            
        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-15)
            # Add colored footer
            self.set_fill_color(*self.accent_color_light)
            self.rect(0, self.get_y(), 210, 15, 'F')
            # Add page number in white
            self.set_text_color(0, 0, 0)
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
        def section_title(self, title):
            # Add colored section title
            self.set_font('Helvetica', 'B', 14)
            self.set_fill_color(*self.accent_color)
            self.set_text_color(255, 255, 255)
            self.cell(0, 8, title.upper(), 0, 1, 'L', fill=True)
            self.set_text_color(0, 0, 0)
            self.ln(2)
        
        def add_skill_section(self, skills):
            if not skills:
                return
                
            self.section_title("SKILLS")
            
            if isinstance(skills, list):
                # Create a nice visual grid of skills
                skill_width = 60
                skill_height = 10
                col = 0
                
                for skill in skills:
                    if col >= 3:  # 3 skills per row
                        col = 0
                        self.ln(skill_height)
                    
                    # Add a nice skill box with light background
                    self.set_fill_color(*self.accent_color_light)
                    self.set_font('Helvetica', 'B', 9)
                    self.cell(skill_width, skill_height, skill, 1, 0, 'C', fill=True)
                    col += 1
                
                self.ln(skill_height + 5)
            
            elif isinstance(skills, dict):
                # Handle categorized skills
                for category, skill_list in skills.items():
                    if skill_list:
                        self.set_font('Helvetica', 'B', 11)
                        self.cell(0, 6, category.replace("_", " ").title(), 0, 1)
                        
                        # Create a grid of skills for each category
                        skill_width = 60
                        skill_height = 10
                        col = 0
                        
                        for skill in skill_list:
                            if col >= 3:  # 3 skills per row
                                col = 0
                                self.ln(skill_height)
                            
                            # Add a nice skill box with light background
                            self.set_fill_color(*self.accent_color_light)
                            self.set_font('Helvetica', '', 9)
                            self.cell(skill_width, skill_height, skill, 1, 0, 'C', fill=True)
                            col += 1
                        
                        self.ln(skill_height + 5)
    
    # Create PDF instance
    pdf = CreativePortfolioPDF()
    pdf.add_page()
    
    # Add sections
    
    # Summary
    if data.get('summarized_objective') or data.get('objective'):
        pdf.section_title("PROFESSIONAL SUMMARY")
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 5, data.get('summarized_objective', data.get('objective', '')))
        pdf.ln(5)
    
    # Education
    if data.get('education'):
        pdf.section_title("EDUCATION")
        pdf.set_font('Helvetica', '', 10)
        
        education = data.get('education')
        if isinstance(education, list):
            for edu in education:
                pdf.multi_cell(0, 5, edu)
                pdf.ln(2)
        else:
            pdf.multi_cell(0, 5, education)
        
        pdf.ln(5)
    
    # Skills with custom formatting
    if data.get('skills'):
        pdf.add_skill_section(data.get('skills'))
    elif data.get('technical_skills'):
        pdf.add_skill_section(data.get('technical_skills'))
    
    # Projects or Experience
    if data.get('project_details') or data.get('projects'):
        pdf.section_title("PORTFOLIO")
        
        projects = data.get('projects', [])
        if not projects and data.get('project_details'):
            project_details = data.get('project_details')
            if isinstance(project_details, dict):
                projects = [{"title": p.get("name", ""), "description": p.get("description", "")} 
                           for p in project_details.values()]
            elif isinstance(project_details, list):
                projects = [{"title": p.get("name", ""), "description": p.get("description", "")} 
                           for p in project_details]
        
        for project in projects:
            # Add a project box with light background
            pdf.set_fill_color(*pdf.accent_color_light)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 8, project.get('title', project.get('name', '')), 0, 1, 'L', fill=True)
            
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(0, 5, project.get('description', ''))
            pdf.ln(5)
    
    # Save the file
    output_filename = f"{data.get('name', 'Candidate').replace(' ', '_')}_Creative_Resume.pdf"
    output_path = os.path.join(config.OUTPUT_DIR, output_filename)
    pdf.output(output_path)
    return output_path

# Function to generate a matching cover letter with template 4
def generate_cover_letter_4(data, cover_letter_text):
    """
    Creative Portfolio cover letter template with matching style to resume template 4
    """
    # Convert data to dict if it's a JSON string
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            data = {"name": "Candidate", "designation": "Professional"}
    
    # Use the FPDF library to create a new PDF
    from fpdf import FPDF
    
    class CreativePortfolioPDF(FPDF):
        def __init__(self):
            super().__init__()
            self.accent_color = (142, 68, 173)  # Purple accent color
            self.accent_color_light = (187, 143, 206)  # Light purple for backgrounds
        
        def header(self):
            # Add colorful header
            self.set_fill_color(*self.accent_color)
            self.rect(0, 0, 210, 30, 'F')
            
            # Add name in white
            self.set_font('Helvetica', 'B', 20)
            self.set_text_color(255, 255, 255)
            self.cell(0, 20, data.get('name', 'Candidate'), 0, 1, 'C')
            
            # Add designation below name
            if data.get('designation'):
                self.set_font('Helvetica', 'I', 12)
                self.cell(0, 10, data.get('designation', ''), 0, 1, 'C')
            
            # Reset text color
            self.set_text_color(0, 0, 0)
            
        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-15)
            # Add colored footer
            self.set_fill_color(*self.accent_color_light)
            self.rect(0, self.get_y(), 210, 15, 'F')
            # Add page number in white
            self.set_text_color(0, 0, 0)
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
        def section_title(self, title):
            # Add colored section title
            self.set_font('Helvetica', 'B', 14)
            self.set_fill_color(*self.accent_color)
            self.set_text_color(255, 255, 255)
            self.cell(0, 8, title.upper(), 0, 1, 'L', fill=True)
            self.set_text_color(0, 0, 0)
            self.ln(2)
    
    # Create PDF instance
    pdf = CreativePortfolioPDF()
    pdf.add_page()
    
    # Add cover letter title
    pdf.section_title("COVER LETTER")
    
    # Date
    import datetime
    today = datetime.datetime.now().strftime("%B %d, %Y")
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, today, 0, 1, 'R')
    pdf.ln(5)
    
    # Recipient
    recipient = data.get('recipient', 'Hiring Manager')
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 6, f"Dear {recipient},", 0, 1)
    pdf.ln(5)
    
    # Cover letter content with nice formatting
    pdf.set_font('Helvetica', '', 10)
    paragraphs = cover_letter_text.split('\n\n')
    
    for paragraph in paragraphs:
        if paragraph.strip():
            pdf.multi_cell(0, 5, paragraph.strip())
            pdf.ln(5)
    
    # Closing
    pdf.ln(5)
    pdf.cell(0, 6, "Sincerely,", 0, 1)
    pdf.ln(10)
    
    # Signature with stylish accent
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(*pdf.accent_color)
    pdf.cell(0, 6, data.get('name', 'Candidate'), 0, 1)
    pdf.set_text_color(0, 0, 0)
    
    # Save the file
    output_filename = f"{data.get('name', 'Candidate').replace(' ', '_')}_Creative_Cover_Letter.pdf"
    output_path = os.path.join(config.OUTPUT_DIR, output_filename)
    pdf.output(output_path)
    return output_path

# Dictionary to store available resume templates
RESUME_TEMPLATES = {
    1: generate_resume_1,  # Default/Original template
    2: generate_resume_2,  # Professional template
    3: generate_resume_3,  # Creative Resume template (your provided code)
    4: generate_resume_4,  # Creative Portfolio template
    # Add more templates here when available
}

# Define a function to generate cover letter using template 2
def generate_cover_letter_2(data, cover_letter_text):
    """Generate cover letter using the professional template (template 2)."""
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            data = {"name": "Candidate", "designation": "Professional"}
    
    # Create PDF using similar approach to resume but with cover letter content
    # This is a simplified version - implement according to your needs
    from .template_2 import ResumePDF
    
    pdf = ResumePDF()
    pdf.name = data.get('name', 'Candidate')
    pdf.designation = data.get('designation', '')
    pdf.contact = " | ".join(filter(None, [
        data.get('phone', ''), 
        data.get('email', ''), 
        data.get('linkedin', '')
    ]))
    pdf.add_page()
    
    # Add cover letter title
    pdf.section_title('Cover Letter')
    
    # Process the cover letter text into paragraphs
    paragraphs = cover_letter_text.split('\n\n')
    for paragraph in paragraphs:
        if paragraph.strip():
            pdf.section_body(paragraph.strip())
    
    # Save the file
    filename = f"{pdf.name.replace(' ', '_')}_Cover_Letter.pdf"
    output_path = os.path.join(config.OUTPUT_DIR, filename)
    pdf.output(output_path)
    return output_path

# Dictionary to store available cover letter templates
COVER_LETTER_TEMPLATES = {
    1: generate_cover_letter_pdf,  # Default/Original template
    2: generate_cover_letter_2,    # Professional template
    3: generate_cover_letter_3,    # Creative Resume template
    4: generate_cover_letter_4,    # Creative Portfolio template
    # Add more templates here when available
}

def get_available_templates() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get a list of all available templates with their details.
    Useful for providing template options to the frontend.
    
    Returns:
        Dictionary with resume and cover letter template information
    """
    resume_templates = [
        {"id": 1, "name": "Standard Template", "description": "Basic clean resume layout"},
        {"id": 2, "name": "Professional Template", "description": "Modern professional resume with improved formatting"},
        {"id": 3, "name": "Creative Resume", "description": "Blue header with gold accents and elegant section styling"},
        {"id": 4, "name": "Creative Portfolio", "description": "Colorful template with visual emphasis for creative professionals"}
    ]
    
    cover_letter_templates = [
        {"id": 1, "name": "Standard Cover Letter", "description": "Basic clean cover letter layout"},
        {"id": 2, "name": "Professional Cover Letter", "description": "Matching cover letter for professional resume template"},
        {"id": 3, "name": "Creative Cover Letter", "description": "Blue header with gold accents for a stylish look"},
        {"id": 4, "name": "Creative Portfolio Cover Letter", "description": "Matching cover letter for the Creative Portfolio template"}
    ]
    
    return {
        "resume_templates": resume_templates,
        "cover_letter_templates": cover_letter_templates
    }

def generate_resume(data: Any, template_id: int = 1) -> str:
    """
    Generate a resume with the specified template.
    
    Args:
        data: Resume data (dictionary or JSON string)
        template_id: ID of the template to use
        
    Returns:
        Path to the generated PDF file
    """
    # Log the template_id for debugging
    print(f"Generating resume with template_id: {template_id}")
    
    # Get the generator function for the specified template
    if template_id in RESUME_TEMPLATES:
        template_func = RESUME_TEMPLATES[template_id]
    else:
        print(f"Warning: Template ID {template_id} not found, using default template")
        template_func = RESUME_TEMPLATES[1]  # Default to template 1
    
    # Pass data to the template function
    try:
        output_path = template_func(data)
        print(f"Generated resume PDF: {output_path}")
        
        # Ensure the file is in the output directory
        if not output_path.startswith(config.OUTPUT_DIR):
            filename = os.path.basename(output_path)
            new_path = os.path.join(config.OUTPUT_DIR, filename)
            
            # If the file exists but is not in output dir, copy it
            if os.path.exists(output_path):
                import shutil
                shutil.copy2(output_path, new_path)
                return new_path
        
        return output_path
    except Exception as e:
        print(f"Error generating resume with template {template_id}: {str(e)}")
        raise

def generate_cover_letter(data: Any, cover_letter_text: str, template_id: int = 1) -> str:
    """
    Generate a cover letter with the specified template.
    
    Args:
        data: Resume/candidate data (dictionary or JSON string)
        cover_letter_text: Text content for the cover letter
        template_id: ID of the template to use
        
    Returns:
        Path to the generated PDF file
    """
    # Log the template_id for debugging
    print(f"Generating cover letter with template_id: {template_id}")
    
    # Get the generator function for the specified template
    if template_id in COVER_LETTER_TEMPLATES:
        template_func = COVER_LETTER_TEMPLATES[template_id]
    else:
        print(f"Warning: Cover letter template ID {template_id} not found, using default template")
        template_func = COVER_LETTER_TEMPLATES[1]  # Default to template 1
    
    # Handle the different parameter requirements between templates
    try:
        if template_id == 1:
            # Original template only needs name and text
            if isinstance(data, dict):
                name = data.get('name', 'Candidate')
            elif isinstance(data, str):
                try:
                    data_dict = json.loads(data)
                    name = data_dict.get('name', 'Candidate')
                except:
                    name = 'Candidate'
            else:
                name = 'Candidate'
                
            output_path = template_func(cover_letter_text, name)
        else:
            # Other templates need full data and text
            output_path = template_func(data, cover_letter_text)
        
        # Ensure the file is in the output directory
        if not output_path.startswith(config.OUTPUT_DIR):
            filename = os.path.basename(output_path)
            new_path = os.path.join(config.OUTPUT_DIR, filename)
            
            # If the file exists but is not in output dir, copy it
            if os.path.exists(output_path):
                import shutil
                shutil.copy2(output_path, new_path)
                return new_path
        
        return output_path
    except Exception as e:
        print(f"Error generating cover letter with template {template_id}: {str(e)}")
        raise