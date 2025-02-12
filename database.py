import sqlite3

# Initialize database
def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            question TEXT,
            answer TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            user_id INTEGER,
            quiz_id INTEGER,
            is_correct INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Save quiz to database
def save_quiz(title, description, question):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO quizzes (title, description, question) VALUES (?, ?, ?)", (title, description, question))
    quiz_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return quiz_id

# Get quiz from database
def get_quiz(quiz_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
    quiz = cursor.fetchone()
    conn.close()
    return quiz

# Save user response
def save_response(user_id, quiz_id, is_correct):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO responses (user_id, quiz_id, is_correct) VALUES (?, ?, ?)", (user_id, quiz_id, is_correct))
    conn.commit()
    conn.close()
