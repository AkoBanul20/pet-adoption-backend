# email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from jinja2 import Environment, FileSystemLoader

# Email Settings
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.yourprovider.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "your_smtp_user")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_smtp_password")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@yourdomain.com")
BASE_URL = os.getenv("BASE_URL", "http://yourdomain.com")

# Load the Jinja2 templates
template_dir = os.path.join(os.path.dirname(__file__), "email_templates")
env = Environment(loader=FileSystemLoader(template_dir))


def send_email(to_email: str, subject: str, html_content: str):
    """
    Send an email with HTML content.
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = EMAIL_FROM
    message["To"] = to_email

    # Attach HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, message.as_string())
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_verification_email(email: str, token: str):
    """
    Send a verification email with a token.
    """
    template = env.get_template("verification_email.html")
    verification_url = f"{BASE_URL}/verify?token={token}"
    
    html_content = template.render(
        verification_url=verification_url,
        email=email
    )
    
    return send_email(
        to_email=email,
        subject="Verify Your Email Address",
        html_content=html_content
    )


def send_password_reset_email(email: str, token: str):
    """
    Send a password reset email with a token.
    """
    template = env.get_template("reset_password_email.html")
    reset_url = f"{BASE_URL}/reset-password?token={token}"
    
    html_content = template.render(
        reset_url=reset_url,
        email=email
    )
    
    return send_email(
        to_email=email,
        subject="Reset Your Password",
        html_content=html_content
    )