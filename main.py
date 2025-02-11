import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import requests
from openai import OpenAI

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = f"https://new-quiz-ubbm.onrender.com/{TOKEN}"  # Replace with your actual Render/Koyeb URL
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
GEMINI_AI_KEY = os.getenv("GEMINI_AI_KEY")
PORT = int(os.environ.get("PORT", 8080))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Telegram bot
bot_app = Application.builder().token(TOKEN).build()

def generate_quiz(prompt):
    """Generate AI-based multiple-choice questions using Gemini AI."""
    response = OpenAI(api_key=GEMINI_AI_KEY).completion.create(
        model="gemini-pro",
        prompt=f"Generate 5 multiple-choice questions on: {prompt}"
    )
    return response['choices'][0]['text']

def get_image(keyword):
    """Fetch an image from Pexels based on a keyword."""
    url = f"https://api.pexels.com/v1/search?query={keyword}"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers).json()
    return response["photos"][0]["src"]["large"] if response["photos"] else None

async def start(update: Update, context: CallbackContext):
    """Start command handler."""
    await update.message.reply_text("Welcome to the AI Quiz Maker Bot! Use /quiz <topic> to generate a quiz.")

async def quiz(update: Update, context: CallbackContext):
    """Generate a quiz based on user input."""
    if not context.args:
        await update.message.reply_text("Usage: /quiz <topic>")
        return
    topic = " ".join(context.args)
    questions = generate_quiz(topic)
    await update.message.reply_text(f"Here is your AI-generated quiz on {topic}:\n{questions}")

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    """Handle Telegram webhook updates."""
    update = Update.de_json(request.get_json(), bot_app.bot)
    bot_app.process_update(update)
    return "OK", 200

@app.route("/")
def home():
    return "Quiz Maker Bot is running!"

if __name__ == "__main__":
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("quiz", quiz))

    # Set webhook on startup
    bot_app.bot.set_webhook(WEBHOOK_URL)

    app.run(host="0.0.0.0", port=PORT)
