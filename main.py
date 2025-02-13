import os
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your Koyeb app URL

if not TOKEN or not WEBHOOK_URL:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or WEBHOOK_URL environment variable.")

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for webhook handling
app = Flask(__name__)

# Quiz data storage (in-memory for simplicity)
quizzes = {}

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to Quiz Bot! Use /create to start a quiz.")

async def create_quiz(update: Update, context: CallbackContext):
    await update.message.reply_text("Let's create a new quiz. Send me the title.")
    context.user_data["step"] = "title"

async def handle_message(update: Update, context: CallbackContext):
    step = context.user_data.get("step")
    user_id = update.message.from_user.id
    
    if step == "title":
        context.user_data["title"] = update.message.text
        await update.message.reply_text("Now send me a description.")
        context.user_data["step"] = "description"
    elif step == "description":
        context.user_data["description"] = update.message.text
        await update.message.reply_text("Now send your first question.")
        context.user_data["step"] = "question"
    elif step == "question":
        quiz_id = str(len(quizzes) + 1)
        quizzes[quiz_id] = {
            "title": context.user_data["title"],
            "description": context.user_data["description"],
            "questions": [update.message.text],
            "creator": user_id,
        }
        await update.message.reply_text("Question added! Use /add to add more questions or /finish to complete.")
        context.user_data["step"] = "add_questions"
        context.user_data["quiz_id"] = quiz_id

async def handle_button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("start_"):
        quiz_id = data.split("_")[1]
        await query.edit_message_text(f"Starting quiz: {quizzes[quiz_id]['title']}\nFirst question: {quizzes[quiz_id]['questions'][0]}")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot_app.bot)
    bot_app.update_queue.put(update)
    return "OK", 200

bot_app = ApplicationBuilder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("create", create_quiz))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
bot_app.add_handler(CallbackQueryHandler(handle_button_click))

def main():
    bot_app.bot.setWebhook(f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
        del quizzes[quiz_id]
        await query.edit_message_text("Quiz deleted successfully!")
    else:
        await query.edit_message_text("Quiz not found.")

# Main function
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables.")

    app = ApplicationBuilder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create_quiz))
    app.add_handler(CommandHandler("finish", handle_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_button_click))

    app.run_polling()

if __name__ == "__main__":
    main()
