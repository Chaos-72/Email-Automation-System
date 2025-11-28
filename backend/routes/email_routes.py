# # backend/routes/email_routes.py
# from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
# from pydantic import BaseModel, EmailStr
# from typing import List
# from ..services.email_service import send_email
# from ..services.llm_service import generate_email
# from ..db import get_db
# from ..models import Email
# from sqlalchemy.orm import Session
# import csv, io, dateutil.parser
# from datetime import datetime, timezone

# router = APIRouter(prefix="/api/email", tags=["email"])

# class SendEmailReq(BaseModel):
#     subject: str
#     body_html: str
#     recipients: List[EmailStr]
#     send_time: str = None  # optional ISO string

# @router.post("/send")
# def send_email_endpoint(req: SendEmailReq, db: Session = Depends(get_db)):
#     try:
#         send_time = None
#         if req.send_time and req.send_time.strip() !="":
#             send_time = dateutil.parser.isoparse(req.send_time)
#             # convert to UTC if it's offset-aware
#             if send_time.tzinfo:
#                 send_time = send_time.astimezone(timezone.utc).replace(tzinfo=None)

#         if send_time and send_time > datetime.utcnow():
#             # schedule
#             mail = Email(subject=req.subject, body_html=req.body_html, recipients=list(req.recipients), send_time=send_time, sent=False)
#             db.add(mail)
#             db.commit()
#             return {"ok": True, "status": "scheduled", "email_id": mail.id}
#         else:
#             resp = send_email(req.subject, req.body_html, req.recipients)
#             sent_flag = int(resp.get("status_code",0)) in (200,202)
#             mail = Email(subject=req.subject, body_html=req.body_html, recipients=list(req.recipients), send_time=None, sent=sent_flag)
#             db.add(mail)
#             db.commit()
#             return {"ok": True, "status": "sent", "send_response": resp}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/bulk_upload")
# async def bulk_upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     """
#     Upload CSV with columns: email,name,company,...
#     For demo: generate sample for first 3 recipients and return previews.
#     """
#     try:
#         content = await file.read()
#         s = content.decode()
#         reader = csv.DictReader(io.StringIO(s))
#         rows = list(reader)
#         previews = []
#         for r in rows[:3]:
#             recipient = {"email": r.get("email"), "name": r.get("name"), "company": r.get("company")}
#             instruction = f"Write a personalized follow-up email for {recipient.get('name')} at {recipient.get('company')}."
#             email_out = generate_email(instruction, recipient)
#             previews.append({"recipient": recipient, "email": email_out})
#         # For demo, do NOT auto-send; frontend should call /email/send with confirmed list
#         return {"ok": True, "previews": previews, "total": len(rows)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# =============
# 
# Updated code
# 
# ============

# backend/routes/email_routes.py
import os  # ✅ Added import os
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, EmailStr
from typing import List
from ..services.email_service import send_email
from ..services.llm_service import generate_email
from ..db import get_db
from ..models import Email
from sqlalchemy.orm import Session
import csv, io, dateutil.parser
from datetime import datetime, timezone  # ✅ Added timezone

router = APIRouter(prefix="/api/email", tags=["email"])

class SendEmailReq(BaseModel):
    subject: str
    body_html: str
    recipients: List[EmailStr]
    send_time: str = None  # optional ISO string

@router.post("/send")
def send_email_endpoint(req: SendEmailReq, db: Session = Depends(get_db)):
    try:
        # ✅ Handle empty send_time safely
        send_time = None
        if req.send_time and req.send_time.strip() != "":
            send_time = dateutil.parser.isoparse(req.send_time)
            # ✅ Convert offset-aware datetime to naive UTC for DB
            if send_time.tzinfo:
                send_time = send_time.astimezone(timezone.utc).replace(tzinfo=None)

        if send_time and send_time > datetime.utcnow():
            # schedule email
            mail = Email(
                subject=req.subject,
                body_html=req.body_html,
                recipients=list(req.recipients),
                send_time=send_time,
                sent=False
            )
            db.add(mail)
            db.commit()
            return {"ok": True, "status": "scheduled", "email_id": mail.id}
        else:
            # send immediately
            resp = send_email(req.subject, req.body_html, req.recipients)
            sent_flag = int(resp.get("status_code",0)) in (200,202)
            mail = Email(
                subject=req.subject,
                body_html=req.body_html,
                recipients=list(req.recipients),
                send_time=None,
                sent=sent_flag
            )
            db.add(mail)
            db.commit()
            return {"ok": True, "status": "sent", "send_response": resp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk_upload")
async def bulk_upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload CSV with columns: email,name,company,...
    For demo: generate sample for first 3 recipients and return previews.
    """
    try:
        content = await file.read()
        s = content.decode()
        reader = csv.DictReader(io.StringIO(s))
        rows = list(reader)
        previews = []
        for r in rows[:3]:
            recipient = {"email": r.get("email"), "name": r.get("name"), "company": r.get("company")}
            instruction = f"Write a personalized follow-up email for {recipient.get('name')} at {recipient.get('company')}."
            email_out = generate_email(instruction, recipient)
            previews.append({"recipient": recipient, "email": email_out})
        return {"ok": True, "previews": previews, "total": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
