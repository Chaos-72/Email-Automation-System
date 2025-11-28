# backend/services/email_service.py
# import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# from dotenv import load_dotenv
# load_dotenv()

# SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
# SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@example.com")
# sg = SendGridAPIClient(SENDGRID_API_KEY)

# def send_email(subject: str, html_body: str, to_emails: list):
#     message = Mail(
#         from_email=SENDER_EMAIL,
#         to_emails=to_emails,
#         subject=subject,
#         html_content=html_body
#     )
#     try:
#         resp = sg.send(message)
#         return {"status_code": resp.status_code, "body": getattr(resp, "body", None)}
#     except Exception as e:
#         return {"status_code": 500, "error": str(e)}


# ==================
# Update code
# ==================

# backend/services/email_service.py
# ✅ UPDATED: USE GMAIL API VIA OAUTH

import base64
import os
from email.mime.text import MIMEText
from ..google_utils import get_google_services



def send_email(subject: str, html_body: str, to_emails: list):
    """Send email via Gmail API using OAuth token."""
    try:
        _, gmail_service = get_google_services()   #-> Initialize Gmail API client freshly each time
        message = MIMEText(html_body, "html")
        message["to"] = ", ".join(to_emails)
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        result = gmail_service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

        return {"status_code": 200, "id": result.get("id"), "labelIds": result.get("labelIds")}
    except Exception as e:
        # return {"status_code": 500, "error": str(e)}

        # Fall back to SendGrid if Gmail API fails
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        msg = Mail(from_email="you@example.com", to_emails=to_emails,
                subject=subject, html_content=html_body)
        resp = sg.send(msg)
        return {"status_code": resp.status_code}



