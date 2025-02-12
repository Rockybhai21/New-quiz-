import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Quiz data storage (in-memory for simplicity)
quizzes = {}

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to Quiz Bot! Use /create to start creating a quiz.")

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
        quiz_id = str(len(quizzes) + 1)  # Generate a unique quiz ID
        quizzes[quiz_id] = {
            "title": context.user_data["title"],
            "description": context.user_data.get("description", ""),
            "questions": [question],
            "creator": user_id,
        }
        await update.message.reply_text(f"Question added! Use /add to add more questions or /finish to complete the quiz.")
        context.user_data["step"] = "add_questions"
        context.user_data["quiz_id"] = quiz_id

    elif step == "add_questions":
        if update.message.text.lower() == "/finish":
            quiz_id = context.user_data["quiz_id"]
            await show_quiz_menu(update, context, quiz_id)
            context.user_data.clear()
        else:
            quizzes[context.user_data["quiz_id"]]["questions"].append(update.message.text)
            await update.message.reply_text(f"Question added! Use /add to add more questions or /finish to complete the quiz.")

# Show quiz menu
async def show_quiz_menu(update: Update, context: CallbackContext, quiz_id):
    quiz = quizzes[quiz_id]
    keyboard = [
        [InlineKeyboardButton("Start Quiz", callback_data=f"start_{quiz_id}")],
        [InlineKeyboardButton("Share Quiz", callback_data=f"share_{quiz_id}")],
        [InlineKeyboardButton("Delete Quiz", callback_data=f"delete_{quiz_id}")],
        [InlineKeyboardButton("Close", callback_data="close")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Quiz created successfully!\nTitle: {quiz['title']}\nDescription: {quiz.get('description', 'No description')}\nQuestions: {len(quiz['questions'])}",
        reply_markup=reply_markup,
    )

# Handle button clicks
async def handle_button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("start_"):
        quiz_id = data.split("_")[1]
        await start_quiz(query, context, quiz_id)
    elif data.startswith("share_"):
        quiz_id = data.split("_")[1]
        await share_quiz(query, context, quiz_id)
    elif data.startswith("delete_"):
        quiz_id = data.split("_")[1]
        await delete_quiz(query, context, quiz_id)
    elif data == "close":
        await query.edit_message_text("Menu closed.")

# Start quiz
async def start_quiz(query, context: CallbackContext, quiz_id):
    quiz = quizzes[quiz_id]
    await query.edit_message_text(f"Starting quiz: {quiz['title']}\nFirst question: {quiz['questions'][0]}")

# Share quiz
async def share_quiz(query, context: CallbackContext, quiz_id):
    quiz_link = f"https://t.me/your_bot_username?start=quiz_{quiz_id}"
    await query.edit_message_text(f"Share this link to invite others to take the quiz: {quiz_link}")

# Delete quiz
async def delete_quiz(query, context: CallbackContext, quiz_id):
    if quiz_id in quizzes:
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
