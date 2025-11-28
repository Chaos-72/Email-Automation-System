# # backend/google_utils.py
# # ✅ NEW FILE
# import os, pickle
# from googleapiclient.discovery import build
# from google.auth.transport.requests import Request

# # Scopes for Gmail + Calendar
# SCOPES = [
#     "https://www.googleapis.com/auth/calendar",
#     "https://www.googleapis.com/auth/gmail.send"
# ]

# def get_google_services():
#     """
#     Load OAuth token and return Gmail + Calendar API clients.
#     Make sure token.pkl exists (run test_oauth_calendar.py once).
#     """
#     creds = None
#     if os.path.exists("token.json"):
#         with open("token.json", "rb") as token:
#             creds = pickle.load(token)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#             with open("token.json", "wb") as token:
#                 pickle.dump(creds, token)
#         else:
#             raise Exception("⚠️ No valid OAuth token found. Run test_oauth_calendar.py first!")

#     calendar_service = build("calendar", "v3", credentials=creds, cache_discovery=False)
#     gmail_service = build("gmail", "v1", credentials=creds, cache_discovery=False)
#     return calendar_service, gmail_service


# =================
# backend/google_utils.py
# ✅ UPDATED: SIMPLIFIED FOR TOKEN.JSON 
# =================

# backend/google_utils.py

import os
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# ✅ Scopes for Gmail + Calendar
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
]

def get_token_path():
    """Ensure token.json path works no matter where app is run from."""
    return os.path.join(os.path.dirname(__file__), "token.json")

def get_google_services():
    """Return authenticated Calendar + Gmail API clients."""
    creds = None
    token_path = get_token_path()

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)
        else:
            raise Exception("⚠️ No valid OAuth token found. Run google_auth_flow.py first!")

    calendar_service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    gmail_service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    return calendar_service, gmail_service
