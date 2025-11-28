# # backend/services/calendar_service.py
# from google.oauth2.service_account import Credentials
# from googleapiclient.discovery import build
# import os
# from ..google_utils import get_google_services
# from datetime import datetime, timedelta
# from typing import List

# GOOGLE_SA_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json")
# # SCOPES = ["https://www.googleapis.com/auth/calendar"]

# # Initialize via OAuth
# calendar_service, _ = get_google_services()

# creds = Credentials.from_service_account_file(GOOGLE_SA_FILE, scopes=SCOPES)
# # service = build("calendar", "v3", credentials=creds, cache_discovery=False)

# TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# def list_conflicts(start_iso: str, end_iso: str, calendar_id: str = "primary"):
#     events_result = calendar_service.events().list(
#         calendarId=calendar_id, 
#         timeMin=start_iso, 
#         timeMax=end_iso, 
#         singleEvents=True, 
#         orderBy='startTime'
#     ).execute()
#     return events_result.get("items", [])

# def cancel_events(event_ids: List[str], calendar_id: str = "primary"):
#     results = []
#     for eid in event_ids:
#         try:
#             calendar_service.events().delete(calendarId=calendar_id, eventId=eid).execute()
#             results.append({"event_id": eid, "status": "deleted"})
#         except Exception as e:
#             results.append({"event_id": eid, "status": f"error: {str(e)}"})
#     return results

# def create_event(title: str, start_iso: str, end_iso: str, attendees: List[str] = None, calendar_id: str = "primary"):
#     if attendees is None:
#         attendees = []
#     event_body = {
#         "summary": title,
#         "start": {"dateTime": start_iso, "timeZone": TIMEZONE},
#         "end": {"dateTime": end_iso, "timeZone": TIMEZONE},
#         "attendees": [{"email": a} for a in attendees],
#         "conferenceData": {"createRequest": {"requestId": f"meet-{int(datetime.utcnow().timestamp())}"}},
#     }
#     created = calendar_service.events().insert(
#         calendarId=calendar_id, 
#         body=event_body, 
#         conferenceDataVersion=1
#     ).execute()

#     return {
#         "event_id": created.get("id"),
#         "htmlLink": created.get("htmlLink"),
#         "meet_link": created.get("hangoutLink")
#           or (created.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri")
#                if created.get("conferenceData") else None),
#         "raw": created
#     }


# ===================
# 
# Updated code

# ===================



# backend/services/calendar_service.py
# ✅ UPDATED TO USE OAUTH INSTEAD OF SERVICE ACCOUNT
from ..google_utils import get_google_services
from datetime import datetime
from typing import List
import os

# GOOGLE_SA_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json")

TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# TIMEZONE = "Asia/Kolkata"


def list_conflicts(start_iso: str, end_iso: str, calendar_id: str = "primary"):
    # Initialize via OAuth
    calendar_service, _ = get_google_services()
    events_result = calendar_service.events().list(
        calendarId=calendar_id,
        timeMin=start_iso,
        timeMax=end_iso,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get("items", [])

def cancel_events(event_ids: List[str], calendar_id: str = "primary"):
    # Initialize via OAuth
    calendar_service, _ = get_google_services()
    results = []
    for eid in event_ids:
        try:
            calendar_service.events().delete(calendarId=calendar_id, eventId=eid).execute()
            results.append({"event_id": eid, "status": "deleted"})
        except Exception as e:
            results.append({"event_id": eid, "status": f"error: {str(e)}"})
    return results

def create_event(title: str, start_iso: str, end_iso: str, attendees: List[str] = None, calendar_id: str = "primary", recurrence: str = None):
    # Initialize via OAuth
    calendar_service, _ = get_google_services()
    if attendees is None:
        attendees = []
    event_body = {
        "summary": title,
        "start": {"dateTime": start_iso, "timeZone": TIMEZONE},
        "end": {"dateTime": end_iso, "timeZone": TIMEZONE},
    }

    # Add attendees if any
    if attendees:
        event_body["attendees"] = [{"email": a} for a in attendees]
    
    # Add Google Meet link
    event_body["conferenceData"] = {
        "createRequest": {"requestId": f"meet-{int(datetime.utcnow().timestamp())}"}
    }

    # Add recurrence if provided
    if recurrence:
        event_body["recurrence"] = [recurrence]   # e.g., "RRULE:FREQ=WEEKLY;BYDAY=MO"

    created = calendar_service.events().insert(
        calendarId=calendar_id,
        body=event_body,
        conferenceDataVersion=1
    ).execute()

    return {
        "event_id": created.get("id"),
        "htmlLink": created.get("htmlLink"),
        "meet_link": created.get("hangoutLink")
            or (created.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri")
                if created.get("conferenceData") else None),
        "raw": created
    }

