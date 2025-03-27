import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Initialize session state
if 'reading_log' not in st.session_state:
    st.session_state.reading_log = []
if 'mood_log' not in st.session_state:
    st.session_state.mood_log = []

# Title
st.title("📚 Digital Detox Reading Tracker")

# Sidebar for input
st.sidebar.header("Log Your Reading Session")
book_title = st.sidebar.text_input("Book Title")
duration = st.sidebar.number_input("Time Spent Reading (minutes)", min_value=1, step=1)
date = st.sidebar.date_input("Date", datetime.date.today())
mood = st.sidebar.slider("Mood After Reading (1-10)", 1, 10, 5)
focus = st.sidebar.slider("Focus Level (1-10)", 1, 10, 5)
productivity = st.sidebar.slider("Productivity Level (1-10)", 1, 10, 5)

if st.sidebar.button("Log Reading Session"):
    st.session_state.reading_log.append({
        "Date": date,
        "Book": book_title,
        "Duration (min)": duration
    })
    st.session_state.mood_log.append({
        "Date": date,
        "Mood": mood,
        "Focus": focus,
        "Productivity": productivity
    })
    st.success("Reading session logged successfully!")

# Display reading log
st.subheader("📖 Your Reading Log")
if st.session_state.reading_log:
    df = pd.DataFrame(st.session_state.reading_log)
    st.dataframe(df)
else:
    st.write("No reading sessions logged yet.")

# Streak Tracking
st.subheader("⏳ Streaks")
if st.session_state.reading_log:
    dates = sorted([entry['Date'] for entry in st.session_state.reading_log])
    streak = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            streak += 1
        else:
            streak = 1
    st.write(f"🔥 Current Streak: {streak} days")
else:
    st.write("Start reading to build your streak!")

# Visualization of mood, focus, productivity
st.subheader("📈 Mood, Focus & Productivity Over Time")
if st.session_state.mood_log:
    df_mood = pd.DataFrame(st.session_state.mood_log)
    df_mood = df_mood.sort_values("Date")
    fig, ax = plt.subplots()
    ax.plot(df_mood["Date"], df_mood["Mood"], label="Mood", marker='o')
    ax.plot(df_mood["Date"], df_mood["Focus"], label="Focus", marker='s')
    ax.plot(df_mood["Date"], df_mood["Productivity"], label="Productivity", marker='^')
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.write("No mood, focus, or productivity data yet.")
