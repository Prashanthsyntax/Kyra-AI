# agents/email_agent.py
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
import os

groq = Groq(api_key=GROQ_API_KEY)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar"
]

def get_gmail_service():
    creds = Credentials.from_authorized_user_file("gmail_token.json", SCOPES)
    # Auto-refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


def classify_email(subject: str, snippet: str) -> str:
    """Returns 'urgent', 'fyi', or 'spam'."""
    try:
        resp = groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content":
                f"Classify this email as exactly one word: urgent, fyi, or spam.\n"
                f"Subject: {subject}\nSnippet: {snippet}"}],
            max_tokens=5
        )
        return resp.choices[0].message.content.strip().lower()
    except:
        return "fyi"   # safe default if Groq fails


def fetch_important_emails(max_results: int = 20) -> list[dict]:
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId="me", maxResults=max_results, q="is:unread"
        ).execute()
        messages = results.get("messages", [])

        important = []
        for msg in messages:
            full = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["Subject", "From"]
            ).execute()
            headers  = {h["name"]: h["value"] for h in full["payload"]["headers"]}
            subject  = headers.get("Subject", "(no subject)")
            sender   = headers.get("From", "Unknown")
            snippet  = full.get("snippet", "")

            label = classify_email(subject, snippet)
            if label in ("urgent", "fyi"):
                important.append({
                    "from":     sender,
                    "subject":  subject,
                    "snippet":  snippet,
                    "priority": label
                })
        return important

    except Exception as e:
        print(f"[Kyra] Email fetch failed: {e}")
        return []