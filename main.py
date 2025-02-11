import os
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from openai import OpenAI  # Use Gemini AI when API is available
import requests

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
GEMINI_AI_KEY = os.getenv("GEMINI_AI_KEY")

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
    url = "https://api.pexels.com/v1/search?query=" + keyword
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers).json()
    return response["photos"][0]["src"]["large"] if response["photos"] else None

async def start(update: Update, context: CallbackContext):
    """Start command handler."""
    await update.message.reply_text("Welcome to the Quiz Maker Bot! Use /quiz <topic> to generate a quiz.")

async def quiz(update: Update, context: CallbackContext):
    """Generate a quiz based on user input."""
    if not context.args:
        await update.message.reply_text("Usage: /quiz <topic>")
        return
    topic = " ".join(context.args)
    questions = generate_quiz(topic)
    await update.message.reply_text(f"Here is your quiz on {topic}:")
    await update.message.reply_text(questions)

@app.route("/")
def home():
    return "Quiz Maker Bot is running!"

if __name__ == "__main__":
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("quiz", quiz))
    bot_app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    app.run(host="0.0.0.0", port=PORT)
