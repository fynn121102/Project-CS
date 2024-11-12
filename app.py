# Import necessary libraries
import streamlit as st
import folium
from streamlit_folium import st_folium
import random

# Streamlit app title and description
st.title("Community Event Map")
st.write("Explore community events happening around St. Gallen!")

# Hardcoded events data with a new 'cancellation probability' field
events = [
    {
        "name": "Football Match",
        "organizer": "Max Mustermann",
        "location": [47.4239, 9.3748],
        "date": "31st October",
        "time": "14:15",
        "description": "Join us for a friendly game of football!",
        "participants": 7,
        "max_participants": 20,
        "weather": "Sunny, 18°C",
        "weather_emoji": "☀️",
        "cancellation_prob": 0.2,  # 20% chance of cancellation
    },
    {
        "name": "Ride to Zurich",
        "organizer": "Tanja Musterfrau",
        "location": [47.4249, 9.3768],
        "date": "25th October",
        "time": "10:15",
        "description": "Carpool ride to Zurich. Join if interested!",
        "participants": 2,
        "max_participants": 3,
        "weather": "Cloudy, 15°C",
        "weather_emoji": "☁️",
        "cancellation_prob": 0.1,  # 10% chance of cancellation
    },
    {
        "name": "Hiking Trip",
        "organizer": "Lara Testperson",
        "location": [47.4299, 9.3825],
        "date": "29th October",
        "time": "08:00",
        "description": "An adventurous hike in the mountains.",
        "participants": 5,
        "max_participants": 10,
        "weather": "Rainy, 12°C",
        "weather_emoji": "🌧️",
        "cancellation_prob": 0.6,  # 60% chance of cancellation
    },
]

# Initialize the Folium map centered around St. Gallen
map_center = [47.4239, 9.3748]
m = folium.Map(location=map_center, zoom_start=13)

# Display event markers with weather and cancellation info
for event in events:
    # Calculate the cancellation probability as a percentage
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
    
    # Create and add marker with popup
    popup = folium.Popup(popup_html, max_width=300)
    folium.Marker(
        location=event["location"],
        popup=popup,
        tooltip=event["name"],
        icon=folium.Icon(color="blue" if event["participants"] < event["max_participants"] else "gray")
    ).add_to(m)

# Display the map in Streamlit
st_folium(m, width=700, height=500)

# Sidebar for joining events
st.sidebar.title("Join an Event")
event_to_join = st.sidebar.selectbox("Select an event to join", [event["name"] for event in events])

# Display join button and handle joining
if st.sidebar.button("Join Event"):
    for event in events:
        if event["name"] == event_to_join:
            if event["participants"] < event["max_participants"]:
                event["participants"] += 1
                st.sidebar.success(f"You have joined {event_to_join}!")
            else:
                st.sidebar.error(f"Sorry, {event_to_join} is fully booked.")

# Sidebar event details
st.sidebar.title("Event Details")
for event in events:
    st.sidebar.subheader(f"{event['name']} {event['weather_emoji']}")
    st.sidebar.write(f"Date: {event['date']}, Time: {event['time']}")
    st.sidebar.write(f"Organizer: {event['organizer']}")
    st.sidebar.write(f"Participants: {event['participants']} / {event['max_participants']}")
    st.sidebar.write(f"Weather: {event['weather']}")
    st.sidebar.write(f"Description: {event['description']}")
    
    # Display cancellation probability as a bar
    st.sidebar.progress(event["cancellation_prob"])
    st.sidebar.write(f"Cancellation Probability: {int(event['cancellation_prob'] * 100)}%")
    st.sidebar.write("---")
