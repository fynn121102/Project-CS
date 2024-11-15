import streamlit as st
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
import random
from geopy.geocoders import Nominatim

# Initialize events list with sample data
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

# List to store events user has joined
user_enrolled_events = []

# Function to render the main map
def render_map(search_query=""):
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)

    # Filter events based on search query
    filtered_events = [
        event for event in events
        if search_query.lower() in event["name"].lower() or search_query.lower() in event["description"].lower()
    ]

    # Display each event on the map
    for idx, event in enumerate(filtered_events):
        # Create a horizontal bar for participants
        participants_ratio = event["participants"] / event["max_participants"]
        participant_bar = f'<div style="width: 100%; background-color: grey; height: 10px; position: relative;">' \
                          f'<div style="width: {participants_ratio * 100}%; background-color: green; height: 10px;"></div>' \
                          f'</div>'

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
            <button onclick="window.location.href='?join_event={idx}'">Join Event</button>
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

# Handle event joining
join_event = st.experimental_get_query_params().get("join_event")
if join_event:
    event_idx = int(join_event[0])
    if event_idx < len(events):
        event = events[event_idx]
        if event["participants"] < event["max_participants"]:
            event["participants"] += 1
            if event not in user_enrolled_events:
                user_enrolled_events.append(event)
            st.success(f"You successfully joined '{event['name']}'!")
            st.experimental_set_query_params()

# Display the map
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

    location_choice = st.radio("Select event location", ["Click on Map", "Enter Address"])
    location = None

    if location_choice == "Click on Map":
        st.write("Click on the map below to select a location.")
        mini_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)
        location_picker = st_folium(mini_map, height=300, width=700)
        if location_picker and location_picker["last_clicked"]:
            location = location_picker["last_clicked"]

    elif location_choice == "Enter Address":
        address = st.text_input("Event Address (Street and Number)")
        if address:
            geolocator = Nominatim(user_agent="community-bridger")
            geocoded_location = geolocator.geocode(address)
            if geocoded_location:
                location = [geocoded_location.latitude, geocoded_location.longitude]
            else:
                st.warning("Address not found. Please try a different address.")

    if st.form_submit_button("Add Event"):
        if not location:
            st.warning("Please select a location on the map or enter an address for the event.")
        else:
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
                "weather": {"forecast": "Partly Cloudy ⛅", "temp": random.randint(15, 25)}  # Placeholder weather
            }
            events.append(new_event)
            st.success(f"Event '{name}' added successfully!")
            st.experimental_rerun()

# Display user's joined events
st.subheader("Your Joined Events")
if user_enrolled_events:
    for enrolled_event in user_enrolled_events:
        st.write(f"- {enrolled_event['name']} on {enrolled_event['date']} at {enrolled_event['time']}")
else:
    st.write("You have not joined any events yet.")


