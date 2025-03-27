import datetime
from fpdf import FPDF
import json
import unicodedata
import re
import os
import config


class ResumePDF(FPDF):

    def header(self):
        """Creates the gradient header background."""
        self.set_fill_color(255, 255, 255)
        self.rect(0, 0, 210, 20, 'F')

        # Gradient Effect
        colors = [(153, 119, 230), (127, 85, 217), (102, 51, 204)]
        x_positions = [16, 8, 0]

        for i in range(3):
            self.set_fill_color(*colors[i])
            self.rect(x_positions[i], 0, 40, 8, 'F')

    def add_name(self, name):
        
        """Adds the name, title to the resume header."""
        
        self.set_xy(10, 10)
        self.set_font("Arial", style="B", size=18)
        self.cell(0, 10, name, ln=True)
        self.ln(4)

       

    def add_designation(self, title):
        # """Adds the designation below the name."""
        self.set_xy(10, 22)  # Move it below the name
        self.set_font("Arial", style="B", size=14)
        self.set_text_color(102, 0, 204)
        self.cell(0, 8, title, ln=True,align='L')
        self.set_text_color(0, 0, 0)
    
    def add_email(self,email):
         # Contact details (Top Right)
        self.set_xy(120, 10)
        self.set_font("Arial", style="B", size=12)
        self.cell(0, 7, "Email Id: ", ln=False)
        self.set_font("Arial", size=12)
        self.cell(0, 7, email, ln=True, align='R')


    def add_contact(self,phone):
        self.set_xy(130, 18)
        self.set_font("Arial", style="B", size=12)
        self.cell(0, 7, "Phone Number: ", ln=False)
        self.set_font("Arial", size=12)
        self.cell(0, 7, phone, ln=True, align='R')

    def add_section_title(self, title, color=(102, 51, 204)):
        """Adds a section title with a colored text effect."""
        self.set_font("Arial", style="B", size=16)
        self.set_text_color(*color)
        self.cell(0, 5, title, ln=True)
        

    def add_summary(self, text):
        """Adds the summary section."""
         # Ensure spacing before summary
        self.set_font("Arial", size=11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6,text)
        self.ln(1)

    def add_work_experience(self):
        self.add_section_title("Work Experience")

    def add_experience(self, title, company, date, details):
        """Adds a work experience section with bullet points."""
        self.set_font("Arial", style="B", size=12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, title, ln=True)

        self.set_font("Arial", style="I", size=11)
        self.set_text_color(85, 85, 85)
        self.cell(0, 8, f"{company}  _  {date}", ln=True)

        self.set_font("Arial", size=11)
        self.set_text_color(0, 0, 0)
        for detail in details:
            self.cell(5)
            self.cell(0, 6, f"- {detail}", ln=True)
        self.ln(2)

    def add_skills(self, skills_list):
        """Adds the skills section."""
        self.add_section_title("Skills")
        self.set_font("Arial", size=11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, ", ".join(skills_list))
        self.ln(5)
    

    

    def add_project_title(self):
            self.set_fill_color(230, 230, 250)
            self.set_font("Arial", style="B", size=16)
            self.set_text_color(102, 51, 204)
            self.cell(0, 10, "Project Experience", ln=True)
            self.ln(3)

    def extract_contact_info(self,json_data):
        # Check if contact_information is present or if fields exist at root level
        contact_info = json_data.get("contact_information", json_data)

        email = contact_info.get("email", "")
        phone_number = contact_info.get("phone_number", "")

        self.add_email(email)
        self.add_contact(phone_number)
        return email, phone_number

        
    def add_project_experience(self, company, description, technologies, details):
        # """Adds a project experience section with formatted text."""
        # Add title with a gradient background
        

        self.set_x(self.l_margin)
        # Project Name
         # Project Title (Bold, Black)
        self.set_font("Arial", style="B", size=12)
        self.set_text_color(102, 51, 204)
        self.cell(0, 8, company, ln=True, align="L")
        self.ln(1)
        
        self.set_text_color(0, 0, 0)
        # Project Description
        self.set_font("Arial", size=11)
        self.multi_cell(0, 6, description)
        self.ln(2)

        # Bullet Points for details
        for detail in details:
            self.cell(5)
            self.cell(0, 6, f"- {detail}", ln=True)
        self.ln(2)

        
       # Technologies Section (Ensuring Proper Formatting)
        self.set_font("Arial", style="B", size=11)
        self.cell(self.get_string_width("Technologies: "), 6, "Technologies:", ln=False)  # Keep label inline

        self.set_font("Arial", size=11)
        self.multi_cell(0, 6, technologies)  # Ensures it wraps properly
    
    # def add_education(self, title,text):
    #         self.set_x(self.l_margin)
    #         self.add_section_title(title)
    #         self.set_font("Arial", size=11)
    #         self.set_text_color(0, 0, 0)
    #         self.multi_cell(0, 6," ".join(text))
    #         self.ln(5)

    def add_education(self, education):
        self.add_section_title("EDUCATION")

        # If education is a string, print it directly
        if isinstance(education, str):
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 7, education)
            self.ln(5)
            return

        # Ensure education is always a list
        if isinstance(education, dict):
            education = [education]  # Convert single dict to list
        
        if not isinstance(education, list):  # If not a list after conversion, skip processing
            print("Error: 'education' should be a string, dictionary, or list.")
            return

        for edu in education:
            if not isinstance(edu, dict):  # Ensure each entry is a dictionary
                print("Skipping invalid education entry:", edu)
                continue

            self.set_font("Arial", "B", 10)
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            duration = edu.get('duration', '')
            
            
            self.cell(0, 7, f"Graduate in {degree} from {institution}", ln=True)
            self.set_font("Arial", "", 10)
            self.cell(0, 7, f"- {duration}", ln=True, align="R")

        self.ln(2)
   



    def footer(self):
        """Adds a stylish footer with a thin underline."""
        self.set_y(-15)
        self.set_text_color(100, 100, 100)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"Page {self.page_no()} | Resume", align='C')
    
     




def generate_resume_4(data):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ""  # Initialize name attribute
    # Check if 'data' is a string, then convert it to a dictionary
    if isinstance(data, str):
        try:
            data_json = json.loads(data)
        except json.JSONDecodeError as e:
            print("Invalid JSON format:", e)
            return None
    elif isinstance(data, dict):
        data_json = data
    else:
        raise ValueError("Data must be either a JSON string or a dictionary")
    
    name = data_json.get('name', '')

    def remove_unicode(text):

        """Normalize Unicode to ASCII and remove non-ASCII characters."""
        if isinstance(text, str):
            return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        elif isinstance(text, list):
            return [remove_unicode(item) for item in text]
        elif isinstance(text, dict):
            return {k: remove_unicode(v) for k, v in text.items()}
        return text

    # Ensure `data_json` is a dictionary
    if isinstance(data_json, str):
        try:
            data_json = json.loads(data_json)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None  # Exit if JSON parsing fails

    if not isinstance(data_json, dict):
        print("Invalid input format. Expected a dictionary.")
        return None

    clean_json_data = {key: remove_unicode(value) for key, value in data_json.items()}

    pdf = ResumePDF()
    # pdf.set_margins(15, 15, 15)
    pdf.add_page()

    if 'name' in clean_json_data:
        pdf.add_name(name=clean_json_data['name'])
    
    
    if 'contact_information' in clean_json_data:
        contact_info = clean_json_data['contact_information']
    
    else:

        if 'email' in clean_json_data and clean_json_data.get('email', '')!="":
            pdf.add_email(clean_json_data['email'])    
            

        if 'phone_number' in clean_json_data and clean_json_data.get('phone_number', '')!="":
            pdf.add_contact(clean_json_data['phone_number'])    


        
    if 'designation' in clean_json_data:
        pdf.add_designation(title=clean_json_data['designation'])
        
    if 'summarized_objective' in clean_json_data:
        pdf.add_summary(clean_json_data['summarized_objective'])
    
    if clean_json_data['work_experience']:
        pdf.add_work_experience()
        for exp in clean_json_data['work_experience']:
            responsibilities = exp.get('responsibilities', [])[:6]  # Limit to 6 responsibilities
            pdf.add_experience(exp.get('position',''), exp.get('company', 'Unknown Company'), exp.get('duration', 'Unknown Duration'), responsibilities)
    
    if 'skills' in clean_json_data:
        pdf.add_skills(clean_json_data['skills'])
    
    education_courses = clean_json_data.get('education', [])
        
    if education_courses:
        pdf.add_education(education_courses)
        
    if 'project_experience' in clean_json_data and clean_json_data['project_experience']:

        pdf.add_project_title()
        for project in clean_json_data.get('project_experience', []):
            project_name = project.get('project_name') or project.get('name') or project.get('title') or 'Unknown Project'
            
            pdf.add_project_experience(
                company=project_name,
                description=project.get('description', ''),
                technologies=", ".join(project.get('technologies', ['N/A'])) if isinstance(project.get('technologies'), list) else project.get('technologies', 'N/A'),
                details=project.get('responsibilities', [])  # Extracting responsibilities
            )


    # Save the file to the output directory
    safe_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    if not safe_name:
        safe_name = 'Resume'
        
    filename = f"{safe_name}_Resume.pdf"
    output_path = os.path.join(config.OUTPUT_DIR, filename)
    pdf.output(output_path)
    return output_path


def generate_cover_letter_4(data, cover_letter_text):
    """
    Creative Cover Letter template matching Resume Template 4
    
    Features:
    - Colorful header with accent colors
    - Modern typography
    - Coordinated formatting with Resume Template 4
    """
    # Convert data to dict if it's a JSON string
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            data = {"name": "Candidate", "designation": "Professional"}
    
    class CreativeCoverLetterPDF(FPDF):
        def __init__(self):
            super().__init__()
            self.accent_color = (142, 68, 173)  # Purple
            self.accent_color_light = (187, 143, 206)  # Light purple
        
        def header(self):
            # Add colorful header
            self.set_fill_color(*self.accent_color)
            self.rect(0, 0, 210, 20, 'F')
            
            # Add name and designation in white
            self.set_font('Arial', 'B', 16)
            self.set_text_color(255, 255, 255)
            self.cell(0, 12, data.get('name', 'Candidate'), 0, 1, 'C')
            
            if data.get('designation'):
                self.set_font('Arial', 'I', 12)
                self.cell(0, 8, data.get('designation', ''), 0, 1, 'C')
            
            self.ln(5)
        
        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-15)
            self.set_fill_color(*self.accent_color_light)
            self.rect(0, self.get_y(), 210, 15, 'F')
            
            # Page number
            self.set_text_color(0, 0, 0)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    # Create a new PDF instance
    pdf = CreativeCoverLetterPDF()
    pdf.add_page()
    
    # Add date
    today = datetime.datetime.now().strftime("%B %d, %Y")
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, today, 0, 1, 'R')
    pdf.ln(5)
    
    # Add greeting
    recipient = data.get('recipient', 'Hiring Manager')
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(*pdf.accent_color)
    pdf.cell(0, 6, f"Dear {recipient},", 0, 1)
    pdf.ln(5)
    
    # Add cover letter content
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(50, 50, 50)  # Dark gray for readability
    
    # Split into paragraphs and add each one
    paragraphs = cover_letter_text.split('\n\n')
    for paragraph in paragraphs:
        if paragraph.strip():
            pdf.multi_cell(0, 6, paragraph.strip())
            pdf.ln(5)
    
    # Add closing
    pdf.ln(5)
    pdf.cell(0, 6, "Sincerely,", 0, 1)
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(*pdf.accent_color)
    pdf.cell(0, 6, data.get('name', 'Candidate'), 0, 1)
    
    # Save to file
    output_filename = f"{data.get('name', 'Candidate').replace(' ', '_')}_Creative_Cover_Letter.pdf"
    output_path = os.path.join(config.OUTPUT_DIR, output_filename)
    pdf.output(output_path)
    return output_path

