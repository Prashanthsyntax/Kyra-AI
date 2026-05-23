import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
from datetime import datetime

groq = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = f"""
You are Kyra, a personal AI assistant. Today's date is {datetime.now().strftime('%Y-%m-%d')}.
The user will send you a message. Parse it and return ONLY a valid JSON object.

Choose ONE action from below and return that JSON:

1. Set a calendar event:
   {{"action": "set_calendar", "title": "...", "start": "YYYY-MM-DDTHH:MM:00", "end": "YYYY-MM-DDTHH:MM:00", "description": "..."}}

2. Post a tweet:
   {{"action": "post_tweet", "text": "..."}}

3. Get a specific summary:
   {{"action": "get_summary", "type": "whatsapp" | "news" | "twitter" | "all"}}

4. General chat / question:
   {{"action": "chat", "reply": "your response here"}}

5. Unknown command:
   {{"action": "unknown", "reply": "I didn't understand that. Can you rephrase?"}}

Return ONLY the JSON. No explanation, no markdown, no extra text.
""".strip()


def parse_intent(user_message: str) -> dict:
    """Send the user's message to Groq and get a structured action back."""
    try:
        response = groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            max_tokens=300,
            temperature=0.1,    # low temp = more deterministic JSON
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown fences if Groq adds them
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"action": "chat", "reply": "I had trouble understanding that. Please try again."}
    except Exception as e:
        return {"action": "chat", "reply": f"Error: {e}"}
