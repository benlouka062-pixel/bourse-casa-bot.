import os
import logging
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# === CONFIGURATION ===
BOT_TOKEN = "8342446918:AAG4cuQKWZypIeAmfTy45PB0r7hQ8QFjhqo"
WEBHOOK_SECRET = "taoussi123"  # change si tu veux

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === INIT BOT ===
bot = Bot(token=BOT_TOKEN)
application = Application.builder().bot(bot).build()

# === FLASK APP ===
app = Flask(__name__)

# === COMMANDES ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Taoussi actif sur Railway !")

async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        symbol = context.args[0].upper()
        await update.message.reply_text(f"🖼️ Graphique pour {symbol} (à implémenter)")
    else:
        await update.message.reply_text("Usage: /graph IAM")

# === AJOUT DES HANDLERS ===
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("graph", graph))

# === WEBHOOK ENDPOINT ===
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Reçoit les updates de Telegram"""
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return "Unauthorized", 401
    
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return "OK", 200

@app.route("/")
def index():
    return "✅ Bot Taoussi is running on Railway!"

@app.route("/health")
def health():
    return "OK", 200

# === WEBHOOK SETUP (à exécuter UNE FOIS) ===
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    webhook_url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'ton-app')}/webhook/{BOT_TOKEN}"
    data = {"url": webhook_url, "secret_token": WEBHOOK_SECRET}
    import requests
    r = requests.post(url, json=data)
    logger.info(f"Webhook set: {r.json()}")

# === DÉMARRAGE ===
if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
