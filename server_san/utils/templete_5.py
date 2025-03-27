from fpdf import FPDF
import json
import unicodedata
import re
import os
import config



def remove_unicode(text):
    if isinstance(text, str):
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    elif isinstance(text, list):
        return [remove_unicode(item) for item in text]
    elif isinstance(text, dict):
        return {k: remove_unicode(v) for k, v in text.items()}
    return text
from fpdf import FPDF

class PDF(FPDF):

    def header(self):
        if self.page_no() == 1:
            self.set_font("Arial", "B", 20)
            self.cell(0, 10, self.name, ln=True, align="C")
            self.set_font("Arial", "", 12)
            self.cell(0, 10, self.designation, ln=True, align="C")
            self.set_font("Arial", "", 10)
            self.cell(0, 10, self.contact, ln=True, align="C")
            self.ln(5)
            self.line(10, 40, 200, 40)
            self.ln(5)
    
    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        #self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
    
    def section_body(self, text):
        self.set_font("Times", "I", 10)
        self.multi_cell(0, 7, text)
        
    def education_section(self, education):
        self.section_title("EDUCATION")

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
            degree = edu.get('degree', 'Unknown Degree')
            institution = edu.get('institution', 'Unknown Institution')
            location = edu.get('location', '')
            year = edu.get('year', 'N/A')

            self.cell(0, 7, f"Graduate in {degree} from {institution}, {location}", ln=True)
            self.set_font("Arial", "", 10)
            self.cell(0, 7, f"- {year}", ln=True, align="R")

        self.ln(5)



    def skills_section(self, skills):
        self.set_x(self.l_margin)  # Reset X position to the left margin
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "TECHNICAL SKILLS", ln=True, align="L")
        self.ln(5)

        for key, value in skills.items():
            self.set_x(self.l_margin)  # Reset X position to the left margin

            if len(value) != 0:
                self.set_font("Arial", "B", 10)
                self.cell(60, 7, key, align="L")
                self.set_font("Arial", "", 10)
                
                # Convert list to string if value is a list
                if isinstance(value, list):
                    value = ", ".join(value)
                
                self.multi_cell(100, 7, ": " + value, border=0, align="L")




    
    def experience_section(self, experience):
        self.section_title("EXPERIENCE")
        for exp in experience:
            self.set_font("Arial", "B", 10)
            self.cell(0, 7, exp['title'] + " - " + exp['company'], ln=False)
            self.cell(-50)  # Move back for right alignment
            self.cell(50, 7, f"{exp['duration']}", align="R", ln=True)  # Align right
            self.set_font("Arial", "", 10)
            
            for i in exp['responsibilities']:
                self.cell(0, 6, f"- {i}", ln=True)
                self.cell(3)
            # self.multi_cell(0, 7, f"- {exp['responsibilities']}")
            self.ln(2)


def generate_resume_5(data):
    
    data = remove_unicode(data)
    pdf = PDF()
    pdf.set_font("Arial", "", 12)
    pdf.name = data.get('name', '')

    pdf.designation = data.get('designation', '')
    contact_info = data.get('contact_info', {})
    pdf.contact = " | ".join(filter(None, [
        contact_info.get('phone', ''), 
        contact_info.get('email', ''), 
        contact_info.get('linkedin', '')
    ]))
    pdf.add_page()
    
    if data.get('summarized_objective'):
        pdf.section_title('Summary')
        pdf.section_body(data['summarized_objective'])
    
    
    
    if data.get('technical_skills'):
        pdf.skills_section(data['technical_skills'])
    
    if data.get('experience'):
        pdf.experience_section(data['experience'])
    
    # if data.get('education'):
    #     pdf.education_section(data['education'])

    # if "education" in data and data["education"]:
    #     pdf.section_title("EDUCATION")
    #     pdf.set_font("Arial", "", 9)
    #     pdf.multi_cell(0, 6, data["education"])
    #     pdf.ln(5)

    # Save the file to the output directory
    safe_name = pdf.name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    if not safe_name:
        safe_name = 'Resume'
        
    filename = f"{safe_name}_Resume.pdf"
    output_path = os.path.join(config.OUTPUT_DIR, filename)
    pdf.output(output_path)
    return output_path

# Function to generate a matching cover letter with template 4
def generate_cover_letter_5(data, cover_letter_text):
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