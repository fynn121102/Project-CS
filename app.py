import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import random
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt

# Initialize event data
events = [
    {
        "name": "Football Match",
        "organizer": "John Doe",
        "location": [47.4239, 9.3748],
        "date": "2024-11-20",
        "time": "15:00",
        "description": "Join us for a friendly football match!",
        "participants": 15,
        "max_participants": 20,
        "event_type": "outdoor",
        "cancellation_prob": 30,
        "weather": {"forecast": "Sunny 🌞", "temp": 20}
    },
    {
        "name": "Study Group",
        "organizer": "Jane Smith",
        "location": [47.4245, 9.3769],
        "date": "2024-11-22",
        "time": "10:00",
        "description": "Group study session for exams.",
        "participants": 8,
        "max_participants": 10,
        "event_type": "indoor",
        "cancellation_prob": 5,
        "weather": {"forecast": "Cloudy ☁️", "temp": 18}
    }
]

# User's joined events
user_enrolled_events = []

# Function to render the map
def render_map(search_query=""):
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)

    # Filter events by search query
    filtered_events = [
        event for event in events
        if search_query.lower() in event["name"].lower() or search_query.lower() in event["description"].lower()
    ]

    for idx, event in enumerate(filtered_events):
        # Visual bar for participants
        participants_ratio = event["participants"] / event["max_participants"]
        participant_bar = f'<div style="width: 100%; background-color: grey; height: 10px; position: relative;">' \
                          f'<div style="width: {participants_ratio * 100}%; background-color: green; height: 10px;"></div>' \
                          f'</div>'

        # Visual bar for cancellation probability
        cancellation_prob_bar = f'<div style="width: 100%; background-color: grey; height: 10px; position: relative;">' \
                                f'<div style="width: {event["cancellation_prob"]}%; background-color: red; height: 10px;"></div>' \
                                f'</div>'

        # Determine join/leave button state
        if event in user_enrolled_events:
            action_button = f'<button onclick="window.location.href=\'?leave_event={idx}\'">Leave Event</button>'
        else:
            action_button = f'<button onclick="window.location.href=\'?join_event={idx}\'">Join Event</button>'

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
            <p>{event['cancellation_prob']}%</p>
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

# Streamlit app layout
st.title("Community-Bridger")
st.header("Connect with fellows around you!")

# Event search bar
search_query = st.text_input("Search events", "")

# Handle join/leave events
params = st.experimental_get_query_params()
if "join_event" in params:
    event_idx = int(params["join_event"][0])
    event = events[event_idx]
    if event not in user_enrolled_events and event["participants"] < event["max_participants"]:
        event["participants"] += 1
        user_enrolled_events.append(event)
    st.experimental_set_query_params()

if "leave_event" in params:
    event_idx = int(params["leave_event"][0])
    event = events[event_idx]
    if event in user_enrolled_events:
        event["participants"] -= 1
        user_enrolled_events.remove(event)
    st.experimental_set_query_params()

# Display map
map_ = render_map(search_query=search_query)
st_data = st_folium(map_, width=700)

# Form to add a new event
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

    if st.form_submit_button("Add Event"):
        if address:
            geolocator = Nominatim(user_agent="community-bridger")
            geocoded_location = geolocator.geocode(address)
            if geocoded_location:
                location = [geocoded_location.latitude, geocoded_location.longitude]
                new_event = {
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
                    "weather": {"forecast": "Partly Cloudy ⛅", "temp": random.randint(15, 25)}
                }
                events.append(new_event)
                st.success(f"Event '{name}' added successfully!")
                st.experimental_rerun()
            else:
                st.warning("Address not found. Please try again.")

# User's joined events
st.subheader("Your Joined Events")
if user_enrolled_events:
    for event in user_enrolled_events:
        st.write(f"- {event['name']} on {event['date']} at {event['time']}")
else:
    st.write("You have not joined any events yet.")



