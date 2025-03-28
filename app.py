import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import sqlite3
import hashlib
import os

# Database setup
def init_db():
    conn = sqlite3.connect('reading_tracker.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS reading_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  date DATE,
                  book TEXT,
                  duration INTEGER,
                  reflection TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS mood_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  date DATE,
                  mood INTEGER,
                  focus INTEGER,
                  productivity INTEGER,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

# Password hashing
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# Initialize database
init_db()

# Authentication functions
def create_user(username, password):
    conn = sqlite3.connect('reading_tracker.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password) VALUES (?,?)', 
              (username, make_hashes(password)))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('reading_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    data = c.fetchone()
    conn.close()
    
    if data and check_hashes(password, data[2]):
        return data[0]  # Return user_id
    return None

# Get user data
def get_user_logs(user_id):
    conn = sqlite3.connect('reading_tracker.db')
    
    reading_logs = pd.read_sql(
        'SELECT date, book, duration, reflection FROM reading_logs WHERE user_id = ? ORDER BY date', 
        conn, params=(user_id,))
    
    mood_logs = pd.read_sql(
        'SELECT date, mood, focus, productivity FROM mood_logs WHERE user_id = ? ORDER BY date', 
        conn, params=(user_id,))
    
    conn.close()
    return reading_logs, mood_logs

# Main app
def main():
    st.title("📚 Vaisiya's Reading Tracker!")

    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'reading_log' not in st.session_state:
        st.session_state.reading_log = []
    if 'mood_log' not in st.session_state:
        st.session_state.mood_log = []

    # Login/Signup
    if not st.session_state.user_id:
        menu = ["Login", "SignUp"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
            st.sidebar.subheader("Login Section")
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type='password')
            
            if st.sidebar.button("Login"):
                user_id = login_user(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.reading_log, st.session_state.mood_log = get_user_logs(user_id)
                    st.sidebar.success("Logged In as {}".format(username))
                else:
                    st.sidebar.error("Incorrect Username/Password")

        elif choice == "SignUp":
            st.sidebar.subheader("Create New Account")
            new_user = st.sidebar.text_input("Username")
            new_password = st.sidebar.text_input("Password", type='password')
            
            if st.sidebar.button("Signup"):
                if new_user and new_password:
                    try:
                        create_user(new_user, new_password)
                        st.sidebar.success("Account created! Please login.")
                    except sqlite3.IntegrityError:
                        st.sidebar.error("Username already exists")
                else:
                    st.sidebar.warning("Please enter both username and password")

        return  # Stop execution if not logged in

    # Logged in section
    st.sidebar.header(f"Welcome back! 👋")
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.reading_log = []
        st.session_state.mood_log = []
        st.experimental_rerun()

    # Log reading session
    st.sidebar.header("Log Reading Session")
    book_title = st.sidebar.text_input("Book Title")
    duration = st.sidebar.number_input("Time Spent Reading (minutes)", min_value=1, step=1)
    date = st.sidebar.date_input("Date", datetime.date.today())
    mood = st.sidebar.slider("Mood After Reading (1-10)", 1, 10, 5)
    focus = st.sidebar.slider("Focus Level (1-10)", 1, 10, 5)
    productivity = st.sidebar.slider("Productivity Level (1-10)", 1, 10, 5)
    reflection = st.sidebar.text_area("Reflection", placeholder="What did you notice about yourself, your mood, or your experience?")

    if st.sidebar.button("Log Reading Session"):
        conn = sqlite3.connect('reading_tracker.db')
        c = conn.cursor()
        
        # Insert reading log
        c.execute('INSERT INTO reading_logs (user_id, date, book, duration, reflection) VALUES (?,?,?,?,?)',
                 (st.session_state.user_id, date, book_title, duration, reflection))
        
        # Insert mood log
        c.execute('INSERT INTO mood_logs (user_id, date, mood, focus, productivity) VALUES (?,?,?,?,?)',
                 (st.session_state.user_id, date, mood, focus, productivity))
        
        conn.commit()
        conn.close()
        
        # Update session state
        st.session_state.reading_log, st.session_state.mood_log = get_user_logs(st.session_state.user_id)
        st.success("Reading session logged successfully!")

    # Display reading log
    st.subheader("📖 Your Reading Log")
    if not st.session_state.reading_log.empty:
        st.dataframe(st.session_state.reading_log)
    else:
        st.write("No reading sessions logged yet.")

    # Streak Tracking
    st.subheader("⏳ Streaks")
    if not st.session_state.reading_log.empty:
        dates = pd.to_datetime(st.session_state.reading_log['date']).sort_values()
        streak = 1
        for i in range(1, len(dates)):
            if (dates.iloc[i] - dates.iloc[i-1]).days == 1:
                streak += 1
            else:
                streak = 1
        st.write(f"🔥 Current Streak: {streak} days")
    else:
        st.write("Start reading to build your streak!")

    # Reading Duration Statistics & Visualization
    st.subheader("📊 Reading Over Time")
    if not st.session_state.reading_log.empty:
        df = st.session_state.reading_log.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Calculate statistics
        avg_duration_per_session = df["duration"].mean()

        st.write(f"📘 **Average Duration per Session:** {avg_duration_per_session:.2f} minutes")

        # Visualization of reading duration over time
        fig, ax = plt.subplots()
        ax.plot(df["date"], df["duration"], label="Reading Duration", marker='o', linestyle='-', color='b')
        ax.set_xlabel("Date")
        ax.set_ylabel("Minutes Spent Reading")
        ax.set_title("Reading Duration Over Time")
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.write("No reading data yet.")

    # Visualization of mood, focus, productivity
    st.subheader("📈 Mood, Focus & Productivity Over Time")
    if not st.session_state.mood_log.empty:
        df_mood = st.session_state.mood_log.copy()
        df_mood['date'] = pd.to_datetime(df_mood['date'])
        df_mood = df_mood.sort_values('date')
        
        fig, ax = plt.subplots()
        ax.plot(df_mood["date"], df_mood["mood"], label="Mood", marker='o')
        ax.plot(df_mood["date"], df_mood["focus"], label="Focus", marker='s')
        ax.plot(df_mood["date"], df_mood["productivity"], label="Productivity", marker='^')
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.write("No mood, focus, or productivity data yet.")

if __name__ == '__main__':
    main()