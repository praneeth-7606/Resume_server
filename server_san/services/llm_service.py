from mistralai import Mistral
import json
import os
from typing import Dict, Any
import config

def LLM_CALL_1(resume_text: str) -> str:
    """Extract structured JSON from resume text"""
    try:
        model = "mistral-large-latest"
        client = Mistral(api_key=config.API_KEY)
        parsed_text = resume_text # Limit text length to avoid token limits
        
        # Read system prompt from file
        system_prompt_path = os.path.join(config.PROMPTS_DIR, "LLM1.txt")
        if os.path.exists(system_prompt_path):
            with open(system_prompt_path, 'r') as file:
                system_prompt = file.read()
        else:
            # Fallback if file doesn't exist
            system_prompt = """
           You are an advanced AI specializing in extracting structured information from unstructured text. Your task is to format resume data into a structured JSON schema. Donot give the response other than JSON format . Donot have any description at stop start with json format. Donot have the json word in the start.

 

            name and designation mandatory key value pairs and create a proper summarized_objective a key  in for any kind of templete.
            Ensure valid JSON formatting.The output should start ``` { ``` and end with ``` } ```. No other additional words should be there.

            feel free to re arrange the order of the keys in the JSON schema as long as the data is correct but make sure to adhere to the new_resume_format below.
            """
        
        try:
            print("This is LLM_1: System prompt:",system_prompt)
            chat_response = client.chat.complete(
                model=model,
                temperature=0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is an extracted resume text:\n\n{parsed_text}\n\nFormat it into JSON."}
                ],
                response_format = {
                    "type": "json_object",
                }
            )
            
            json_schema = chat_response.choices[0].message.content
            
            # Clean the JSON output by removing triple backticks if present
            cleaned_json = json_schema.strip()
            if cleaned_json.startswith("```json") and cleaned_json.endswith("```"):
                cleaned_json = cleaned_json[7:-3].strip()
            elif cleaned_json.startswith("```") and cleaned_json.endswith("```"):
                cleaned_json = cleaned_json[3:-3].strip()
            
            # Validate the JSON
            try:
                json.loads(cleaned_json)
                return cleaned_json
            except json.JSONDecodeError:
                # If invalid JSON, try to fix common issues
                import re
                cleaned_json = cleaned_json.replace('\n', ' ').replace('\r', '')
                cleaned_json = re.sub(r'(?<!")(\w+)(?=":)', r'"\1"', cleaned_json)
                return cleaned_json
                
        except Exception as e:
            print(f"Error in Mistral API call: {str(e)}")
            # Return a default JSON structure
            default_json = {
                "name": "",
                "designation": "",
                "objective": "",
                "education": [],
                "skills": [],
                "project_details": {}
            }
            return json.dumps(default_json)
    
    except Exception as e:
        print(f"Unexpected error in LLM_CALL_1: {str(e)}")
        default_json = {
            "name": "",
            "designation": "",
            "objective": "",
            "education": [],
            "skills": [],
            "project_details": {}
        }
        return json.dumps(default_json)

def LLM_CALL_2(formatted_json_schema: Dict, old_resume_text: str, skill_matrix_json: str) -> str:
    """Reformat old resume with skill matrix data into new structured JSON"""
    try:
        model = "mistral-large-latest"
        client = Mistral(api_key=config.API_KEY)
        
        new_resume_text = formatted_json_schema
        # Limit text lengths to avoid token limits
        old_resume_text = old_resume_text
        if len(skill_matrix_json) > 2000:
            skill_matrix_json = skill_matrix_json[:2000] + "... [truncated]"
        
        system_prompt = f"""
        You are an AI assistant that reformats resumes into a structured JSON format.
        Take the competency matrix and old resume as input, extract relevant details, and map them to the new resume format.
        Only respond with the new resume format as a JSON object that adheres strictly to the provided JSON Schema. Do not include any extra messages.
        **Instructions:**
                - Only use the given details; do not generate fictional information.
                - Follow the JSON structure exactly as provided.
                - Ensure the output starts directly with a valid JSON object (no extra text or explanations).
                - Try to keep the project description within 40-50 words.
                - If there are any keys having empoty values pl skip the resoective keys in output.
                Generate the updated resume in JSON format:
                name and designation mandatory key value pairs and create a proper summarized objective a key  in for any kind of templete.
                make sure it follows the given format of formatted_json_schema wiht same json format with key value pairs. 
                Points to note : In the key "Education" form a sentance and give in points make a list and use that. Do not make up values , if you have no access to a value, don't make it up.
                Keep the names of the keyvalues in the json schema same. Skills also give as per the json schema.
                

                Make sure to keep the same key names as in the json schema for rest attributes.

                You are given the following details: You are given the following details:

                Your task is to extract relevant details and format them into the following structured JSON format:
                {new_resume_text}
        """
        
        try:
            chat_response = client.chat.complete(
                model=model,
                temperature=0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""
                    You are given the following details:
                    
                    **Skill Matrix (Extracted from External Data Sources):**
                    {skill_matrix_json}
                    
                    **Old Resume (Extracted Text):**
                    {old_resume_text}
                    
                    Your task is to extract relevant details and format them into the following structured JSON format:
                    
                    {json.dumps(formatted_json_schema, indent=2)}
                    
                    **Instructions:**
                    - Only use the given details; do not generate fictional information.
                    - Follow the JSON structure exactly as provided.
                    - Ensure the output is a valid JSON object (no extra text or explanations).
                    - "name" and "designation" are mandatory fields.
                    - Create a proper summarized objective.
                    
                    Generate the updated resume in JSON format:
                    """}
                ],
                response_format = {
                    "type": "json_object",
                }
            )
            
            resume_content = chat_response.choices[0].message.content
            
            # Attempt to validate and clean JSON if needed
            try:
                json.loads(resume_content)
                return resume_content
            except json.JSONDecodeError:
                # Clean up if it's not valid JSON
                cleaned_content = resume_content.replace('```json', '').replace('```', '').strip()
                return cleaned_content
                
        except Exception as e:
            print(f"Error in Mistral API call: {str(e)}")
            # Extract name from resume text as fallback
            name = "Candidate"
            for line in old_resume_text.split('\n'):
                if line.strip() and len(line.strip()) < 50:
                    name = line.strip()
                    break
                    
            # Return a basic JSON with resume text information
            default_json = {
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
            return json.dumps(default_json)
    
    except Exception as e:
        print(f"Unexpected error in LLM_CALL_2: {str(e)}")
        # Return a basic JSON structure
        default_json = {
            "name": "Candidate",
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
        return json.dumps(default_json)

def LLM_CALL_3(formatted_json_schema, old_cover_text, json_output):
    """Reformat old cover letter with skill matrix into structured JSON"""
    model = "mistral-large-latest"
    client = Mistral(api_key=config.API_KEY)

    new_resume_text = formatted_json_schema
    Content2 = old_cover_text
    Skill_Matrix = json_output
    
    system_prompt = f"""
    You are an AI assistant that reformats resumes into a structured JSON format.
    Take the competency matrix and old resume as input, extract relevant details, and map them to the new resume format.
    Only respond with the new resume format as a JSON object that adheres strictly to the provided JSON Schema. Do not include any extra messages.
    **Instructions:**
            - Only use the given details; do not generate fictional information.
            - Follow the JSON structure exactly as provided.
            - Ensure the output starts directly with a valid JSON object (no extra text or explanations).
            - Try to keep the project description within 40-50 words.

            Generate the updated resume in JSON format:
            name and designation mandatory key value pairs and create a proper summarized objective a key  in for any kind of templete.
            make sure it follows the given format of formatted_json_schema wiht same json format with key value pairs. 
            Points to note : In the key "Education" form a sentance and give in points make a list and use that. Do not make up values , if you have no access to a value, don't make it up.
            Keep the names of the keyvalues in the json schema same. Skills also give as per the json schema.

            Make sure to keep the same key names as in the json schema for rest attributes.

            You are given the following details: You are given the following details:

            Your task is to extract relevant details and format them into the following structured JSON format:
            {new_resume_text}
    """
    
    chat_response = client.chat.complete(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
            
            **Skill Matrix (Extracted from External Data Sources):**
            {Skill_Matrix}

            **Old Coverletter (Extracted Text):**
            {Content2}

            """}
        ],
        response_format = {
          "type": "json_object",
      }
    )

    resume_content = chat_response.choices[0].message.content
    return resume_content
def LLM_CALL_4(formatted_json_schema, old_resume_text, old_cover_text):
    """Reformat old resume and cover letter into structured JSON"""
    model = "mistral-large-latest"
    client = Mistral(api_key=config.API_KEY)

    new_resume_text = formatted_json_schema
    Content = old_resume_text
    Content2 = old_cover_text

    system_prompt = f"""
    You are an AI assistant that reformats resumes into a structured JSON format.
    Take the competency matrix and old resume as input, extract relevant details, and map them to the new resume format.
    Only respond with the new resume format as a JSON object that adheres strictly to the provided JSON Schema. Do not include any extra messages.
    **Instructions:**
            - Only use the given details; do not generate fictional information.
            - Follow the JSON structure exactly as provided.
            - Ensure the output starts directly with a valid JSON object (no extra text or explanations).
            - Try to keep the project description within 40-50 words.

            Generate the updated resume in JSON format:
            name and designation mandatory key value pairs and create a proper summarized objective a key  in for any kind of templete.
            make sure it follows the given format of formatted_json_schema wiht same json format with key value pairs. 
            Points to note : In the key "Education" form a sentance and give in points make a list and use that. Do not make up values , if you have no access to a value, don't make it up.
            Keep the names of the keyvalues in the json schema same. Skills also give as per the json schema.

            Make sure to keep the same key names as in the json schema for rest attributes.

            You are given the following details: You are given the following details:

            Your task is to extract relevant details and format them into the following structured JSON format:
            {new_resume_text}
    """
    
    try:
        chat_response = client.chat.complete(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""
                
                **Old Resume (Extracted Text):**
                {Content}
                
                **Old Cover Letter (Extracted Text):**
                {Content2}
                
                """}
            ],
            response_format = {
              "type": "json_object",
            }
        )

        resume_content = chat_response.choices[0].message.content
        
        # Attempt to validate and clean JSON if needed
        try:
            json.loads(resume_content)
            return resume_content
        except json.JSONDecodeError:
            # Clean up if it's not valid JSON
            cleaned_content = resume_content.replace('```json', '').replace('```', '').strip()
            return cleaned_content
            
    except Exception as e:
        print(f"Error in Mistral API call: {str(e)}")
        # Extract name from resume text as fallback
        name = "Candidate"
        for line in Content.split('\n'):
            if line.strip() and len(line.strip()) < 50:
                name = line.strip()
                break
                
        # Return a basic JSON with resume text information
        default_json = {
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
        return json.dumps(default_json)

def generate_resume_structure() -> Dict[str, Any]:
    """Generate a default resume structure schema"""
    schema = {
        "name": "",
        "designation": "",
        "objective": "",
        "education": [],
        "skills": [],
        "project_details": {
            "project1": {
                "name": "",
                "role": "",
                "description": "",
                "technology": "",
                "role_played": ""
            }
        }
    }
    return schema

def process_resume(resume_text: str, cover_letter_text: str = "", skill_matrix: str = ""):
    """Process resume text and generate structured JSON output"""
    try:
        # Step 1: Extract initial JSON structure from resume
        initial_json = LLM_CALL_1(resume_text)
        parsed_json = json.loads(initial_json)
        
        # Step 2: Create a standard schema
        resume_schema = generate_resume_structure()
        
        # Step 3: Process with skill matrix if available
        if skill_matrix:
            final_json = LLM_CALL_2(resume_schema, resume_text, skill_matrix)
        # Step 4: Process with cover letter if available
        elif cover_letter_text:
            if skill_matrix:
                # If both skill matrix and cover letter are available
                final_json = LLM_CALL_3(resume_schema, cover_letter_text, skill_matrix)
            else:
                # If only cover letter is available
                final_json = LLM_CALL_4(resume_schema, resume_text, cover_letter_text)
        else:
            # If only resume is available
            final_json = initial_json
            
        # Return the final structured JSON
        return final_json
        
    except Exception as e:
        print(f"Error in process_resume: {str(e)}")
        # Return a default structure in case of errors
        default_json = generate_resume_structure()
        default_json["name"] = "Candidate"
        default_json["designation"] = "Professional"
        default_json["objective"] = "Experienced professional seeking new opportunities."
        return json.dumps(default_json)

# Example usage
if __name__ == "__main__":
    # Sample usage
    sample_resume = """
    John Doe
    Senior Software Engineer
    
    SUMMARY
    Experienced software engineer with 8+ years of experience in full-stack development,
    specializing in Python, JavaScript, and cloud technologies.
    
    EDUCATION
    Master of Science in Computer Science, Stanford University, 2015
    Bachelor of Engineering in Information Technology, MIT, 2013
    
    SKILLS
    Programming: Python, JavaScript, Java, C++
    Web: React, Angular, Node.js, Django, Flask
    Database: PostgreSQL, MongoDB, MySQL
    Cloud: AWS, Azure, Docker, Kubernetes
    
    PROJECTS
    Project Alpha - Lead Developer (2020-Present)
    Developed a scalable microservices architecture for fintech applications
    Technologies: Python, Docker, Kubernetes, AWS
    
    Project Beta - Senior Engineer (2018-2020)
    Built real-time data processing pipeline for analytics
    Technologies: Python, Kafka, Spark, MongoDB
    """
    
    sample_cover_letter = """
    Dear Hiring Manager,
    
    I am writing to express my interest in the Senior Software Engineer position at XYZ Corp.
    With my background in full-stack development and cloud technologies, I believe I am well-suited for this role.
    
    Throughout my career, I have focused on building scalable and efficient systems using modern technologies.
    My experience with Python, JavaScript, and cloud platforms aligns perfectly with your requirements.
    
    I look forward to the opportunity to discuss how my skills can contribute to your team's success.
    
    Sincerely,
    John Doe
    """
    
    sample_skill_matrix = """
    {
      "technical_skills": {
        "programming_languages": ["Python (Expert)", "JavaScript (Advanced)", "Java (Intermediate)", "C++ (Basic)"],
        "frameworks": ["React", "Angular", "Node.js", "Django", "Flask"],
        "databases": ["PostgreSQL", "MongoDB", "MySQL"],
        "cloud_technologies": ["AWS", "Azure", "Docker", "Kubernetes"]
      },
      "soft_skills": ["Leadership", "Communication", "Problem-solving", "Team Collaboration"],
      "certifications": ["AWS Certified Solutions Architect", "Certified Scrum Master"],
      "achievements": ["Reduced system latency by 40%", "Led team of 5 engineers", "Implemented CI/CD pipeline"]
    }
    """
    
    # Process the resume with additional information
    result = process_resume(sample_resume, sample_cover_letter, sample_skill_matrix)
    print(result)
def LLM_CALL_5(formatted_json_schema, old_resume_text):
    """Reformat only old resume into structured JSON"""
    model = "mistral-large-latest"
    client = Mistral(api_key=config.API_KEY)

    new_resume_text = formatted_json_schema
    Content = old_resume_text
  
    system_prompt = f"""
    You are an AI assistant that reformats resumes into a structured JSON format.
    Take the competency matrix and old resume as input, extract relevant details, and map them to the new resume format.
    Only respond with the new resume format as a JSON object that adheres strictly to the provided JSON Schema. Do not include any extra messages.
    **Instructions:**
            - Only use the given details; do not generate fictional information.
            - Follow the JSON structure exactly as provided.
            - Ensure the output starts directly with a valid JSON object (no extra text or explanations).
            - Try to keep the project description within 40-50 words.

            Generate the updated resume in JSON format:
            name and designation mandatory key value pairs and create a proper summarized objective a key  in for any kind of templete.
            make sure it follows the given format of formatted_json_schema wiht same json format with key value pairs. 
            Points to note : In the key "Education" form a sentance and give in points make a list and use that. Do not make up values , if you have no access to a value, don't make it up.
            Keep the names of the keyvalues in the json schema same. Skills also give as per the json schema.
            

            Make sure to keep the same key names as in the json schema for rest attributes.

            You are given the following details: You are given the following details:

            Your task is to extract relevant details and format them into the following structured JSON format:
            {new_resume_text}
    """
    
    chat_response = client.chat.complete(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
             
            **Old Resume (Extracted Text):**
            {Content}
           
            """}
        ],
        response_format = {
          "type": "json_object",
      }
    )

    resume_content = chat_response.choices[0].message.content
    return resume_content

def LLM_CALL_6(formatted_json_schema, old_cover_text):
    """Reformat only old cover letter into structured JSON"""
    model = "mistral-large-latest"
    client = Mistral(api_key=config.API_KEY)

    new_resume_text = formatted_json_schema
    Content2 = old_cover_text
  
    system_prompt = f"""
    You are an AI assistant that reformats resumes into a structured JSON format.
    Take the competency matrix and old resume as input, extract relevant details, and map them to the new resume format.
    Only respond with the new resume format as a JSON object that adheres strictly to the provided JSON Schema. Do not include any extra messages.
    **Instructions:**
            - Only use the given details; do not generate fictional information.
            - Follow the JSON structure exactly as provided.
            - Ensure the output starts directly with a valid JSON object (no extra text or explanations).
            - Try to keep the project description within 40-50 words.

            Generate the updated resume in JSON format:
            name and designation mandatory key value pairs and create a proper summarized objective a key  in for any kind of templete.
            make sure it follows the given format of formatted_json_schema wiht same json format with key value pairs. 
            Points to note : In the key "Education" form a sentance and give in points make a list and use that. Do not make up values , if you have no access to a value, don't make it up.
            Keep the names of the keyvalues in the json schema same. Skills also give as per the json schema.

            Make sure to keep the same key names as in the json schema for rest attributes.

            You are given the following details: You are given the following details:

            Your task is to extract relevant details and format them into the following structured JSON format:
            {new_resume_text}
    """
    
    
    chat_response = client.chat.complete(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
             
            **Old CoverLetter (Extracted Text):**
            {Content2}
           
            """}
        ],
        response_format = {
          "type": "json_object",
      }
    )

    resume_content = chat_response.choices[0].message.content
    return resume_content

def LLM_CALL_7(formatted_json_schema, json_output):
    """Reformat only skill matrix into structured JSON"""
    model = "mistral-large-latest"
    client = Mistral(api_key=config.API_KEY)

    new_resume_text = formatted_json_schema
    Skill_Matrix = json_output
    
    system_prompt = f"""
    You are an AI assistant that reformats resumes into a structured JSON format.
    Take the competency matrix and old resume as input, extract relevant details, and map them to the new resume format.
    Only respond with the new resume format as a JSON object that adheres strictly to the provided JSON Schema. Do not include any extra messages.
    **Instructions:**
            - Only use the given details; do not generate fictional information.
            - Follow the JSON structure exactly as provided.
            - Ensure the output starts directly with a valid JSON object (no extra text or explanations).
            - Try to keep the project description within 40-50 words.

            Generate the updated resume in JSON format:
            name and designation mandatory key value pairs and create a proper summarized objective a key  in for any kind of templete.
            make sure it follows the given format of formatted_json_schema wiht same json format with key value pairs. 
            Points to note : In the key "Education" form a sentance and give in points make a list and use that. Do not make up values , if you have no access to a value, don't make it up.
            Keep the names of the keyvalues in the json schema same. Skills also give as per the json schema.

            Make sure to keep the same key names as in the json schema for rest attributes.

            You are given the following details: You are given the following details:

            Your task is to extract relevant details and format them into the following structured JSON format:
            {new_resume_text}
    """
    
    chat_response = client.chat.complete(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
            
            **Skill Matrix (Extracted from External Data Sources):**
            {Skill_Matrix}
            
            """}
        ],
        response_format = {
          "type": "json_object",
      }
    )

    resume_content = chat_response.choices[0].message.content
    return resume_content

def LLM_CALL_8(formatted_json_schema, old_resume_text, old_cover_text, json_output):
    """Reformat old resume, cover letter, and skill matrix into structured JSON"""
    model = "mistral-large-latest"
    client = Mistral(api_key=config.API_KEY)

    new_resume_text = formatted_json_schema
    Content = old_resume_text
    Content2 = old_cover_text
    Skill_Matrix = json_output

    system_prompt = f"""
    You are an AI assistant that reformats resumes into a structured JSON format.
    Take the competency matrix and old resume as input, extract relevant details, and map them to the new resume format.
    Only respond with the new resume format as a JSON object that adheres strictly to the provided JSON Schema. Do not include any extra messages.
    **Instructions:**
            - Only use the given details; do not generate fictional information.
            - Follow the JSON structure exactly as provided.
            - Ensure the output starts directly with a valid JSON object (no extra text or explanations).
            - Try to keep the project description within 40-50 words.

            Generate the updated resume in JSON format:
            name and designation mandatory key value pairs and create a proper summarized objective a key  in for any kind of templete.
            make sure it follows the given format of formatted_json_schema wiht same json format with key value pairs. 
            Points to note : In the key "Education" form a sentance and give in points make a list and use that. Do not make up values , if you have no access to a value, don't make it up.
            Keep the names of the keyvalues in the json schema same. Skills also give as per the json schema.

            Make sure to keep the same key names as in the json schema for rest attributes.

            You are given the following details: You are given the following details:

            Your task is to extract relevant details and format them into the following structured JSON format:
            {new_resume_text}
    """
    
    
    chat_response = client.chat.complete(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
            
            **Skill Matrix (Extracted from External Data Sources):**
            {Skill_Matrix}

            **Old Resume (Extracted Text):**
            {Content}

            **Old Coverletter (Extracted Text):**
            {Content2}

            """}
        ],
        response_format = {
          "type": "json_object",
      }
    )

    resume_content = chat_response.choices[0].message.content
    return resume_content

def generate_cover_letter_from_resume(resume_summary: Dict) -> str:
    """Generates a professional cover letter based on the candidate's resume summary"""
    model = "mistral-large-latest"
    client = Mistral(api_key=config.API_KEY)
    
    system_prompt = """
    You are an AI assistant that creates professional cover letters based only on a candidate's resume summary.
    Your task is to analyze the resume summary, infer the candidate's expertise, and generate a well-structured cover letter.
    Ensure the tone is formal, engaging, and professional.
    """
    
    user_prompt = f"""
    Candidate Resume Summary:
    {json.dumps(resume_summary, indent=2)}
    
    Based on this summary, write a professional cover letter.
    Follow this structure:
    - Address the hiring manager (use "Dear Hiring Manager" if no specific name is provided).
    - Introduce the candidate and express general interest in roles that match their expertise.
    - Highlight key experiences, achievements, and skills relevant to their domain.
    - Conclude with enthusiasm and a call to action.
    - limit the words to 250 - 300
    
    Ensure the letter is formal and engaging.
    """
    
    chat_response = client.chat.complete(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "text"}
    )
    
    cover_letter = chat_response.choices[0].message.content
    return cover_letter