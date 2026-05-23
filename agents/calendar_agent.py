import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from db import get_session, CalendarLog
from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, GOOGLE_CALENDAR_ID

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _get_service():
    creds = None
    if os.path.exists(GOOGLE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(GOOGLE_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def create_event(title: str, start: str, end: str, description: str = "") -> dict:
    """
    Create a Google Calendar event.
    start / end must be ISO format: '2025-06-01T10:00:00'
    """
    try:
        service = _get_service()
        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start, "timeZone": "Asia/Kolkata"},
            "end":   {"dateTime": end,   "timeZone": "Asia/Kolkata"},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup",  "minutes": 10},
                    {"method": "email",  "minutes": 30},
                ],
            },
        }
        result = service.events().insert(
            calendarId=GOOGLE_CALENDAR_ID, body=event
        ).execute()

        event_id = result.get("id")

        # Log to DB
        session = get_session()
        session.add(CalendarLog(
            title=title, start_time=start,
            end_time=end, event_id=event_id
        ))
        session.commit()
        session.close()

        return {
            "success": True,
            "event_id": event_id,
            "reply": f"Done! I've added '{title}' to your calendar from {start[11:16]} to {end[11:16]}. ✅",
        }
    except Exception as e:
        return {"success": False, "reply": f"Calendar error: {e}"}


def get_upcoming_events(max_results: int = 5) -> str:
    """Return the next N events as a formatted string."""
    try:
        from datetime import datetime, timezone
        service = _get_service()
        now = datetime.now(timezone.utc).isoformat()
        events_result = service.events().list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = events_result.get("items", [])
        if not events:
            return "No upcoming events."
        lines = []
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date"))
            lines.append(f"• {e['summary']} — {start}")
        return "\n".join(lines)
    except Exception as e:
        return f"Could not fetch events: {e}"
