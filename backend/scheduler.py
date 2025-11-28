# # backend/scheduler.py
# from apscheduler.schedulers.background import BackgroundScheduler
# from datetime import datetime
# from .db import SessionLocal
# from .models import Email
# from .services.email_service import send_email
# import logging

# logger = logging.getLogger("scheduler")

# scheduler = BackgroundScheduler()

# def check_and_send_due_emails():
#     db = SessionLocal()
#     try:
#         now = datetime.utcnow()
#         pending = db.query(Email).filter(Email.sent == False, Email.send_time != None, Email.send_time <= now).all()
#         for e in pending:
#             logger.info(f"Sending scheduled email id={e.id} to {e.recipients}")
#             resp = send_email(e.subject, e.body_html, e.recipients)
#             if resp.get("status_code") and int(resp["status_code"]) in (200, 202):
#                 e.sent = True
#                 db.commit()
#             else:
#                 logger.error(f"Failed to send email id={e.id}: {resp}")
#     except Exception as ex:
#         logger.exception("Scheduler error: " + str(ex))
#     finally:
#         db.close()

# def start_scheduler():
#     scheduler.add_job(check_and_send_due_emails, 'interval', seconds=30, id="check_emails", replace_existing=True)
#     scheduler.start()


# ==================
# Updated code
# =================


# backend/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone
from .db import SessionLocal
from .models import Email
from .services.email_service import send_email

scheduler = BackgroundScheduler()

def check_and_send_scheduled_emails():
    """Check database for due emails and send them."""
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        pending_emails = db.query(Email).filter(
            Email.sent == False,
            Email.send_time != None,
            Email.send_time <= now
        ).all()

        for email in pending_emails:
            try:
                recipients = email.recipients if isinstance(email.recipients, list) else []

                # Log the attempt to send the email
                print(f"[Scheduler] Attempting to send Email ID {email.id} to {recipients}")
                result = send_email(email.subject, email.body_html, recipients)
                print(f"[Scheduler] Gmail API result: {result}")

                if result.get("status_code") == 200:
                    email.sent = True
                    print(f"[Scheduler] Sent scheduled email (ID: {email.id})")
                else:
                    print(f"[Scheduler] Failed to send email ID {email.id}: {result}")
            except Exception as e:
                print(f"[Scheduler] Error sending email ID {email.id}: {e}")

        db.commit()
    finally:
        db.close()

def start_scheduler():
    """Start APScheduler background job."""
    scheduler.add_job(check_and_send_scheduled_emails, "interval", minutes=1)
    scheduler.start()
    print("✅ APScheduler started — checking for scheduled emails every minute.")
