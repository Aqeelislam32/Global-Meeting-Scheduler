import os
import streamlit as st
import datetime
import pytz
import yaml

from huggingface_hub import InferenceClient
from streamlit_chat import message

from smolagents import CodeAgent, tool

from zoneinfo import available_timezones

# ---------------- UI STYLE ----------------
st.markdown(
    """
    <style>
        .stApp { background-color: #FFDAB9; }
        [data-testid="stSidebar"] { background-color: #DEB887 !important; }
        .stButton>button { background-color: #8B4513 !important; color: white !important; border-radius: 8px; }
        .stButton>button:hover { background-color: #5a2e1a !important; }
        .stTextArea textarea, .stTextInput input { background-color: #008000 !important; color: white !important; border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- TIMEZONES ----------------
country_timezones = {
    "Pakistan": pytz.country_timezones.get('PK', []),
    "India": pytz.country_timezones.get('IN', []),
    "USA": pytz.country_timezones.get('US', []),
    "UK": pytz.country_timezones.get('GB', []),
}

# ---------------- HF CLIENT ----------------
client = InferenceClient(
    model="Qwen/Qwen2.5-Coder-32B-Instruct"
)

# ---------------- TOOL ----------------
@tool
def get_current_time_in_timezone(timezone: str) -> str:
    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(tz).strftime("%I:%M %p")
        return f"The current time in {timezone} is {local_time}"
    except Exception as e:
        return str(e)

# ---------------- TIME CONVERTER ----------------
def convert_timezone(time_str, from_tz, to_tz):
    try:
        from_zone = pytz.timezone(from_tz)
        to_zone = pytz.timezone(to_tz)

        naive_time = datetime.datetime.strptime(time_str, "%I:%M %p")
        localized_time = from_zone.localize(naive_time)
        converted_time = localized_time.astimezone(to_zone)

        return converted_time.strftime("%I:%M %p")
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- AGENT (FIXED) ----------------
model = client  # IMPORTANT FIX

agent = CodeAgent(
    model=model,
    tools=[get_current_time_in_timezone],
    max_steps=6
)

# ---------------- STREAMLIT UI ----------------
st.sidebar.title("🔹 Scheduling Assistant")
option = st.sidebar.radio("Choose:", ("🌍 Timezone Converter", "📅 Schedule Meeting"))

# ---------------- TIMEZONE CONVERTER ----------------
if option == "🌍 Timezone Converter":
    st.title("🕒 Timezone Converter")

    time_input = st.text_input("Enter Time (HH:MM AM/PM)")
    from_timezone = st.selectbox("From Timezone", pytz.all_timezones)
    to_timezone = st.selectbox("To Timezone", pytz.all_timezones)

    if st.button("Convert Time"):
        if time_input:
            result = convert_timezone(time_input, from_timezone, to_timezone)
            st.success(result)
        else:
            st.error("Enter valid time")

# ---------------- MEETING SCHEDULER ----------------
elif option == "📅 Schedule Meeting":
    st.title("📅 Global Meeting Scheduler")

    meeting_date = st.date_input("Select Date")
    meeting_time = st.text_input("Meeting Time (HH:MM AM/PM)")
    user_timezone = st.selectbox("Your Timezone", pytz.all_timezones)
    attendee_timezone = st.selectbox("Attendee Timezone", pytz.all_timezones)

    if st.button("Schedule"):
        if meeting_time:
            converted_time = convert_timezone(meeting_time, user_timezone, attendee_timezone)
            st.success(
                f"Meeting on {meeting_date.strftime('%A, %d %B %Y')} at {converted_time}"
            )
        else:
            st.error("Enter valid time")
