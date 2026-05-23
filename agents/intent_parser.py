# agents/intent_parser.py
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
import json

groq = Groq(api_key=GROQ_API_KEY)

INTENT_SYSTEM = """You are an intent parser for Kyra AI assistant.
Your job is to understand user commands and return a JSON object.

ONLY return raw JSON — no explanation, no markdown, no code blocks.

Possible actions and their JSON format:

1. Set calendar event:
{"action": "set_calendar", "title": "event name", "start": "YYYY-MM-DDTHH:MM:00", "end": "YYYY-MM-DDTHH:MM:00", "description": ""}

2. Post a tweet:
{"action": "post_tweet", "text": "tweet content"}

3. Get summary (all):
{"action": "get_summary", "type": "all"}

4. Get news:
{"action": "get_summary", "type": "news"}

5. Get calendar:
{"action": "get_summary", "type": "calendar"}

6. Get emails:
{"action": "get_summary", "type": "email"}

7. Get a fact:
{"action": "get_fact", "category": "AI"}
category can be: AI, Politics, Science, Space, History, Tech, Psychology

8. Anything else — casual chat, hi, hello, feelings, questions:
{"action": "chat", "reply": ""}

Today's date context will help you parse relative times like "tomorrow", "tonight", "next Monday".
"""

def parse_intent(command: str) -> dict:
    try:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d %A")

        resp = groq.chat.completions.create(
            model    = GROQ_MODEL,
            messages = [
                {"role": "system", "content": INTENT_SYSTEM},
                {"role": "user",   "content": f"Today is {today}.\nCommand: {command}"}
            ],
            max_tokens  = 200,
            temperature = 0.1,
        )

        raw = resp.choices[0].message.content.strip()

        # Strip markdown if Groq wraps in ```json
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        intent = json.loads(raw)
        print(f"[Kyra] Intent parsed: {intent}")
        return intent

    except json.JSONDecodeError:
        print(f"[Kyra] Intent parse failed — raw: {raw}")
        return {"action": "chat", "reply": ""}
    except Exception as e:
        print(f"[Kyra] Intent parser error: {e}")
        return {"action": "chat", "reply": ""}