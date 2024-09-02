import smtplib
import ssl
import argparse
import re
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from urllib.parse import urlparse

# Gmail SMTP server details
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# Email credentials
SENDER_EMAIL = "your_mail@gmail.com"  # Replace with your Gmail address
SENDER_PASSWORD = "your_password"      # Replace with your Gmail app password

# Log files
SUCCESS_LOG = "email_success.log"
FAILURE_LOG = "email_failure.log"

EMAIL_PREFIX = "security@"

# Function to clean and extract domain from URLs
def extract_domain(url):
    parsed_uri = urlparse(url)
    domain = parsed_uri.netloc if parsed_uri.netloc else parsed_uri.path
    domain = domain.replace("www.", "")
    return domain.split(':')[0]

# Function to send email
def send_email(domain):
    receiver_email = f"{EMAIL_PREFIX}{domain}"
    message = MIMEMultipart("alternative")
    message["Subject"] = "Hey! Do You Pay for Bug Reports?"
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <p style="font-family: Georgia, serif; font-size: 24px;">Hi {domain} team,</p>
        <p style="font-family: Georgia, serif; font-size: 24px;">Hello!!!</p>
        <p style="font-family: Georgia, serif; font-size: 24px;">Thank you for your time and help!</p>
        <p style="font-family: Georgia, serif; font-size: 24px;">Best wishes,<br>Your Name</p>
    </body>
    </html>
    """
    part = MIMEText(html_content, "html")
    message.attach(part)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())
        
        log_success(domain)
        return True
    except Exception as e:
        log_failure(domain, str(e))
        print(e)
        return False

# Function to log successful emails
def log_success(domain):
    with open(SUCCESS_LOG, "a") as f:
        f.write(f"{datetime.now()} - Email sent to: {EMAIL_PREFIX}{domain}\n")

# Function to log failed emails
def log_failure(domain, error):
    with open(FAILURE_LOG, "a") as f:
        f.write(f"{datetime.now()} - Failed to send email to: {EMAIL_PREFIX}{domain} - Error: {error}\n")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Send emails to domain security contacts.")
    parser.add_argument("-f", "--file", required=True, help="File containing list of URLs/domains")
    args = parser.parse_args()

    # Read processed domains from success log to avoid duplicate emails
    processed_domains = set()
    try:
        with open(SUCCESS_LOG, "r") as f:
            for line in f:
                domain = line.split("Email sent to: ")[1].strip()
                processed_domains.add(domain)
    except FileNotFoundError:
        pass

    with open(args.file, "r") as file:
        for line in file:
            time.sleep(10)
            domain = extract_domain(line.strip())
            if domain and f"{EMAIL_PREFIX}{domain}" not in processed_domains:
                print(f"Sending email to: {EMAIL_PREFIX}{domain}")
                if send_email(domain):
                    processed_domains.add(domain)
                else:
                    print(f"Failed to send email to: {EMAIL_PREFIX}{domain}")
            else:
                print(f"Already sent mail to {EMAIL_PREFIX}{domain}")

if __name__ == "__main__":
    main()
