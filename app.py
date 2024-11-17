import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
import random
from datetime import datetime
import google.auth.exceptions

# Path to the service account key
service_account_path = "serviceAccountKey.json"

# Initialize Firebase Admin SDK with error handling
if not os.path.exists(service_account_path):
    st.error("Firebase service account key not found. Please upload the key file.")
else:
    try:
        # Check if Firebase app is already initialized
        if not firebase_admin._apps:
            # Initialize Firebase Admin with the service account key
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://community-bridger-default-rtdb.europe-west1.firebasedatabase.app/'
            })
        else:
            print("Firebase is already initialized.")
    except google.auth.exceptions.RefreshError as e:
        st.error(f"Refresh error: {e}")
        raise
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")
        raise

# Firebase database references
events_ref = db.reference("events")
user_joined_ref = db.reference("user_joined")
names_ref = db.reference("names")

# Fetch events from Firebase
def fetch_events():
    try:
        return events_ref.get() or {}
    except Exception as e:
        st.error(f"Error fetching events: {e}")
        return {}

# Fetch joined events
def fetch_joined_events():
    try:
        return user_joined_ref.get() or {}
    except Exception as e:
        st.error(f"Error fetching joined events: {e}")
        return {}

# Save a name to Firebase
def save_name(name):
    try:
        names_ref.push(name)
    except Exception as e:
        st.error(f"Error saving name: {e}")

# Fetch all saved names
def fetch_names():
    try:
        return names_ref.get() or {}
    except Exception as e:
        st.error(f"Error fetching names: {e}")
        return {}

# Add an event to Firebase
def add_event_to_firebase(event_data):
    try:
        events_ref.push(event_data)
    except Exception as e:
        st.error(f"Error adding event: {e}")

# Join an event
def join_event(event_key):
    try:
        event_data = events_ref.child(event_key).get()
        if event_data and event_data["participants"] < event_data["max_participants"]:
            event_data["participants"] += 1
            events_ref.child(event_key).update({"participants": event_data["participants"]})
            user_joined_ref.push(event_key)
    except Exception as e:
        st.error(f"Error joining event: {e}")

# Leave an event
def leave_event(event_key):
    try:
        event_data = events_ref.child(event_key).get()
        if event_data:
            event_data["participants"] -= 1
            events_ref.child(event_key).update({"participants": event_data["participants"]})
            joined_events = fetch_joined_events()
            for joined_key, joined_event_key in joined_events.items():
                if joined_event_key == event_key:
                    user_joined_ref.child(joined_key).delete()
                    break
    except Exception as e:
        st.error(f"Error leaving event: {e}")

# Display map with events
def render_map(events, joined_events, search_query=""):
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)
    for event_key, event in events.items():
        if search_query.lower() in event["name"].lower() or search_query.lower() in event["description"].lower():
            participants_ratio = event["participants"] / event["max_participants"]
            participant_bar = f'<div style="width: 100%; background-color: grey; height: 10px;">' \
                              f'<div style="width: {participants_ratio * 100}%; background-color: green; height: 10px;"></div>' \
                              f'</div>'
            cancellation_prob_bar = f'<div style="width: 100%; background-color: grey; height: 10px;">' \
                                    f'<div style="width: {event["cancellation_prob"]}%; background-color: red; height: 10px;"></div>' \
                                    f'</div>'
            if event_key in joined_events.values():
                action_button = f'<button onclick="window.location.href=\'?leave_event={event_key}\'">Leave Event</button>'
            else:
                action_button = f'<button onclick="window.location.href=\'?join_event={event_key}\'">Join Event</button>'
            popup_content = f"""
            <div style="font-family:Arial; width:250px;">
                <h4>{event['name']}</h4>
                <p><b>Organized by:</b> {event['organizer']}</p>
                <p><b>Date:</b> {event['date']} at {event['time']}</p>
                <p><b>Description:</b> {event['description']}</p>
                <p><b>Weather:</b> {event['weather']['forecast']} ({event['weather']['temp']}°C)</p>
                <p><b>Participants:</b></p>
                {participant_bar}
                <p>{event['participants']} / {event['max_participants']}</p>
                <p><b>Cancellation Probability:</b></p>
                {cancellation_prob_bar}
                {action_button}
            </div>
            """
            folium.Marker(
                location=event["location"],
                icon=folium.Icon(color="blue", icon="info-sign"),
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=event["name"]
            ).add_to(base_map)
    return base_map

# Main application
st.title("JoinMy")
st.header("Connect with fellows around you!")

# Name input
st.subheader("Add Your Name")
name_input = st.text_input("Enter your name")
if st.button("Submit"):
    if name_input:
        save_name(name_input)
        st.success(f"Name '{name_input}' saved!")
    else:
        st.error("Please enter a valid name.")

# Saved names
st.subheader("Saved Names")
saved_names = fetch_names()
for name_key, name in saved_names.items():
    st.write(name)

# Event search
search_query = st.text_input("Search events", "")

# Fetch events and joined events
events = fetch_events()
joined_events = fetch_joined_events()

# Handle join/leave events
params = st.experimental_get_query_params()
if "join_event" in params:
    join_event(params["join_event"][0])
    st.experimental_set_query_params()

if "leave_event" in params:
    leave_event(params["leave_event"][0])
    st.experimental_set_query_params()

# Display map with events
map_ = render_map(events, joined_events, search_query)
st_folium(map_, width=700)

# Add a new event
with st.form("add_event_form"):
    st.subheader("Add a New Event")
    name = st.text_input("Event Name")
    organizer = st.text_input("Organizer Name")
    description = st.text_area("Event Description")
    date = st.date_input("Event Date", value=datetime.now())
    time = st.time_input("Event Time", value=datetime.now().time())
    max_participants = st.number_input("Max Participants", min_value=1, step=1)
    event_type = st.selectbox("Event Type", ["outdoor", "indoor"])
    address = st.text_input("Event Address (Street and Number)")
    weather_forecast = st.text_input("Weather Forecast (e.g., Sunny 🌞, Rainy 🌧️)")
    weather_temp = st.number_input("Temperature (°C)", value=20)

    if st.form_submit_button("Add Event"):
        # Simulated geocoding logic for now
        location = [47.4239 + random.uniform(-0.01, 0.01), 9.3748 + random.uniform(-0.01, 0.01)]
        event_data = {
            "name": name,
            "organizer": organizer,
            "location": location,
            "date": date.strftime("%Y-%m-%d"),
            "time": time.strftime("%H:%M"),
            "description": description,
            "participants": 0,
            "max_participants": max_participants,
            "event_type": event_type,
            "cancellation_prob": random.randint(5, 30),
            "weather": {"forecast": weather_forecast, "temp": weather_temp}
        }
        add_event_to_firebase(event_data)
        st.success(f"Event '{name}' added successfully!")
        st.experimental_rerun()

# Display joined events
st.subheader("Your Joined Events")
for joined_key, event_key in joined_events.items():
    event = events.get(event_key, {})
    if event:
        st.write(f"- {event['name']} on {event['date']} at {event['time']}")
