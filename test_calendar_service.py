# test_google_calendar.py
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_service_account_file(
    "./credentials.json",
    scopes=["https://www.googleapis.com/auth/calendar"]
)
service = build("calendar", "v3", credentials=creds, cache_discovery=False)

# List next 5 events from your calendar
events_result = service.events().list(
    calendarId="primary", maxResults=5, singleEvents=True, orderBy="startTime"
).execute()
events = events_result.get("items", [])

print("✅ Connection OK. Upcoming events:")
for e in events:
    print(e["summary"], "→", e["start"].get("dateTime", e["start"].get("date")))
