import os
import streamlit as st
import datetime
import pytz
import yaml
from huggingface_hub import InferenceClient
from streamlit_chat import message
from zoneinfo import available_timezones

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp { background-color: #FFDAB9; }
[data-testid="stSidebar"] { background-color: #DEB887 !important; }
.stButton>button { background-color: #8B4513 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- HF CLIENT ----------------
client = InferenceClient(model="Qwen/Qwen2.5-Coder-32B-Instruct")

# ---------------- TIMEZONES ----------------
country_timezones = {
    "Pakistan": pytz.country_timezones.get('PK', []),
    "India": pytz.country_timezones.get('IN', []),
    "USA": pytz.country_timezones.get('US', []),
    "UK": pytz.country_timezones.get('GB', []),
}

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

# ---------------- STREAMLIT UI ----------------
st.sidebar.title("🔹 Scheduling Assistant")
option = st.sidebar.radio("Choose:", ("🌍 Timezone Converter", "📅 Schedule Meeting"))

# ---------------- CONVERTER ----------------
if option == "🌍 Timezone Converter":
    st.title("🕒 Timezone Converter")

    time_input = st.text_input("Enter Time (HH:MM AM/PM)")
    from_timezone = st.selectbox("From Timezone", pytz.all_timezones)
    to_timezone = st.selectbox("To Timezone", pytz.all_timezones)

    if st.button("Convert"):
        if time_input:
            result = convert_timezone(time_input, from_timezone, to_timezone)
            st.success(result)
        else:
            st.error("Enter valid time")

# ---------------- MEETING ----------------
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
