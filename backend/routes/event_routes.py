# # backend/routes/event_routes.py
# from fastapi import APIRouter, HTTPException, Depends
# from pydantic import BaseModel, EmailStr
# from typing import List
# from datetime import datetime, timedelta
# from ..services.calendar_service import list_conflicts, cancel_events, create_event
# from ..services.llm_service import generate_email
# from ..services.email_service import send_email
# from ..db import get_db
# from sqlalchemy.orm import Session
# from ..models import Event, Email as EmailModel
# import dateutil.parser
# import os

# router = APIRouter(prefix="/api/event", tags=["event"])

# class CreateEventReq(BaseModel):
#     title: str
#     start_iso: str  # ISO format
#     end_iso: str
#     attendees: List[EmailStr] = []
#     cancel_conflicts: bool = False
#     notify: bool = True

# @router.post("/create")
# def create_event_endpoint(req: CreateEventReq, db: Session = Depends(get_db)):
#     try:
#         # Optionally detect conflicts
#         conflicts = list_conflicts(req.start_iso, req.end_iso)
#         conflict_ids = [c["id"] for c in conflicts if c.get("id")]
#         canceled = []
#         if req.cancel_conflicts and conflict_ids:
#             canceled = cancel_events(conflict_ids)
#         # Create event
#         created = create_event(req.title, req.start_iso, req.end_iso, list(req.attendees))
#         meet_link = created.get("meet_link") or created.get("htmlLink")
#         # persist event
#         ev = Event(title=req.title, start=dateutil.parser.isoparse(req.start_iso), end=dateutil.parser.isoparse(req.end_iso),
#                    attendees=list(req.attendees), google_event_id=created.get("event_id"), meet_link=meet_link)
#         db.add(ev)
#         db.commit()
#         db.refresh(ev)
#         # generate notification email via LLM
#         if req.notify and req.attendees:
#             instruction = f"Create a meeting invite email for event '{req.title}' at {req.start_iso}. Include this meeting link: {meet_link}. Keep it short and professional."
#             email_out = generate_email(instruction, {"attendees": req.attendees})
#             # send immediate email
#             send_resp = send_email(email_out.get("subject"), email_out.get("body_html"), req.attendees)
#             # log email in DB
#             mail = EmailModel(subject=email_out.get("subject"), body_html=email_out.get("body_html"),
#                               recipients=list(req.attendees), send_time=None, sent=(int(send_resp.get("status_code",0)) in (200,202)))
#             db.add(mail)
#             db.commit()
#         return {"ok": True, "event": {"id": ev.id, "google_event_id": ev.google_event_id, "meet_link": meet_link}, "canceled_conflicts": canceled}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))




# =================
# 
# Updated code
# 
# =====================

# backend/routes/event_routes.py
import os  # ✅ Added import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime, timedelta, timezone  # ✅ Added timezone
from ..services.calendar_service import list_conflicts, cancel_events, create_event
from ..services.llm_service import generate_email
from ..services.email_service import send_email
from ..services.contact_service import find_email_by_name  # ✅ Added import for contact service
from ..db import get_db
from sqlalchemy.orm import Session
from ..models import Event, Email as EmailModel
import dateutil.parser

router = APIRouter(prefix="/api/event", tags=["event"])

class CreateEventReq(BaseModel):
    title: str
    start_iso: str  # ISO format
    end_iso: str
    attendees: List[EmailStr] = []
    cancel_conflicts: bool = False
    notify: bool = True


@router.post("/create")
def create_event_endpoint(req: CreateEventReq, db: Session = Depends(get_db)):
    try:
        # Convert ISO strings to naive UTC datetimes
        start_dt = dateutil.parser.isoparse(req.start_iso)
        if start_dt.tzinfo:
            start_dt = start_dt.astimezone(timezone.utc).replace(tzinfo=None)
        end_dt = dateutil.parser.isoparse(req.end_iso)
        if end_dt.tzinfo:
            end_dt = end_dt.astimezone(timezone.utc).replace(tzinfo=None)


        # This ensure start_iso and end_iso are in UTC --> Testing
        start_iso = start_dt.astimezone(timezone.utc).isoformat()
        end_iso = end_dt.astimezone(timezone.utc).isoformat()

        # Optionally detect conflicts
        conflicts = list_conflicts(req.start_iso, req.end_iso)
        conflict_ids = [c["id"] for c in conflicts if c.get("id")]
        canceled = []

        if req.cancel_conflicts and conflict_ids:
            # cancel overlapping events
            canceled = cancel_events(conflict_ids)
        elif conflicts:
            # Find next available slot after the latest conflict automatically
            start_dt = dateutil.parser.isoparse(req.start_iso)
            end_dt = dateutil.parser.isoparse(req.end_iso)
            while list_conflicts(start_dt.isoformat(), end_dt.isoformat()):
                start_dt += timedelta(minutes=30)
                end_dt = start_dt + timedelta(hours=1)

            req.start_iso = start_dt.isoformat()
            req.end_iso = end_dt.isoformat()


        # Create event in Google Calendar
        recurrence_rule = getattr(req, "recurrence", None)  

        # contact service to resolve names to emails
        resolved_attendees = []
        for a in req.attendees:
            # If user passed a name, resolve to email
            email = find_email_by_name(a) or a
            resolved_attendees.append(email)
        
        created = create_event(req.title, req.start_iso, req.end_iso, resolved_attendees)
        # created = create_event(req.title, req.start_iso, req.end_iso, list(req.attendees))
        meet_link = created.get("meet_link") or created.get("htmlLink")

        # Persist event in DB
        ev = Event(
            title=req.title,
            start=start_dt,
            end=end_dt,
            attendees=list(req.attendees),
            google_event_id=created.get("event_id"),
            meet_link=meet_link
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)

        # Generate notification email via LLM
        if req.notify and req.attendees:
            instruction = f"Create a meeting invite email for event '{req.title}' at {req.start_iso}. Include this meeting link: {meet_link}. Keep it short and professional."
            email_out = generate_email(instruction, {"attendees": req.attendees})
            send_resp = send_email(email_out.get("subject"), email_out.get("body_html"), req.attendees)
            # Log email in DB
            mail = EmailModel(
                subject=email_out.get("subject"),
                body_html=email_out.get("body_html"),
                recipients=list(req.attendees),
                send_time=None,
                sent=(int(send_resp.get("status_code",0)) in (200,202))
            )
            db.add(mail)
            db.commit()

        return {"ok": True, "event": {"id": ev.id, "google_event_id": ev.google_event_id, "meet_link": meet_link}, "canceled_conflicts": canceled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
