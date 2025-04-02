# from fastapi import APIRouter, Depends, HTTPException, Body, BackgroundTasks
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel, EmailStr
# from typing import Optional, List
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.application import MIMEApplication
# import os
# import logging
# from datetime import datetime

# # Import your existing auth and config modules
# import config
# from services.auth_service import get_current_active_user
# from models.schema import User

# # Configure logging
# logger = logging.getLogger(__name__)

# # Create router
# router = APIRouter(
#     prefix="/email",
#     tags=["email"],
#     responses={404: {"description": "Not found"}},
# )

# # Models
# class EmailRequest(BaseModel):
#     recipient_email: EmailStr
#     subject: str
#     body: str
#     resume_file_path: str
#     cover_letter_file_path: str
#     cc_emails: Optional[List[EmailStr]] = []
    
# class EmailResponse(BaseModel):
#     message: str
#     success: bool
#     timestamp: str

# # Email sending function
# def send_email(
#     recipient_email: str,
#     subject: str,
#     body: str,
#     resume_file_path: str,
#     cover_letter_file_path: str,
#     cc_emails: List[str] = []
# ):
#     # Create message container
#     msg = MIMEMultipart()
#     msg['From'] = config.EMAIL_SENDER
#     msg['To'] = recipient_email
#     msg['Subject'] = subject
    
#     if cc_emails:
#         msg['Cc'] = ", ".join(cc_emails)

#     # Attach email body
#     msg.attach(MIMEText(body, 'html'))
    
#     # Attach resume
#     if os.path.exists(resume_file_path):
#         with open(resume_file_path, 'rb') as file:
#             resume_attachment = MIMEApplication(file.read(), Name=os.path.basename(resume_file_path))
#         resume_attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(resume_file_path)}"'
#         msg.attach(resume_attachment)
#     else:
#         logger.error(f"Resume file not found: {resume_file_path}")
#         raise FileNotFoundError(f"Resume file not found: {resume_file_path}")
    
#     # Attach cover letter
#     if os.path.exists(cover_letter_file_path):
#         with open(cover_letter_file_path, 'rb') as file:
#             cover_letter_attachment = MIMEApplication(file.read(), Name=os.path.basename(cover_letter_file_path))
#         cover_letter_attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(cover_letter_file_path)}"'
#         msg.attach(cover_letter_attachment)
#     else:
#         logger.error(f"Cover letter file not found: {cover_letter_file_path}")
#         raise FileNotFoundError(f"Cover letter file not found: {cover_letter_file_path}")
    
#     # Calculate recipients list (including CC)
#     recipients = [recipient_email] + cc_emails
    
#     try:
#         # Connect to mail server
#         server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
#         server.starttls()
#         server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        
#         # Send email
#         server.sendmail(config.EMAIL_SENDER, recipients, msg.as_string())
#         server.quit()
        
#         logger.info(f"Email sent successfully to {recipient_email}")
#         return True
#     except Exception as e:
#         logger.error(f"Failed to send email: {str(e)}")
#         raise e

# # Background task to send email
# def send_email_background(
#     recipient_email: str,
#     subject: str,
#     body: str,
#     resume_file_path: str,
#     cover_letter_file_path: str,
#     cc_emails: List[str] = []
# ):
#     try:
#         send_email(
#             recipient_email=recipient_email,
#             subject=subject,
#             body=body,
#             resume_file_path=resume_file_path,
#             cover_letter_file_path=cover_letter_file_path,
#             cc_emails=cc_emails
#         )
#         logger.info(f"Background email sent successfully to {recipient_email}")
#     except Exception as e:
#         logger.error(f"Background email sending failed: {str(e)}")

# # API Routes
# @router.post("/send-application", response_model=EmailResponse)
# async def send_application_email(
#     background_tasks: BackgroundTasks,
#     email_request: EmailRequest,
#     current_user: User = Depends(get_current_active_user)
# ):
#     try:
#         # Validate file paths
#         if not os.path.exists(email_request.resume_file_path):
#             raise HTTPException(status_code=404, detail=f"Resume file not found: {email_request.resume_file_path}")
            
#         if not os.path.exists(email_request.cover_letter_file_path):
#             raise HTTPException(status_code=404, detail=f"Cover letter file not found: {email_request.cover_letter_file_path}")
        
#         # Use background tasks to send email asynchronously
#         background_tasks.add_task(
#             send_email_background,
#             recipient_email=email_request.recipient_email,
#             subject=email_request.subject,
#             body=email_request.body,
#             resume_file_path=email_request.resume_file_path,
#             cover_letter_file_path=email_request.cover_letter_file_path,
#             cc_emails=email_request.cc_emails
#         )
        
#         # Return immediately with a success message
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         return {
#             "message": f"Email to {email_request.recipient_email} is being sent in the background", 
#             "success": True,
#             "timestamp": timestamp
#         }
        
#     except FileNotFoundError as e:
#         logger.error(f"File not found: {str(e)}")
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         logger.error(f"Error sending application: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# # Endpoint to send test email
# @router.post("/test", response_model=EmailResponse)
# async def test_email(
#     recipient_email: EmailStr = Body(...),
#     current_user: User = Depends(get_current_active_user)
# ):
#     try:
#         # Create message container
#         msg = MIMEMultipart()
#         msg['From'] = config.EMAIL_SENDER
#         msg['To'] = recipient_email
#         msg['Subject'] = "Test Email from Resume Automation System"
        
#         # Create a simple test message
#         body = f"""
#         <html>
#             <body>
#                 <h2>Resume Automation System - Test Email</h2>
#                 <p>Hello,</p>
#                 <p>This is a test email to verify that the email sending functionality is working correctly.</p>
#                 <p>If you're receiving this, your email configuration is working!</p>
#                 <p>Best regards,<br/>Resume Automation System</p>
#             </body>
#         </html>
#         """
#         msg.attach(MIMEText(body, 'html'))
        
#         # Send email
#         server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
#         server.starttls()
#         server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
#         server.sendmail(config.EMAIL_SENDER, recipient_email, msg.as_string())
#         server.quit()
        
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         return {
#             "message": f"Test email sent successfully to {recipient_email}", 
#             "success": True,
#             "timestamp": timestamp
#         }
#     except Exception as e:
#         logger.error(f"Error sending test email: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to send test email: {str(e)}")


from fastapi import APIRouter, Depends, HTTPException, Body, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import logging
from datetime import datetime
import ssl  # Add SSL for more secure connection

# Import your existing auth and config modules
import config
from services.auth_service import get_current_active_user
from models.schema import User

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/email",
    tags=["email"],
    responses={404: {"description": "Not found"}},
)

# Models
class EmailRequest(BaseModel):
    recipient_email: EmailStr
    subject: str
    body: str
    resume_file_path: str
    cover_letter_file_path: str
    cc_emails: Optional[List[EmailStr]] = []
    
class EmailResponse(BaseModel):
    message: str
    success: bool
    timestamp: str

# Email sending function
def send_email(
    recipient_email: str,
    subject: str,
    body: str,
    resume_file_path: str,
    cover_letter_file_path: str,
    cc_emails: List[str] = []
):
    # Create message container
    msg = MIMEMultipart()
    msg['From'] = config.EMAIL_SENDER
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    if cc_emails:
        msg['Cc'] = ", ".join(cc_emails)

    # Attach email body
    msg.attach(MIMEText(body, 'html'))
    
    # Attach resume
    if os.path.exists(resume_file_path):
        with open(resume_file_path, 'rb') as file:
            resume_attachment = MIMEApplication(file.read(), Name=os.path.basename(resume_file_path))
        resume_attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(resume_file_path)}"'
        msg.attach(resume_attachment)
    else:
        logger.error(f"Resume file not found: {resume_file_path}")
        raise FileNotFoundError(f"Resume file not found: {resume_file_path}")
    
    # Attach cover letter
    if os.path.exists(cover_letter_file_path):
        with open(cover_letter_file_path, 'rb') as file:
            cover_letter_attachment = MIMEApplication(file.read(), Name=os.path.basename(cover_letter_file_path))
        cover_letter_attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(cover_letter_file_path)}"'
        msg.attach(cover_letter_attachment)
    else:
        logger.error(f"Cover letter file not found: {cover_letter_file_path}")
        raise FileNotFoundError(f"Cover letter file not found: {cover_letter_file_path}")
    
    # Calculate recipients list (including CC)
    recipients = [recipient_email] + cc_emails
    
    try:
        # Modified email sending code with better error handling for Gmail
        logger.info(f"Attempting to connect to mail server: {config.SMTP_SERVER}:{config.SMTP_PORT}")
        
        # For Gmail, we'll create a more secure context
        context = ssl.create_default_context()
        
        # Connect to mail server
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.ehlo()  # Identify ourselves to the server
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Re-identify ourselves over the secured connection
        
        # Verbose login to debug auth issues
        logger.info(f"Attempting to login with username: {config.SMTP_USERNAME}")
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        logger.info("SMTP login successful")
        
        # Send email
        logger.info(f"Sending email from {config.EMAIL_SENDER} to {recipients}")
        server.sendmail(config.EMAIL_SENDER, recipients, msg.as_string())
        server.quit()
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {str(e)}")
        error_msg = """
        Gmail authentication failed. This is likely due to one of these reasons:
        1. The password is incorrect
        2. You need to use an App Password instead of your regular password
        3. You need to allow 'Less secure app access' in your Google account
        
        Please go to https://myaccount.google.com/apppasswords to create an App Password,
        then update your environment variables.
        """
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise e

# Background task to send email
def send_email_background(
    recipient_email: str,
    subject: str,
    body: str,
    resume_file_path: str,
    cover_letter_file_path: str,
    cc_emails: List[str] = []
):
    try:
        send_email(
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            resume_file_path=resume_file_path,
            cover_letter_file_path=cover_letter_file_path,
            cc_emails=cc_emails
        )
        logger.info(f"Background email sent successfully to {recipient_email}")
    except Exception as e:
        logger.error(f"Background email sending failed: {str(e)}")

# API Routes
@router.post("/send-application", response_model=EmailResponse)
async def send_application_email(
    background_tasks: BackgroundTasks,
    email_request: EmailRequest,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Log the request details
        logger.info(f"Email send request received for recipient: {email_request.recipient_email}")
        logger.info(f"Resume path: {email_request.resume_file_path}")
        logger.info(f"Cover letter path: {email_request.cover_letter_file_path}")
        
        # Validate file paths
        if not os.path.exists(email_request.resume_file_path):
            logger.error(f"Resume file not found: {email_request.resume_file_path}")
            raise HTTPException(status_code=404, detail=f"Resume file not found: {email_request.resume_file_path}")
            
        if not os.path.exists(email_request.cover_letter_file_path):
            logger.error(f"Cover letter file not found: {email_request.cover_letter_file_path}")
            raise HTTPException(status_code=404, detail=f"Cover letter file not found: {email_request.cover_letter_file_path}")
        
        # Use background tasks to send email asynchronously
        background_tasks.add_task(
            send_email_background,
            recipient_email=email_request.recipient_email,
            subject=email_request.subject,
            body=email_request.body,
            resume_file_path=email_request.resume_file_path,
            cover_letter_file_path=email_request.cover_letter_file_path,
            cc_emails=email_request.cc_emails
        )
        
        # Return immediately with a success message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "message": f"Email to {email_request.recipient_email} is being sent in the background", 
            "success": True,
            "timestamp": timestamp
        }
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending application: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Endpoint to send test email
@router.post("/test", response_model=EmailResponse)
async def test_email(
    recipient_email: EmailStr = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    try:
        logger.info(f"Test email requested to: {recipient_email}")
        
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = config.EMAIL_SENDER
        msg['To'] = recipient_email
        msg['Subject'] = "Test Email from Resume Automation System"
        
        # Create a simple test message
        body = f"""
        <html>
            <body>
                <h2>Resume Automation System - Test Email</h2>
                <p>Hello,</p>
                <p>This is a test email to verify that the email sending functionality is working correctly.</p>
                <p>If you're receiving this, your email configuration is working!</p>
                <p>Best regards,<br/>Resume Automation System</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        # Create an SSL context for secure connection
        context = ssl.create_default_context()
        
        # Send email
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        server.sendmail(config.EMAIL_SENDER, recipient_email, msg.as_string())
        server.quit()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "message": f"Test email sent successfully to {recipient_email}", 
            "success": True,
            "timestamp": timestamp
        }
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {str(e)}")
        error_msg = """
        Gmail authentication failed. This is likely due to one of these reasons:
        1. The password is incorrect
        2. You need to use an App Password instead of your regular password
        3. You need to allow 'Less secure app access' in your Google account
        
        Please go to https://myaccount.google.com/apppasswords to create an App Password,
        then update your environment variables.
        """
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send test email: {str(e)}")