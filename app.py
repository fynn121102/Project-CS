import streamlit as st
import firebase_admin
from firebase_admin import credentials, db, messaging
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime
import random

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")  # Use the uploaded service key
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://community-bridger-default-rtdb.firebaseio.com/'
    })

# Firebase database references
events_ref = db.reference("events")
user_joined_ref = db.reference("user_joined")
names_ref = db.reference("names")
tokens_ref = db.reference("tokens")  # To store FCM tokens

# Helper functions
def fetch_events():
    return events_ref.get() or {}

def fetch_joined_events():
    return user_joined_ref.get() or {}

def save_name(name):
    names_ref.push(name)

def fetch_names():
    return names_ref.get() or {}

def add_event_to_firebase(event_data):
    events_ref.push(event_data)

def join_event(event_key):
    event_data = events_ref.child(event_key).get()
    if event_data and event_data["participants"] < event_data["max_participants"]:
        event_data["participants"] += 1
        events_ref.child(event_key).update({"participants": event_data["participants"]})
        user_joined_ref.push(event_key)
        send_fcm_message(f"Someone joined your event: {event_data['name']}")

def leave_event(event_key):
    event_data = events_ref.child(event_key).get()
    if event_data:
        event_data["participants"] -= 1
        events_ref.child(event_key).update({"participants": event_data["participants"]})
        joined_events = fetch_joined_events()
        for joined_key, joined_event_key in joined_events.items():
            if joined_event_key == event_key:
                user_joined_ref.child(joined_key).delete()
                break
        send_fcm_message(f"Someone left your event: {event_data['name']}")

def geocode_address(address, api_key="YOUR_OPENCAGE_API_KEY"):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            coordinates = results[0]['geometry']
            return [coordinates['lat'], coordinates['lng']]
    return None

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
                <p><b>Cancellation Probability:</b> {event['cancellation_prob']}%</p>
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

def send_fcm_message(message):
    """Send an FCM notification."""
    tokens = tokens_ref.get() or []
    if not tokens:
        return
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title="Community Bridger Update",
            body=message,
        ),
        tokens=tokens
    )
    response = messaging.send_multicast(message)
    print(f"FCM: Sent {response.success_count} messages, {response.failure_count} failed.")

# Streamlit app
st.title("Community-Bridger")
st.header("Connect with fellows around you!")

# FCM Token Input (for testing/demo purposes)
st.subheader("Register Device for Notifications")
token_input = st.text_input("Enter FCM Token")
if st.button("Register Token"):
    tokens_ref.push(token_input)
    st.success("Token registered!")

# Name input
st.subheader("Add Your Name")
name_input = st.text_input("Enter your name")
if st.button("Submit"):
    save_name(name_input)
    st.success(f"Name '{name_input}' saved!")

# Display saved names
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

# Display map
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
        location = geocode_address(address)
        if location:
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
            send_fcm_message(f"New event added: {name}")
            st.success(f"Event '{name}' added
