import os
import logging
from flask import Flask, request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get bot token and admin chat ID from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Your bot's token from @BotFather
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # Your Telegram User ID

# Flask app for webhook
app = Flask(__name__)

# Telegram Bot Handlers
async def start(update: Update, context: CallbackContext) -> None:
    """Handles the /start command and sends the menu."""
    chat_id = update.message.chat_id

    keyboard = [
        [KeyboardButton("填写信息", web_app=WebAppInfo(url="https://hourtmeiching.github.io/Testbot/form.html"))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("欢迎！请点击下方按钮填写您的信息。", reply_markup=reply_markup)

# Handle incoming form submission data
@app.route("/submit", methods=["POST"])
def receive_form_data():
    """Receives form data from the web app and sends it to Telegram."""
    data = request.json
    name = data.get("name", "N/A")
    email = data.get("email", "N/A")
    telegram_username = data.get("username", "N/A")
    telegram_first_name = data.get("first_name", "N/A")
    telegram_id = data.get("user_id", "N/A")

    message = f"📩 **新表单提交**\n\n"
    message += f"👤 **姓名**: {name}\n"
    message += f"📧 **电子邮件**: {email}\n\n"
    message += f"🆔 **Telegram 用户信息**\n"
    message += f"🔹 **用户名**: {telegram_username}\n"
    message += f"🔹 **名字**: {telegram_first_name}\n"
    message += f"🔹 **用户 ID**: {telegram_id}"

    # Send message to admin's Telegram account
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
        "chat_id": ADMIN_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    })

    return {"status": "success"}

# Set up Telegram bot application
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Webhook setup
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Handles Telegram webhook updates."""
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return "OK", 200

# Run Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
