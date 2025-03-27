

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config
import urllib.parse  # Import for URL encoding

logger = logging.getLogger(__name__)

async def send_password_reset_email(recipient_email: str, reset_url: str):
    """
    Send password reset email to user
    """
    try:
        # Email configuration
        sender_email = "praneethvvsss@gmail.com"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "praneethvvsss@gmail.com"
        smtp_password = config.SMTP_PASSWORD
        
        # Ensure token is properly URL encoded in the reset URL
        # Extract parts of the URL
        parts = reset_url.split("?token=")
        if len(parts) == 2:
            base_url = parts[0]
            token = parts[1]
            # Ensure token is properly URL encoded
            encoded_token = urllib.parse.quote(token)
            reset_url = f"{base_url}?token={encoded_token}"
        
        logger.info(f"Sending reset email to {recipient_email} with reset URL: {reset_url}")
        print(f"Reset URL: {reset_url}")
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Reset Your Password - Resume Automation Tool"
        message["From"] = sender_email
        message["To"] = recipient_email
        
        # Create the plain-text and HTML version of your message
        text = f"""
        Hello,
        
        You requested to reset your password for your Resume Automation Tool account.
        
        Please click the link below to reset your password:
        {reset_url}
        
        This link will expire in 24 hours.
        
        If you did not request a password reset, please ignore this email.
        
        Regards,
        Resume Automation Tool Team
        """
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
            <div style="text-align: center; margin-bottom: 20px;">
              <h2 style="color: #4361ee;">Reset Your Password</h2>
            </div>
            <p>Hello,</p>
            <p>You requested to reset your password for your Resume Automation Tool account.</p>
            <p>Please click the button below to reset your password:</p>
            <p style="text-align: center; margin: 30px 0;">
              <a href="{reset_url}" style="background-color: #4361ee; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
            </p>
            <p>If the button above doesn't work, copy and paste this URL into your browser:</p>
            <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 14px;">
              {reset_url}
            </p>
            <p style="font-size: 0.9em;">This link will expire in 24 hours.</p>
            <p style="font-size: 0.9em;">If you did not request a password reset, please ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 0.8em; color: #777; text-align: center;">Regards,<br>Resume Automation Tool Team</p>
          </body>
        </html>
        """
        
        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        
        # Add HTML/plain-text parts to MIMEMultipart message
        message.attach(part1)
        message.attach(part2)
        
        # Create secure connection with server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(
                sender_email, recipient_email, message.as_string()
            )
        
        logger.info(f"Password reset email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        # Include full traceback for better debugging
        import traceback
        logger.error(traceback.format_exc())
        return False