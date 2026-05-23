# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from db import init_db, get_session, Message
from scheduler import start_scheduler, stop_scheduler
from agents.intent_parser import parse_intent
from agents.summariser import send_whatsapp_message, run_digest
from agents.calendar_agent import create_event, get_upcoming_events
from connectors.twitter_connector import post_tweet
from connectors.news_connector import get_top_news
from connectors.telegram_connector import build_app
from config import TELEGRAM_CHAT_ID
from agents.kyra_persona import is_emotional, kyra_respond
import uvicorn, asyncio, threading

telegram_app = None


async def handle_command(command: str):
    """Parse and execute a user command."""
    print(f"[Kyra] Command: {command}")
    intent = parse_intent(command)
    action = intent.get("action")

    if action == "set_calendar":
        result = create_event(
            title=intent.get("title", "Event"),
            start=intent.get("start"),
            end=intent.get("end"),
            description=intent.get("description", ""),
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
        else:
            await run_digest()

    elif action in ("chat", "unknown"):
        await send_whatsapp_message(intent.get("reply", ""))

    else:
        await send_whatsapp_message("Try: 'Kyra set my calendar 10 AM to 12 PM study'")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    init_db()
    start_scheduler()

    # Start Telegram bot in background thread
    telegram_app = build_app(handle_command)
    t = threading.Thread(
        target=lambda: telegram_app.run_polling(close_loop=False),
        daemon=True
    )
    t.start()

    print("[Kyra] 🤖 Kyra is online on Telegram!")
    yield
    stop_scheduler()


app = FastAPI(title="Kyra AI Agent", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "Kyra is running 🤖"}


@app.get("/trigger-digest")
async def trigger_digest():
    await run_digest()
    return {"status": "Digest sent to Telegram"}


@app.post("/message")
async def handle_message(request: Request):
    """
    Receives a message from Telegram or any HTTP client.
    Routes to emotional assistant or command handler.
    """
    body    = await request.json()
    text    = body.get("message", "").strip()
    user_id = body.get("user_id", "default")

    if not text:
        return JSONResponse({"reply": "Empty message received."}, status_code=400)

    # Emotional messages (no "Kyra" prefix) → persona handler
    if is_emotional(text) and not text.lower().startswith("kyra"):
        reply = kyra_respond(user_id, text)
        await send_whatsapp_message(reply)
        return {"reply": reply}

    # Everything else → command handler
    await handle_command(text)
    return {"reply": "Command processed."}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)