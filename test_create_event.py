from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from datetime import datetime, timezone
start_time = datetime.now(timezone.utc) + timedelta(minutes=10)
end_time = start_time + timedelta(hours=1)


creds = Credentials.from_service_account_file(
    "./credentials.json",
    scopes=["https://www.googleapis.com/auth/calendar"]
)
service = build("calendar", "v3", credentials=creds, cache_discovery=False)

# Create a test event 10 minutes from now
start_time = datetime.utcnow() + timedelta(minutes=10)
end_time = start_time + timedelta(hours=1)

event = {
    "summary": "Test Event",
    "start": {"dateTime": start_time.isoformat() + "Z"},
    "end": {"dateTime": end_time.isoformat() + "Z"},
    "attendees": [{"email": "your_email@gmail.com"}],
    "conferenceData": {"createRequest": {"requestId": "test123"}}
}

created = service.events().insert(
    calendarId="primary", body=event, conferenceDataVersion=1
).execute()

print("✅ Event created:", created.get("summary"), created.get("start")["dateTime"])
