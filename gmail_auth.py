# gmail_auth.py  ← put this in your KyraAI root folder
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar"   # keep calendar scope too
]

def main():
    creds = None
    if os.path.exists("gmail_token.json"):
        creds = Credentials.from_authorized_user_file("gmail_token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("gmail_token.json", "w") as f:
            f.write(creds.to_json())
        print("✅ gmail_token.json created successfully!")
    else:
        print("✅ Token already valid.")

if __name__ == "__main__":
    main()