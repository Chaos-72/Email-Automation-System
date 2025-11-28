# test_oauth_calendar.py
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle, os

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send"
]

def get_creds():
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            return pickle.load(token)
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=0)
    with open("token.pkl", "wb") as token:
        pickle.dump(creds, token)
    return creds

creds = get_creds()
calendar_service = build("calendar", "v3", credentials=creds)
gmail_service = build("gmail", "v1", credentials=creds)

# ✅ Test: create event
event = {
    "summary": "Test Meeting via OAuth",
    "start": {"dateTime": "2025-10-13T10:00:00+05:30"},
    "end": {"dateTime": "2025-10-13T11:00:00+05:30"},
    "attendees": [{"email": "bhagatraviatgdsc@gmail.com"}],
    "conferenceData": {"createRequest": {"requestId": "oauth-demo-123"}}
}

created = calendar_service.events().insert(
    calendarId="primary", body=event, conferenceDataVersion=1
).execute()

print("✅ Event created:", created["htmlLink"])
