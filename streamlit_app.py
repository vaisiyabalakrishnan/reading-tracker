import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize session state if not exists
if 'reading_log' not in st.session_state:
    st.session_state.reading_log = []

st.title("📖 Digital Detox Reading Tracker")

# Sidebar for logging reading sessions
st.sidebar.header("Log a Reading Session")
book_title = st.sidebar.text_input("Book Title")
time_spent = st.sidebar.number_input("Minutes Spent Reading", min_value=1)
reflection = st.sidebar.text_area("Reflection on Today's Reading")
log_button = st.sidebar.button("Log Reading Session")

if log_button and book_title:
    st.session_state.reading_log.append({
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Book": book_title,
        "Time (mins)": time_spent,
        "Reflection": reflection
    })
    st.sidebar.success("Reading session logged successfully!")

# Display the reading log
st.subheader("📚 Your Reading Log")
if st.session_state.reading_log:
    df = pd.DataFrame(st.session_state.reading_log)
    st.dataframe(df)
else:
    st.info("No reading sessions logged yet.")

# Progress Chart
st.subheader("📊 Reading Progress")
if st.session_state.reading_log:
    df["Date"] = pd.to_datetime(df["Date"])
    df_sorted = df.sort_values(by="Date")
    fig, ax = plt.subplots()
    ax.plot(df_sorted["Date"], df_sorted["Time (mins)"], marker='o', linestyle='-')
    ax.set_xlabel("Date")
    ax.set_ylabel("Minutes Spent Reading")
    ax.set_title("Reading Time Over Time")
    st.pyplot(fig)
else:
    st.info("Start logging sessions to see your progress!")
