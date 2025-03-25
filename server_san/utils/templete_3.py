import config
import json
import os


# Import CreativeResumePDF from the code provided
from fpdf import FPDF
import re

class CreativeResumePDF(FPDF):
    bullet_image_path = "BP.jpeg"  # Ensure this exists in the directory
    
    def __init__(self):
        super().__init__()
        self.set_margins(10, 10, 10)  # Set left, top, and right margins
        self.set_auto_page_break(auto=True, margin=20)  # Ensure bottom margin


    def clean_text(self, text):
        """Cleans text by replacing special characters and encoding it properly."""
        if not isinstance(text, str):
            text = str(text)

        text = re.sub(r'["“”]', '"', text)  # Match regular and fancy double quotes
        text = re.sub(r"[‘’']", "'", text)  # Match single quotes and apostrophes
        text = re.sub(r"[–—]", "-", text)   # Replace en-dash and em-dash with hyphen

        # Encode to Latin-1 safely (ignore unsupported characters)
        text = text.encode("latin-1", "ignore").decode("latin-1")
        
        return text.strip()


    def header(self):
        """Creates an eye-catching header with a stylish background."""
        if self.page_no() == 1:
            # Add header background
            self.set_fill_color(30, 45, 80)  # Darker blue for top bar
            self.rect(0, 0, self.w, 50, 'F')

            # Add white space
            self.ln(18)

            # Centered Name
            self.set_text_color(255, 255, 255)  # White
            self.set_font('Arial', 'B', 26)
            self.cell(0, 12, self.clean_text(self.name), align='C', ln=True)

            # Centered Designation in Gold
            self.set_text_color(255, 215, 0)  # Gold
            self.set_font('Arial', 'B', 18)
            self.cell(0, 10, self.clean_text(self.designation), align='C', ln=True)

            # Centered Contact Details in Dark Blue
            self.set_font('Arial', 'B', 10)
            self.set_text_color(0, 51, 102)
            self.cell(0, 6, self.clean_text(self.contact), align='C', ln=True)
            
            self.ln(10)

    def add_bullet_point(self, text):
        """Adds a bullet point with an image or fallback symbol."""
        text = self.clean_text(text)
        if not text:  # Skip empty entries
            return  

        if os.path.exists(self.bullet_image_path):
            self.image(self.bullet_image_path, x=self.get_x(), y=self.get_y(), w=5, h=5)
            self.cell(6)  # Space between bullet and text
        else:
            self.cell(5, 6, "•", ln=False)  # Unicode bullet fallback

        self.multi_cell(0, 7, text)
        self.ln(1)
            
    def add_profile_section(self, profile_text):
        """Adds a centered profile section with a full-width colored bar for the title."""
        if not profile_text.strip():
            return  # Skip if empty

        self.set_font('Arial', 'B', 12)
        self.set_text_color(255, 255, 255)  # White text for contrast

        # Set the background color for the bar (Deep Blue)
        bar_height = 10
        self.set_fill_color(30, 45, 80)  # Dark Blue

        # Draw the colored bar (full-width)
        self.rect(0, self.get_y(), self.w, bar_height, 'F')

        # Place the title in the center of the bar
        self.cell(0, bar_height, "PROFILE", align='C', ln=True)

        # Move cursor below the bar
        self.ln(5)

        # Profile Text (Centered)
        self.set_font('Arial', '', 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 7, self.clean_text(profile_text), align='C')
        
        self.ln(5)  # Extra space after the section
    
    def add_section(self, title, content):
        print(f"Adding section: {title}, Content: {content}")  # Debugging line

        if not content or (isinstance(content, list) and not any(isinstance(item, (str, dict)) and item for item in content)):
            return  # Skip empty sections

        self.set_font('Arial', 'B', 11)
        self.set_text_color(30, 45, 80)  # Deep Blue Title
        self.cell(0, 8, self.clean_text(title.upper()), ln=True)
        self.cell(0, 0, '', 'T', ln=True)  # Underline
        self.ln(5)

        self.set_font('Arial', '', 10)
        self.set_text_color(50, 50, 50)

        for item in content:
            if isinstance(item, dict) and 'title' in item:  # Handling cases like 'Courses'
                self.add_bullet_point(item['title'])
            elif isinstance(item, str) and item.strip():  # Ignore empty strings
                self.add_bullet_point(item)

        self.ln(3)

    def add_courses_section(self, courses):
        """Formats the Courses section separately with title and institution."""
        if not courses:
            return  # Skip if empty

        self.set_font('Arial', 'B', 11)
        self.set_text_color(30, 45, 80)  # Deep Blue Title
        self.cell(0, 8, "COURSES", ln=True)
        self.cell(0, 0, '', 'T', ln=True)  # Underline
        self.ln(5)

        self.set_font('Arial', '', 10)
        self.set_text_color(50, 50, 50)

        for course in courses:
            if 'title' in course and 'institution' in course:
                self.set_font('Arial', 'B', 10)
                self.cell(0, 6, f"{self.clean_text(course['title'])} - {self.clean_text(course['institution'])}", ln=True)
            self.ln(2)  # Add spacing

    def add_project_section(self, projects):
        """Formats the projects section, ensuring empty projects are skipped."""
        if not projects or not any(p.get('title', '').strip() for p in projects):
            return  # Skip if no valid projects

        self.set_font('Arial', 'B', 12)
        self.set_text_color(30, 45, 80)
        self.cell(0, 8, self.clean_text("PROJECTS"), ln=True)
        self.cell(0, 0, '', 'T', ln=True)
        self.ln(5)

        for project in projects:
            title = self.clean_text(project.get('title', ''))
            description = self.clean_text(project.get('description', ''))

            if not title:
                continue  # Skip projects without a title

            self.set_font('Arial', 'B', 11)
            self.add_bullet_point(title)

            if description:
                self.set_font('Arial', '', 10)
                self.multi_cell(0, 6, description)

            self.ln(5)

    def footer(self):
        """Adds a stylish footer with a thin underline."""
        self.set_y(-15)
        self.set_text_color(100, 100, 100)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"Page {self.page_no()} | Resume", align='C')

# Define the function to generate a resume using the CreativeResumePDF template
def generate_resume_3(data, template_id=3):
    """
    Generate a resume PDF using the CreativeResumePDF template with robust handling of missing or mismatched data.
    
    Template features:
    - Blue header with gold accents
    - Modern typography and elegant styling
    
    This function handles:
    - Objective/Profile section (checks both 'objective' and 'summarized_objective')
    - Education section (accepts either a list or a string)
    - Skills section: segregates skills based on categories if available in a dictionary; otherwise, checks for keys in the main data.
    - Courses section (if available)
    - Projects section (supports both dict and list formats)
    - Declaration section (if available)
    """
    
    # Convert to dict if needed
    if not isinstance(data, dict):
        try:
            data = json.loads(data)
        except Exception as e:
            raise ValueError("Invalid data format. Ensure input is a dictionary or valid JSON string.") from e

    print("Data of template 3", data)
    
    pdf = CreativeResumePDF()
    pdf.name = data.get('name', '')
    pdf.designation = data.get('designation', '')
    
    # Extract contact information from possible keys
    contact_info = {}
    for key in ['contact', 'contact_information']:
        if key in data and isinstance(data[key], dict):
            contact_info = data[key]
            break
    pdf.contact = " | ".join(filter(None, [
        contact_info.get('phone', ''),
        contact_info.get('email', ''),
        contact_info.get('location', '')
    ]))
    
    pdf.add_page()
    
    # Objective / Profile Summary Section: check for 'objective' or 'summarized_objective'
    profile_text = data.get('objective') or data.get('summarized_objective')
    if profile_text:
        pdf.add_profile_section(profile_text)
    
    # Education Section: if education exists, check if it is a list or string
    education_data = data.get('education')
    if education_data:
        if isinstance(education_data, list) and education_data:
            pdf.add_section('Education', education_data)
        elif isinstance(education_data, str) and education_data.strip():
            pdf.add_section('Education', [education_data.strip()])
    
    # Skills Section: segregate based on categories if available.
    segregated = False
    
    # Option 1: Check if 'skills' is provided as a dictionary with categorized data.
    if 'skills' in data and isinstance(data['skills'], dict):
        skills_section = data['skills']
        skill_keys = {
            "Technical Skills": ["technical", "technical_skills"],
            "Soft Skills": ["soft", "soft_skills"],
            "Languages": ["languages", "language_skills"]
        }
        for section_name, possible_keys in skill_keys.items():
            for key in possible_keys:
                if key in skills_section and skills_section[key]:
                    content = skills_section[key]
                    if isinstance(content, list):
                        pdf.add_section(section_name, content)
                    elif isinstance(content, str) and content.strip():
                        pdf.add_section(section_name, [content.strip()])
                    segregated = True
                    break
    
    # Option 2: If not segregated within 'skills', check main data for these keys.
    if not segregated:
        for section, key in [('Technical Skills', 'technical_skills'),
                             ('Soft Skills', 'soft_skills'),
                             ('Languages', 'languages')]:
            if key in data and data[key]:
                content = data[key]
                if isinstance(content, list):
                    pdf.add_section(section, content)
                elif isinstance(content, str) and content.strip():
                    pdf.add_section(section, [content.strip()])
                segregated = True

    # Option 3: Fallback - if segregated data not found, use a generic 'skills' list if provided.
    if not segregated and 'skills' in data and data['skills']:
        generic_skills = data['skills']
        if isinstance(generic_skills, list):
            pdf.add_section('Skills', generic_skills)
        elif isinstance(generic_skills, str) and generic_skills.strip():
            pdf.add_section('Skills', [generic_skills.strip()])
    
    # Courses Section: add if non-empty list is provided
    courses = data.get('courses')
    if courses and isinstance(courses, list) and courses:
        pdf.add_courses_section(courses)
    
    # Projects Section: support both 'project_details' (as dict) and 'projects' (as list)
    projects_list = []
    if 'project_details' in data and isinstance(data['project_details'], dict):
        for project in data['project_details'].values():
            title = project.get("name", "").strip()
            description = project.get("description", "").strip()
            if title:
                projects_list.append({
                    "title": title,
                    "description": description
                })
    elif 'projects' in data and isinstance(data['projects'], list):
        for project in data['projects']:
            title = project.get("title", "").strip()
            description = project.get("description", "").strip()
            if title:
                projects_list.append({
                    "title": title,
                    "description": description
                })
    if projects_list:
        pdf.add_project_section(projects_list)
    
    # Declaration Section
    declaration = data.get('declaration')
    if declaration and isinstance(declaration, str) and declaration.strip():
        pdf.add_section('Declaration', [declaration.strip()])
    else:
        pdf.add_section('Declaration', ["I hereby declare that the above information is true to the best of my knowledge."])
    
    # Generate filename and output PDF
    output_filename = f"{data.get('name', 'Candidate').replace(' ', '_')}_Creative_Resume.pdf"
    output_path = os.path.join(config.OUTPUT_DIR, output_filename)
    pdf.output(output_path)
    return output_path
# Function to generate a matching cover letter for template 3
def generate_cover_letter_3(data, cover_letter_text):
    """
    Creative cover letter template with matching style to resume template 3
    
    Features:
    - Coordinated styling with the Creative Resume
    - Blue header with gold accents
    - Professional formatting
    """
    # Convert data to dict if it's a JSON string
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            data = {"name": "Candidate", "designation": "Professional"}
    
    # Create a new PDF using the CreativeResumePDF class
    pdf = CreativeResumePDF()
    pdf.name = data.get('name', '')
    pdf.designation = data.get('designation', '')
    
    # Handle contact information in different formats
    if isinstance(data.get('contact'), dict):
        pdf.contact = f"{data['contact'].get('phone', '')} | {data['contact'].get('email', '')} | {data['contact'].get('location', '')}"
    else:
        # Combine any available contact info
        contact_parts = []
        for field in ['phone', 'email', 'linkedin']:
            if data.get(field):
                contact_parts.append(data.get(field))
        pdf.contact = " | ".join(contact_parts) if contact_parts else ""
    
    pdf.add_page()
    
    # Add "COVER LETTER" header with blue background
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(255, 255, 255)  # White text for contrast
    bar_height = 10
    pdf.set_fill_color(30, 45, 80)  # Dark Blue
    pdf.rect(0, pdf.get_y(), pdf.w, bar_height, 'F')
    pdf.cell(0, bar_height, "COVER LETTER", align='C', ln=True)
    pdf.ln(5)
    
    # Add date
    import datetime
    today = datetime.datetime.now().strftime("%B %d, %Y")
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, today, 0, 1, 'R')
    pdf.ln(5)
    
    # Add greeting
    recipient = data.get('recipient', 'Hiring Manager')
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(30, 45, 80)  # Deep Blue
    pdf.cell(0, 6, f"Dear {recipient},", 0, 1)
    pdf.ln(5)
    
    # Add cover letter content
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(50, 50, 50)  # Dark gray for body text
    
    # Split into paragraphs and add each one
    paragraphs = cover_letter_text.split('\n\n')
    for paragraph in paragraphs:
        if paragraph.strip():
            pdf.multi_cell(0, 6, pdf.clean_text(paragraph.strip()))
            pdf.ln(5)
    
    # Add closing
    pdf.ln(5)
    pdf.cell(0, 6, "Sincerely,", 0, 1)
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(30, 45, 80)  # Deep Blue
    pdf.cell(0, 6, pdf.clean_text(data.get('name', 'Candidate')), 0, 1)
    
    # Save to file
    output_filename = f"{data.get('name', 'Candidate').replace(' ', '_')}_Creative_Cover_Letter.pdf"
    output_path = os.path.join(config.OUTPUT_DIR, output_filename)
    pdf.output(output_path)
    return output_path