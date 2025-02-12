import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
from database import init_db, save_quiz, get_quiz, save_response
from utils import translate, rate_limit

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Start command
@rate_limit(5)  # Allow 5 requests per user
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    logger.info(f"User {user_id} started the bot.")
    welcome_message = translate("welcome", "en")  # Default to English
    await update.message.reply_text(welcome_message)

# Create quiz command
async def create_quiz(update: Update, context: CallbackContext):
    await update.message.reply_text("Let's create a new quiz. First, send me the title of your quiz.")
    context.user_data["step"] = "title"

# Handle quiz creation steps
async def handle_message(update: Update, context: CallbackContext):
    step = context.user_data.get("step")
    user_id = update.message.from_user.id

    if step == "title":
        context.user_data["title"] = update.message.text
        await update.message.reply_text("Great! Now send me a description of your quiz (or /skip to skip this step).")
        context.user_data["step"] = "description"

    elif step == "description":
        if update.message.text.lower() != "/skip":
            context.user_data["description"] = update.message.text
        await update.message.reply_text("Now send me your first question (e.g., 'What is CPU?').")
        context.user_data["step"] = "question"

    elif step == "question":
        question = update.message.text
        quiz_id = save_quiz(context.user_data["title"], context.user_data.get("description"), question)
        await update.message.reply_text(f"Question added! Use /add to add more questions or /finish to complete the quiz.")
        context.user_data["step"] = "add_questions"

    elif step == "add_questions":
        if update.message.text.lower() == "/finish":
            await update.message.reply_text(f"Quiz created successfully! Use /share_{quiz_id} to share it.")
            context.user_data.clear()
        else:
            save_quiz(context.user_data["title"], context.user_data.get("description"), update.message.text)
            await update.message.reply_text(f"Question added! Use /add to add more questions or /finish to complete the quiz.")

# Share quiz command
async def share_quiz(update: Update, context: CallbackContext):
    quiz_id = context.args[0]
    quiz_link = f"https://t.me/your_bot_username?start=quiz_{quiz_id}"
    await update.message.reply_text(f"Share this link to invite others to take the quiz: {quiz_link}")

# Handle quiz responses
async def handle_quiz_response(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    quiz_id = context.user_data.get("quiz_id")
    user_answer = update.message.text
    correct_answer = get_quiz(quiz_id)["answer"]

    if user_answer.lower() == correct_answer.lower():
        save_response(user_id, quiz_id, True)
        await update.message.reply_text("Correct!")
    else:
        save_response(user_id, quiz_id, False)
        await update.message.reply_text(f"Incorrect! The correct answer is {correct_answer}.")

# Main function
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables.")

    app = ApplicationBuilder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create_quiz))
    app.add_handler(CommandHandler("share", share_quiz))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_quiz_response))

    app.run_polling()

if __name__ == "__main__":
    main()
