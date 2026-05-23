require("dotenv").config({ path: "../.env" });
const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode  = require("qrcode-terminal");
const express = require("express");
const axios   = require("axios");

const PYTHON_WEBHOOK = process.env.PYTHON_WEBHOOK || "http://localhost:8000/webhook/message";
const MY_NUMBER      = process.env.YOUR_PHONE_NUMBER;   // e.g. 91XXXXXXXXXX
const BOT_PORT       = 3000;

// ── WhatsApp client setup ────────────────────────────────────────────────────
const client = new Client({
  authStrategy: new LocalAuth({ dataPath: ".wwebjs_auth" }),
  puppeteer: {
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
    ],
  },
});

// Show QR code in terminal on first run
client.on("qr", (qr) => {
  console.log("[Kyra] Scan this QR code with your WhatsApp:");
  qrcode.generate(qr, { small: true });
});

client.on("ready", () => {
  console.log("[Kyra] WhatsApp bot is ready ✅");
});

client.on("auth_failure", (msg) => {
  console.error("[Kyra] Auth failed:", msg);
});

// ── Incoming messages → forward to Python ────────────────────────────────────
client.on("message", async (msg) => {
  try {
    const chat   = await msg.getChat();
    const contact = await msg.getContact();

    const payload = {
      from:        msg.from.replace("@c.us", "").replace("@g.us", ""),
      sender_name: contact.pushname || contact.number,
      chat_name:   chat.name || chat.id.user,
      body:        msg.body,
      timestamp:   msg.timestamp,
      is_group:    chat.isGroup,
    };

    console.log(`[Kyra] Message from ${payload.sender_name}: ${payload.body.substring(0, 60)}`);

    // Forward to FastAPI
    await axios.post(PYTHON_WEBHOOK, payload, { timeout: 10000 });
  } catch (err) {
    console.error("[Kyra] Error forwarding message:", err.message);
  }
});

client.initialize();

// ── Express server — receives send commands from Python ──────────────────────
const app = express();
app.use(express.json());

/**
 * POST /send
 * Body: { "to": "91XXXXXXXXXX", "message": "Hello from Kyra!" }
 */
app.post("/send", async (req, res) => {
  const { to, message } = req.body;
  if (!to || !message) {
    return res.status(400).json({ error: "Missing 'to' or 'message'" });
  }
  try {
    const chatId = `${to}@c.us`;
    await client.sendMessage(chatId, message);
    console.log(`[Kyra] Sent message to ${to}`);
    res.json({ success: true });
  } catch (err) {
    console.error("[Kyra] Send error:", err.message);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /status
 */
app.get("/status", (req, res) => {
  res.json({ status: "running", connected: client.info ? true : false });
});

app.listen(BOT_PORT, () => {
  console.log(`[Kyra] WhatsApp bot HTTP server running on port ${BOT_PORT}`);
});
