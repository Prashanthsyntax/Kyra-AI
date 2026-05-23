# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from db import init_db
from scheduler import start_scheduler, stop_scheduler
from agents.intent_parser import parse_intent
from agents.summariser import send_whatsapp_message, run_digest
from agents.calendar_agent import create_event, get_upcoming_events
from agents.kyra_persona import is_emotional, kyra_respond
from connectors.twitter_connector import post_tweet
from connectors.news_connector import get_top_news
from connectors.telegram_connector import build_app
import uvicorn, threading

telegram_app = None


async def handle_command(command: str, user_id: str = "default"):
    """
    Central router for all incoming messages.
    - No 'Kyra' prefix  → Kyra persona (emotional / casual)
    - 'Kyra' prefix     → intent parser → task execution
    """
    print(f"[Kyra] Incoming: {command}")
    stripped = command.strip().lower()

    # ── Persona route (hi, hello, feelings, casual chat) ──────
    if not stripped.startswith("kyra"):
        reply = kyra_respond(user_id, command)
        await send_whatsapp_message(reply)
        return

    # ── Command route ──────────────────────────────────────────
    intent = parse_intent(command)
    action = intent.get("action")

    if action == "set_calendar":
        result = create_event(
            title       = intent.get("title", "Event"),
            start       = intent.get("start"),
            end         = intent.get("end"),
            description = intent.get("description", ""),
        )
        await send_whatsapp_message(result["reply"])

    elif action == "post_tweet":
        result = post_tweet(intent.get("text", ""))
        msg = "Tweet posted! 🐦" if result["success"] else f"Tweet failed: {result.get('error')}"
        await send_whatsapp_message(msg)

    elif action == "get_summary":
        stype = intent.get("type", "all")
        if stype == "news":
            await send_whatsapp_message("📰 Top news:\n" + get_top_news())
        elif stype == "calendar":
            await send_whatsapp_message("📅 Upcoming:\n" + get_upcoming_events())
        elif stype == "email":
            from agents.summariser import _format_emails
            await send_whatsapp_message("✉ Emails:\n" + _format_emails())
        else:
            await run_digest()

    elif action == "get_fact":
        from agents.facts_agent import generate_fact
        category = intent.get("category", "Science")
        fact = generate_fact(category)
        msg = f"🧠 *{fact['category']}*\n{fact['fact']}\n\n↳ {fact.get('why', '')}"
        await send_whatsapp_message(msg)

    elif action == "chat":
        # Intent parser said chat — let Kyra persona handle it
        reply = kyra_respond(user_id, command)
        await send_whatsapp_message(reply)

    else:
        await send_whatsapp_message(
            "Try:\n"
            "• Kyra what's the news\n"
            "• Kyra set my calendar 10 AM to 11 AM meeting\n"
            "• Kyra post a tweet: hello world\n"
            "• Kyra give me a fact about space"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    init_db()
    start_scheduler()

    telegram_app = build_app(handle_command)
    t = threading.Thread(
        target=lambda: telegram_app.run_polling(close_loop=False),
        daemon=True
    )
    t.start()

    print("[Kyra] 🤖 Kyra is online!")
    yield
    stop_scheduler()


app = FastAPI(title="Kyra AI Agent", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "Kyra is running 🤖"}


@app.get("/trigger-digest")
async def trigger_digest():
    await run_digest()
    return {"status": "Digest sent"}


@app.post("/message")
async def handle_message(request: Request):
    body    = await request.json()
    text    = body.get("message", "").strip()
    user_id = body.get("user_id", "default")

    if not text:
        return JSONResponse({"reply": "Empty message."}, status_code=400)

    await handle_command(text, user_id)
    return {"reply": "OK"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)