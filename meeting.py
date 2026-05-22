import os
import streamlit as st
import datetime
import pytz
import yaml

from huggingface_hub import InferenceClient
from streamlit_chat import message

from smolagents import CodeAgent
from smolagents.tools import tool


from zoneinfo import available_timezones

# Custom CSS for styling
st.markdown(
    """
    <style>
        .stApp { background-color: #FFDAB9; }
        [data-testid="stSidebar"] { background-color: #DEB887 !important; }
        .stButton>button { background-color: #8B4513 !important; color: white !important; border-radius: 8px; }
        .stButton>button:hover { background-color: #5a2e1a !important; }
        .stTextArea textarea, .stTextInput input { background-color: #008000 !important; color: white !important; border-radius: 8px; }
        .stTextArea textarea::placeholder, .stTextInput input::placeholder { color: white !important; font-style: italic; }
    </style>
    """,
    unsafe_allow_html=True
)

# Available timezones for specific countries
country_timezones = {
    "Pakistan": pytz.country_timezones.get('PK', []),
    "India": pytz.country_timezones.get('IN', []),
    "USA": pytz.country_timezones.get('US', []),
    "UK": pytz.country_timezones.get('GB', []),
}
# Set Hugging Face API Token securely
# Set Hugging Face API Token

# Initialize Hugging Face Inference Client
client = InferenceClient("https://jc26mwg228mkj8dw.us-east-1.aws.endpoints.huggingface.cloud")

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """Fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(tz).strftime("%I:%M %p")
        return f"✅ The current time in **{timezone}** is **{local_time}**."
    except Exception as e:
        return f"⚠️ Error fetching time for timezone '{timezone}': {str(e)}"
# Function to convert time between timezones
def convert_timezone(time_str, from_tz, to_tz):
    """Converts time from one timezone to another."""
    try:
        from_zone = pytz.timezone(from_tz)
        to_zone = pytz.timezone(to_tz)
        
        # Convert string time to datetime object
        naive_time = datetime.datetime.strptime(time_str, "%I:%M %p")
        
        # Localize the time to the source timezone
        localized_time = from_zone.localize(naive_time)
        
        # Convert to the target timezone
        converted_time = localized_time.astimezone(to_zone)
        
        # Format the output time
        return converted_time.strftime("%I:%M %p")
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# Load Model
model = HfApiModel(
    max_tokens=2096,
    temperature=0.5,
    model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
    custom_role_conversions=None,
)

# Load Prompt Templates
with open("prompt.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

# Create CodeAgent
agent = CodeAgent(
    model=model,
    tools=[get_current_time_in_timezone],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)

# Function for text generation using Hugging Face LLM
def generate_text(prompt: str):
    output = client.text_generation(
        prompt,
        max_new_tokens=100,
    )
    return output

# Sidebar
st.sidebar.title("🔹 Scheduling Assistant")
option = st.sidebar.radio("📌 Choose a feature:", ("🌍 Timezone Converter", "📅 Schedule Meeting"))

if option == "🌍 Timezone Converter":
    st.title("🕒 Timezone Converter")
    time_input = st.text_input("Enter Time (HH:MM AM/PM)", placeholder="Example: 02:30 PM")
    
    from_timezone = st.selectbox("From Timezone", pytz.all_timezones)
    to_timezone = st.selectbox("To Timezone", pytz.all_timezones)
    
    if st.button("Convert Time"):
        if time_input:
            result = convert_timezone(time_input, from_timezone, to_timezone)
            st.success(result)
        else:
            st.error("⚠️ Please enter a valid time.")
elif option == "📅 Schedule Meeting":
    st.title("📅 Global Meeting Scheduler")

    # Date picker for meeting date
    meeting_date = st.date_input("📆 Select Meeting Date")  # Added date input
    meeting_time = st.text_input("Enter Meeting Time (HH:MM AM/PM)", placeholder="Example: 04:15 PM")
    user_timezone = st.selectbox("Your Timezone", sorted(pytz.all_timezones))
    attendee_timezone = st.selectbox("Attendee Timezone", sorted(pytz.all_timezones))
    
    if st.button("Schedule Meeting"):
        if meeting_time:
            converted_time = convert_timezone(meeting_time, user_timezone, attendee_timezone)
            st.success(f"📌 Meeting scheduled on **{meeting_date.strftime('%A, %d %B %Y')}** at **{converted_time}**.")
        else:
            st.error("⚠️ Please enter a valid meeting time.")



