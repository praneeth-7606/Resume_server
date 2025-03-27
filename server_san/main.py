from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

import config
from services import data_service
from routers import upload, search, generate
from utils import template_manager  # Import template manager

# Initialize the FastAPI app
app = FastAPI(title="Resume Automation API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Adjust for your React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates
templates = Jinja2Templates(directory=config.TEMPLATES_DIR)

# Include routers
app.include_router(upload.router)
app.include_router(search.router)
app.include_router(generate.router)

# Add a route to serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def get_html():
    with open(os.path.join(config.TEMPLATES_DIR, "index.html"), "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Startup event
@app.on_event("startup")
async def startup_event():
    # Create default prompts
    data_service.create_prompts()
    
    # Display available templates
    templates_info = template_manager.get_available_templates()
    print(f"Available resume templates: {len(templates_info['resume_templates'])}")
    for template in templates_info['resume_templates']:
        print(f"  - Template {template['id']}: {template['name']}")
    
    print(f"Available cover letter templates: {len(templates_info['cover_letter_templates'])}")
    for template in templates_info['cover_letter_templates']:
        print(f"  - Template {template['id']}: {template['name']}")

# Mount static files directory
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)