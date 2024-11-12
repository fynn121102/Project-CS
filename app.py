# Import necessary libraries
import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import random

# Initialize event list with future dates
events = [
    {
        "name": "Football Match",
        "organizer": "Max Mustermann",
        "location": [47.4239, 9.3748],
        "date": "2024-11-18",
        "time": "14:15",
        "description": "Join us for a friendly game of football!",
        "participants": 7,
        "max_participants": 20,
        "weather": "Sunny, 18°C",
        "weather_emoji": "☀️",
        "cancellation_prob": 0.2,
    },
    {
        "name": "Ride to Zurich",
        "organizer": "Tanja Musterfrau",
        "location": [47.4249, 9.3768],
        "date": "2024-11-25",
        "time": "10:15",
        "description": "Carpool ride to Zurich. Join if interested!",
        "participants": 2,
        "max_participants": 3,
        "weather": "Cloudy, 15°C",
        "weather_emoji": "☁️",
        "cancellation_prob": 0.1,
    },
    {
        "name": "Hiking Trip",
        "organizer": "Lara Testperson",
        "location": [47.4299, 9.3825],
        "date": "2024-12-12",
        "time": "08:00",
        "description": "An adventurous hike in the mountains.",
        "participants": 5,
        "max_participants": 10,
        "weather": "Rainy, 12°C",
        "weather_emoji": "🌧️",
        "cancellation_prob": 0.6,
    },
]

# Streamlit app title and description
st.title("Community Event Map")
st.write("Explore and organize community events happening around St. Gallen!")

# Sidebar for creating a new event
st.sidebar.title("Add a New Event")
name = st.sidebar.text_input("Event Name")
organizer = st.sidebar.text_input("Organizer")
date = st.sidebar.date_input("Event Date", min_value=datetime(2024, 11, 14), max_value=datetime(2024, 12, 24))
time = st.sidebar.time_input("Event Time")
description = st.sidebar.text_area("Description")
max_participants = st.sidebar.number_input("Max Participants", min_value=1, value=10)
weather = st.sidebar.selectbox("Weather Forecast", ["Sunny, 18°C ☀️", "Cloudy, 15°C ☁️", "Rainy, 12°C 🌧️"])
location_lat = st.sidebar.number_input("Latitude", min_value=47.0, max_value=48.0, value=47.4239)
location_lon = st.sidebar.number_input("Longitude", min_value=9.0, max_value=10.0, value=9.3748)
cancellation_prob = st.sidebar.slider("Cancellation Probability", 0.0, 1.0, 0.2)

if st.sidebar.button("Add Event"):
    # Add new event to the events list
    weather_type, emoji = weather.split(" ")
    events.append({
        "name": name,
        "organizer": organizer,
        "location": [location_lat, location_lon],
        "date": date.strftime("%Y-%m-%d"),
        "time": time.strftime("%H:%M"),
        "description": description,
        "participants": 0,
        "max_participants": max_participants,
        "weather": weather_type,
        "weather_emoji": emoji,
        "cancellation_prob": cancellation_prob,
    })
    st.sidebar.success("Event added successfully!")

# Filter events based on search
st.sidebar.title("Search Events")
search_term = st.sidebar.text_input("Search by Event Name")
filtered_events = [event for event in events if search_term.lower() in event["name"].lower()]

# Initialize the Folium map centered around St. Gallen
map_center = [47.4239, 9.3748]
m = folium.Map(location=map_center, zoom_start=13)

# Display filtered event markers on the map
for event in filtered_events:
    cancel_percent = int(event["cancellation_prob"] * 100)
    
    # Create HTML popup with event details
    popup_html = f"""
    <b>{event['name']}</b> {event['weather_emoji']}<br>
    <i>{event['date']}, {event['time']}</i><br>
    Organizer: {event['organizer']}<br>
    Participants: {event['participants']} / {event['max_participants']}<br>
    Weather: {event['weather']}<br>
    Description: {event['description']}<br>
    Cancellation Probability: <progress value="{cancel_percent}" max="100"></progress> {cancel_percent}%
    """
    
    popup = folium.Popup(popup_html, max_width=300)
    folium.Marker(
        location=event["location"],
        popup=popup,
        tooltip=event["name"],
        icon=folium.Icon(color="blue" if event["participants"] < event["max_participants"] else "gray")
    ).add_to(m)

# Display the map in Streamlit
st_folium(m, width=700, height=500)

# Sidebar to join events
st.sidebar.title("Join an Event")
event_to_join = st.sidebar.selectbox("Select an event to join", [event["name"] for event in filtered_events])

if st.sidebar.button("Join Event"):
    for event in events:
        if event["name"] == event_to_join:
            if event["participants"] < event["max_participants"]:
                event["participants"] += 1
                st.sidebar.success(f"You have joined {event_to_join}!")
            else:
                st.sidebar.error(f"Sorry, {event_to_join} is fully booked.")

# Display event details in the sidebar
st.sidebar.title("Event Details")
for event in filtered_events:
    st.sidebar.subheader(f"{event['name']} {event['weather_emoji']}")
    st.sidebar.write(f"Date: {event['date']}, Time: {event['time']}")
    st.sidebar.write(f"Organizer: {event['organizer']}")
    st.sidebar.write(f"Participants: {event['participants']} / {event['max_participants']}")
    st.sidebar.write(f"Weather: {event['weather']}")
    st.sidebar.write(f"Description: {event['description']}")
    st.sidebar.progress(event["cancellation_prob"])
    st.sidebar.write(f"Cancellation Probability: {int(event['cancellation_prob'] * 100)}%")
    st.sidebar.write("---")

