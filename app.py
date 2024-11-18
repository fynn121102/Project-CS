import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime
import random

# Initialize session state for joined events and events list
if "joined_events" not in st.session_state:
    st.session_state.joined_events = []  # Stores event ids that user joined
    st.session_state.events = [
        {"id": 1, "name": "Yoga Class", "organizer": "Alice", "location": [47.4239, 9.3748], "date": "2024-12-10", "time": "10:00 AM", "description": "Relax and stretch!", "participants": 5, "max_participants": 20, "event_type": "outdoor", "cancellation_prob": 5, "weather": {"forecast": "Sunny 🌞", "temp": 22}},
        {"id": 2, "name": "Coding Workshop", "organizer": "Bob", "location": [47.4250, 9.3750], "date": "2024-12-15", "time": "1:00 PM", "description": "Learn to code!", "participants": 2, "max_participants": 20, "event_type": "indoor", "cancellation_prob": 10, "weather": {"forecast": "Cloudy ☁️", "temp": 18}},
    ]

# Update participants count in the in-memory events
def update_participants(event_id, new_participants):
    for event in st.session_state.events:
        if event["id"] == event_id:
            event["participants"] = new_participants
            break

# Handle Join/Leave Events
params = st.experimental_get_query_params()
if "join_event" in params:
    event_id = int(params["join_event"][0])
    for event in st.session_state.events:
        if event["id"] == event_id and event["participants"] < event["max_participants"]:
            event["participants"] += 1
            st.session_state.joined_events.append(event_id)
            update_participants(event_id, event["participants"])
    st.experimental_set_query_params()

if "leave_event" in params:
    event_id = int(params["leave_event"][0])
    for event in st.session_state.events:
        if event["id"] == event_id:
            event["participants"] -= 1
            st.session_state.joined_events.remove(event_id)
            update_participants(event_id, event["participants"])
    st.experimental_set_query_params()

# Render map with events
def render_map(events, user_enrolled_events, search_query=""):
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)
    filtered_events = [
        event for event in events
        if search_query.lower() in event["name"].lower() or search_query.lower() in event["description"].lower()
    ]
    for event in filtered_events:
        participants_ratio = event["participants"] / event["max_participants"]
        participant_bar = f'<div style="width: 100%; background-color: grey; height: 10px;">' \
                          f'<div style="width: {participants_ratio * 100}%; background-color: green; height: 10px;"></div>' \
                          f'</div>'  
        if event["id"] in user_enrolled_events:
            action_button = f'<button onclick="window.location.href=\'?leave_event={event["id"]}\'">Leave Event</button>'
        else:
            action_button = f'<button onclick="window.location.href=\'?join_event={event["id"]}\'">Join Event</button>'
        popup_content = f"""
        <div style="font-family:Arial; width:250px;">
            <h4>{event['name']}</h4>
            <p><b>Organized by:</b> {event['organizer']}</p>
            <p><b>Date:</b> {event['date']} at {event['time']}</p>
            <p><b>Description:</b> {event['description']}</p>
            <p><b>Participants:</b></p>
            {participant_bar}
            <p>{event['participants']} / {event['max_participants']}</p>
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

# App setup
st.title("Community-Bridger")
st.header("Connect with fellows around you!")

# Search Bar
search_query = st.text_input("Search events", "")

# Display Map
map_ = render_map(st.session_state.events, st.session_state.joined_events, search_query=search_query)
st_folium(map_, width=700)

# Add a New Event
with st.form("add_event_form"):
    st.subheader("Add a New Event")
    name = st.text_input("Event Name")
    organizer = st.text_input("Organizer Name")
    description = st.text_area("Event Description")
    date = st.date_input("Event Date", value=datetime.now())
    time = st.time_input("Event Time", value=datetime.now().time())
    max_participants = st.number_input("Max Participants", min_value=1, step=1)
    event_type = st.selectbox("Event Type", ["outdoor", "indoor"])
    location_lat = st.number_input("Latitude", format="%.6f")
    location_lng = st.number_input("Longitude", format="%.6f")
    cancellation_prob = random.randint(5, 30)
    weather_forecast = random.choice(["Sunny 🌞", "Cloudy ☁️", "Partly Cloudy ⛅"])
    weather_temp = random.randint(5, 20)

    if st.form_submit_button("Add Event"):
        if name and organizer and description and location_lat and location_lng:
            new_event = {
                "name": name,
                "organizer": organizer,
                "location": [location_lat, location_lng],
                "date": date.strftime("%Y-%m-%d"),
                "time": time.strftime("%H:%M"),
                "description": description,
                "participants": 0,
                "max_participants": max_participants,
                "event_type": event_type,
                "cancellation_prob": cancellation_prob,
                "weather": {"forecast": weather_forecast, "temp": weather_temp}
            }
            st.session_state.events.append(new_event)  # Add to in-memory event list
            st.session_state.joined_events.append(new_event["id"])  # Automatically join the new event
            st.success(f"Event '{name}' added successfully!")
            st.experimental_rerun()  # Reload app to reflect changes
        else:
            st.error("Please fill in all fields!")

# Display Joined Events
st.subheader("Your Joined Events")
if st.session_state.joined_events:
    for event_id in st.session_state.joined_events:
        event = next(event for event in st.session_state.events if event["id"] == event_id)
        st.write(f"- {event['name']} on {event['date']} at {event['time']}")
else:
    st.write("You have not joined any events yet.")

