"""
Professional template module for resume and cover letter generation.
This module provides the ResumePDF class and resume generation function
for template option 2.
"""

from fpdf import FPDF
import re
import json
import os
import config


class ResumePDF(FPDF):
    
    def __init__(self):
        super().__init__()
        self.first_page = True  # Track if it's the first page

        self.bullet_image_path = config.BP

    def clean_text(self, text):
        if not isinstance(text, str):
            text = str(text)
        text = re.sub(r'[""]', '"', text)
        text = re.sub(r"['']", "'", text)
        text = re.sub(r"[–—]", "-", text)
        text = text.encode("latin-1", "ignore").decode("latin-1")
        return text
    

    def header(self):
        if self.first_page:
            self.set_font('Courier', 'B', 25)
            self.cell(0, 10, self.clean_text(self.name), align='C', ln=True)
            if hasattr(self, 'designation') and self.designation:
                self.set_font('Courier', 'I', 12)
                self.cell(0, 10, self.clean_text(self.designation), align='C', ln=True)
            if hasattr(self, 'contact') and self.contact:
                self.set_font('Courier', '', 11)
                self.cell(0, 8, self.clean_text(self.contact), align='C', ln=True)
            self.ln(5)
            self.first_page = False  

    def section_title(self, title):
        """Adds a section title with an underline for better readability."""
        self.set_font('Courier', 'B', 18)
        title = self.clean_text(title.upper())  # Ensure text is cleaned
        self.cell(0, 8, title, ln=True)
        
        # Draw a line below the title
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)  # Add spacing after the line

    def section_body(self, body):
        if body:
            self.set_font('Arial', '', 10)
            self.multi_cell(0, 6, self.clean_text(body))
            self.ln(5)
    
    def add_bullet_point(self, text):
        """Adds a bullet point with an image or fallback symbol."""
        text = self.clean_text(text)
        if not text:  # Skip empty entries
            return  

        try:
            if os.path.exists(self.bullet_image_path):
                # Print debug info when successfully finding the image
                print(f"Found bullet image at: {self.bullet_image_path}")
                self.image(self.bullet_image_path, x=self.get_x(), y=self.get_y(), w=5, h=5)
                self.cell(6)  # Space between bullet and text
            else:
                # Print debug info when image not found
                print(f"Bullet image not found at: {self.bullet_image_path}")
                self.cell(5, 6, "•", ln=False)  # Unicode bullet fallback
        except Exception as e:
            # Print any exceptions that occur
            print(f"Error adding bullet image: {str(e)}")
            self.cell(5, 6, "•", ln=False)  # Unicode bullet fallback

        self.multi_cell(0, 7, text)
        self.ln(1)

    def list_section(self, title, content):
        if content:
            self.section_title(title)
            self.set_font('Arial', '', 11)
            for item in content:
                self.multi_cell(0, 6, self.clean_text(f"• {item}"))
                self.ln(1)
            self.ln(1)

    def experience_section(self, experiences):
        if experiences:
            self.section_title('Experience')
            for exp in experiences:
                self.set_font('Courier', 'B', 15)
                self.multi_cell(0, 6, self.clean_text(f"{exp['title']} - {exp['company']}"))
                self.set_font('Arial', 'I', 10)
                self.multi_cell(0, 6, self.clean_text(exp['duration']))
                self.set_font('Arial', '', 10)
                if exp.get('responsibilities'):
                    for res in exp['responsibilities']:
                        self.add_bullet_point(res)  # Using defined bullet point method
                self.ln(1)

    def skills_section(self, skills):
        if skills and any(skill_list for skill_list in skills.values()):
            self.section_title('Technical Skills')
            for category, skill_list in skills.items():
                if skill_list:  # Ensures only non-empty categories are printed
                    self.set_font('Arial', 'B', 10)
                    self.multi_cell(0, 6, self.clean_text(category.replace('_', ' ').title()))
                    self.set_font('Arial', '', 10)
                    self.multi_cell(0, 6, self.clean_text(", ".join(skill_list)))
                    self.ln(1)

    def projects_section(self, projects):
        if projects:
            self.section_title('Projects')
            for project in projects:
                self.set_font('Arial', 'B', 10)
                self.multi_cell(0, 6, self.clean_text(project.get('title', project.get('name', ''))))
                self.set_font('Arial', '', 10)
                self.multi_cell(0, 6, self.clean_text(project.get('description', '')))
                self.ln(1)

    def certifications_section(self, certifications):
        if certifications:
            self.section_title('Certifications')
            self.set_font('Arial', '', 10)
            for cert in certifications:
                self.multi_cell(0, 6, self.clean_text(cert))
                self.ln(1)


def generate_resume_2(data):
    """Generate a resume using template 2 (Professional template)"""
    # Handle different input types
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            # If JSON parsing fails, create minimal data
            data = {
                "name": "Candidate",
                "designation": "Professional",
                "summarized_objective": "Resume data could not be parsed correctly."
            }
            
    pdf = ResumePDF()
    pdf.name = data.get('name', '')

    # Set properties
    pdf.designation = data.get('designation', '')
    
    # Extract contact information from possible keys
    contact_info = {}
    for key in ['contact', 'contact_information', 'personal_details']:
        if key in data and isinstance(data[key], dict):
            contact_info = data[key]
            break

    pdf.contact = " | ".join(filter(None, [
        contact_info.get('phone', ''),
        contact_info.get('email', ''),
        contact_info.get('linkedin', ''),
        contact_info.get('location', '')
    ]))

    pdf.add_page()

    # Add sections if data exists
    if data.get('summarized_objective') or data.get('objective'):
        pdf.section_title('Summary')
        pdf.section_body(data.get('summarized_objective', data.get('objective', '')))
    
    if data.get('education'):
        education = data['education']

    # Ensure education is a list or a string before processing
    if isinstance(education, list):
        if all(isinstance(edu, dict) for edu in education):  # List of dictionaries
            valid_entries = [
                edu for edu in education
                if 'institution' in edu and 'degree' in edu and 'duration' in edu
            ]
            if valid_entries:
                pdf.section_title('Education')
                edu_text = "\n".join(
                    f"{edu['institution']} - {edu['degree']} ({edu['duration']})"
                    for edu in valid_entries
                )
                pdf.section_body(edu_text)

        elif all(isinstance(edu, str) for edu in education):  # List of strings (institution names)
            if education:  # Ensure it's not an empty list
                pdf.section_title('Education')
                edu_text = ", ".join(education)
                pdf.section_body(edu_text)

    elif isinstance(education, str) and education.strip():  # Single string case
        pdf.section_title('Education')
        pdf.section_body(education)


    
    # Handle skills in different possible formats
    if data.get('technical_skills'):
        pdf.skills_section(data['technical_skills'])
    elif data.get('skills'):
        # Convert flat skills list to dictionary format if needed
        if isinstance(data['skills'], list):
            pdf.section_title('Skills')
            skills_text = ", ".join(data['skills'])
            pdf.section_body(skills_text)
        elif isinstance(data['skills'], dict):
            pdf.skills_section(data['skills'])
    
    # Add experience if available
    if data.get('experience'):
        pdf.experience_section(data['experience'])
            
    # Handle project details in different possible formats
    if data.get('projects'):
        pdf.projects_section(data['projects'])
    elif data.get('project_details'):
        # Convert project_details to projects format
        projects = []
        if isinstance(data['project_details'], dict):
            for key, project in data['project_details'].items():
                if isinstance(project, dict):
                    project_entry = {
                        'title': project.get('name', ''),
                        'description': f"{project.get('description', '')}\n"
                                      f"Role: {project.get('role', '')}\n"
                                      f"Technologies: {project.get('technology', '')}\n"
                                      f"{project.get('role_played', '')}"
                    }
                    projects.append(project_entry)
        elif isinstance(data['project_details'], list):
            for project in data['project_details']:
                if isinstance(project, dict):
                    project_entry = {
                        'title': project.get('name', ''),
                        'description': f"{project.get('description', '')}\n"
                                      f"Role: {project.get('role', '')}\n"
                                      f"Technologies: {project.get('technology', '')}\n"
                                      f"{project.get('role_played', '')}"
                    }
                    projects.append(project_entry)
        
        if projects:
            pdf.projects_section(projects)

    # Add certifications if available
    if data.get('certifications'):
        pdf.certifications_section(data['certifications'])

    # Save the file to the output directory
    safe_name = pdf.name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    if not safe_name:
        safe_name = 'Resume'
        
    filename = f"{safe_name}_Resume.pdf"
    output_path = os.path.join(config.OUTPUT_DIR, filename)
    pdf.output(output_path)
    return output_path