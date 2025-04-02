
# from fastapi import FastAPI, Depends, Request, Response
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse, JSONResponse
# import os
# import logging

# import config
# from services import data_service
# from routers import upload, search, generate, auth
# from utils import template_manager

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Initialize the FastAPI app
# app = FastAPI(title="Resume Automation API")

# # Add this CORS middleware BEFORE including any routers
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # For debugging CORS issues - Add a middleware to print request headers
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     # Log the request method and path
#     logger.info(f"Request: {request.method} {request.url.path}")
    
#     # Log headers for certain problematic endpoints
#     if request.url.path in ["/auth/me", "/auth/token", "/auth/signup", "/auth/logout"]:
#         logger.info(f"Headers: {dict(request.headers)}")
    
#     # Process the request
#     response = await call_next(request)
    
#     # Log the response status
#     logger.info(f"Response: {response.status_code}")
    
#     # For problematic endpoints, add CORS headers directly to the response
#     if request.url.path in ["/auth/me", "/auth/token", "/auth/signup", "/auth/logout"]:
#         response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "http://localhost:3000")
#         response.headers["Access-Control-Allow-Credentials"] = "true"
    
#     return response

# # Setup templates
# templates = Jinja2Templates(directory=config.TEMPLATES_DIR)

# # Include routers after CORS middleware
# app.include_router(upload.router)
# app.include_router(search.router)
# app.include_router(generate.router)
# app.include_router(auth.router)

# # Add a route to serve the HTML page
# @app.get("/", response_class=HTMLResponse)
# async def get_html():
#     with open(os.path.join(config.TEMPLATES_DIR, "index.html"), "r") as f:
#         html_content = f.read()
#     return HTMLResponse(content=html_content)

# # Handle OPTIONS requests explicitly for CORS preflight
# @app.options("/{full_path:path}")
# async def options_handler(request: Request, full_path: str):
#     response = JSONResponse(content={})
#     origin = request.headers.get("origin", "http://localhost:3000")
    
#     # Add CORS headers
#     response.headers["Access-Control-Allow-Origin"] = origin
#     response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
#     response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
#     response.headers["Access-Control-Allow-Credentials"] = "true"
#     response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
    
#     return response

# # Startup event
# @app.on_event("startup")
# async def startup_event():
#     logger.info("Starting up the application")
    
#     # Create default prompts
#     data_service.create_prompts()
    
#     # Display available templates
#     templates_info = template_manager.get_available_templates()
#     logger.info(f"Available resume templates: {len(templates_info['resume_templates'])}")
#     for template in templates_info['resume_templates']:
#         logger.info(f"  - Template {template['id']}: {template['name']}")
    
#     logger.info(f"Available cover letter templates: {len(templates_info['cover_letter_templates'])}")
#     for template in templates_info['cover_letter_templates']:
#         logger.info(f"  - Template {template['id']}: {template['name']}")

# # Mount static files directory 
# app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")

# # Run the application
# if __name__ == "__main__":
#     import uvicorn
#     logger.info("Starting server...")
#     uvicorn.run(app, host="0.0.0.0", port=8000)





from fastapi import FastAPI, Depends, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import os
import logging

import config
from services import data_service
from routers import upload, search, generate, auth, email  # Add the new email router import
from utils import template_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI(title="Resume Automation API")

# Add this CORS middleware BEFORE including any routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# For debugging CORS issues - Add a middleware to print request headers
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log the request method and path
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Log headers for certain problematic endpoints
    if request.url.path in ["/auth/me", "/auth/token", "/auth/signup", "/auth/logout"]:
        logger.info(f"Headers: {dict(request.headers)}")
    
    # Process the request
    response = await call_next(request)
    
    # Log the response status
    logger.info(f"Response: {response.status_code}")
    
    # For problematic endpoints, add CORS headers directly to the response
    if request.url.path in ["/auth/me", "/auth/token", "/auth/signup", "/auth/logout"]:
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "http://localhost:3000")
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Setup templates
templates = Jinja2Templates(directory=config.TEMPLATES_DIR)

# Include routers after CORS middleware
app.include_router(upload.router)
app.include_router(search.router)
app.include_router(generate.router)
app.include_router(auth.router)
app.include_router(email.router)  # Add the new email router

# Add a route to serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def get_html():
    with open(os.path.join(config.TEMPLATES_DIR, "index.html"), "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Handle OPTIONS requests explicitly for CORS preflight
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    response = JSONResponse(content={})
    origin = request.headers.get("origin", "http://localhost:3000")
    
    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
    
    return response

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")
    
    # Create default prompts
    data_service.create_prompts()
    
    # Display available templates
    templates_info = template_manager.get_available_templates()
    logger.info(f"Available resume templates: {len(templates_info['resume_templates'])}")
    for template in templates_info['resume_templates']:
        logger.info(f"  - Template {template['id']}: {template['name']}")
    
    logger.info(f"Available cover letter templates: {len(templates_info['cover_letter_templates'])}")
    for template in templates_info['cover_letter_templates']:
        logger.info(f"  - Template {template['id']}: {template['name']}")

# Mount static files directory 
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")

# Run the application
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
