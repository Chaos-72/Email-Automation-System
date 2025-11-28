"""
Run this script once to authenticate your Gmail & Calendar access.

Usage:
    python backend/google_auth_flow.py

It will open a browser window — log in using your sender Gmail account
(e.g., bhagatravi4contact@gmail.com). After approval, it creates `token.json`
that will be reused by your backend (no need to re-login every time).
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import json
import os

# ✅ Scopes for Gmail + Calendar
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

def main():
    creds = None

    # Your OAuth client secrets file downloaded from Google Cloud Console
    client_secret_file = os.path.join(os.path.dirname(__file__), "credentials.json")

    if not os.path.exists(client_secret_file):
        raise FileNotFoundError(
            f"❌ Missing {client_secret_file}. "
            "Download it from Google Cloud Console > Credentials > OAuth 2.0 Client IDs."
        )

    print("🔑 Starting Google OAuth flow...")
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save token for backend reuse
    token_path = os.path.join(os.path.dirname(__file__), "token.json")
    with open(token_path, "wb") as token_file:
        pickle.dump(creds, token_file)

    print(f"✅ Authentication successful! Token saved at: {token_path}")
    print("Now restart your FastAPI server — Gmail & Calendar should work.")

if __name__ == "__main__":
    main()
