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
reflection = st.sidebar.text_area("Reflection", placeholder="What did you notice about yourself, your mood, or your experience?")

if st.sidebar.button("Log Reading Session"):
    st.session_state.reading_log.append({
        "Date": date,
        "Book": book_title,
        "Duration (min)": duration,
        "Reflection": reflection
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

# Reading Duration Statistics & Vizualization
st.subheader("📊 Reading Over Time")
if st.session_state.reading_log:
    df = pd.DataFrame(st.session_state.reading_log)

    # Ensure date is sorted
    df = df.sort_values("Date")

    # Calculate statistics
    avg_duration_per_session = df["Duration (min)"].mean()
    avg_duration_per_day = df.groupby("Date")["Duration (min)"].sum().mean()

    st.write(f"📘 **Average Duration per Session:** {avg_duration_per_session:.2f} minutes")
    st.write(f"📆 **Average Duration per Day:** {avg_duration_per_day:.2f} minutes")

    # Visualization of reading duration over time
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Duration (min)"], label="Reading Duration", marker='o', linestyle='-', color='b')
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
