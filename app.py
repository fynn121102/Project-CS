import streamlit as st
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import random

# App Title and Header
st.title("Community Bridger")
st.subheader("Connect with fellows around you!")

# Initialize geolocator for address search
geolocator = Nominatim(user_agent="community_bridger")

# Data Storage
if "events" not in st.session_state:
    st.session_state["events"] = [
        {
            "name": "Football Match",
            "organizer": "Alice",
            "location": [47.42391, 9.37477],  # Coordinates for St. Gallen, Switzerland
            "date": datetime(2024, 11, 20, 15, 30),
            "description": "Join us for a friendly football match at the city park.",
            "capacity": 20,
            "signed_up": 5,
            "outdoor": True
        },
        {
            "name": "Study Group Meetup",
            "organizer": "Bob",
            "location": [47.42456, 9.37616],  # Different location in St. Gallen
            "date": datetime(2024, 11, 24, 18, 0),
            "description": "Study session for upcoming exams.",
            "capacity": 15,
            "signed_up": 8,
            "outdoor": False
        }
    ]

# Function to calculate cancellation probability
def calculate_cancellation_probability(event):
    if event["outdoor"]:
        # Simulate a weather-based calculation
        forecast = random.choice(["sunny", "cloudy", "rainy", "stormy"])
        if forecast == "rainy":
            return 70  # Higher probability due to rain
        elif forecast == "stormy":
            return 90  # Very high due to storm risk
        else:
            return 20  # Lower probability if clear or cloudy
    else:
        return 5  # Minimal risk for indoor events

# Function to render map with events
def render_map(center=[47.42391, 9.37477], zoom_start=13, search_query=""):
    map_ = folium.Map(location=center, zoom_start=zoom_start)
    for event in st.session_state["events"]:
        # Calculate cancellation probability
        prob = calculate_cancellation_probability(event)
        color = "red" if prob > 50 else "green"
        
        # Display cancellation and participant probability as graphs
        popup_html = f"""
        <b>{event['name']}</b><br>
        Organized by: {event['organizer']}<br>
        Participants: {event['signed_up']} / {event['capacity']}<br>
        Date & Time: {event['date']}<br>
        Description: {event['description']}<br>
        <b>Weather Forecast:</b> {forecast}<br>
        <b>Cancellation Probability:</b> {prob}%<br>
        <b>Join Now</b><br>
        """
        
        iframe = folium.IFrame(popup_html, width=300, height=150)
        folium.Marker(
            event["location"],
            popup=folium.Popup(iframe),
            icon=folium.Icon(color=color)
        ).add_to(map_)
    return map_

# Event Creation
with st.sidebar.form("new_event"):
    st.subheader("Create a New Event")
    name = st.text_input("Event Name")
    organizer = st.text_input("Organizer")
    date = st.date_input("Date", datetime.today())
    time = st.time_input("Time", datetime.now().time())
    description = st.text_area("Description")
    capacity = st.number_input("Capacity", min_value=1, step=1)
    outdoor = st.checkbox("Outdoor Event")
    location_name = st.text_input("Location (Type city name)")

    # Geolocate and add event to map
    if st.form_submit_button("Add Event"):
        if location_name:
            location = geolocator.geocode(location_name)
            if location:
                lat_lng = [location.latitude, location.longitude]
                new_event = {
                    "name": name,
                    "organizer": organizer,
                    "location": lat_lng,
                    "date": datetime.combine(date, time),
                    "description": description,
                    "capacity": capacity,
                    "signed_up": 0,
                    "outdoor": outdoor
                }
                st.session_state["events"].append(new_event)
                st.success(f"Event '{name}' added at {location_name}")
            else:
                st.error("Location not found. Please try a different city.")

# Event Search
search_query = st.text_input("Search Events", "").lower()

# Display Map
map_ = render_map(search_query=search_query)
st_folium(map_, width=700, height=500)

# Event Registration (Join Button)
for i, event in enumerate(st.session_state["events"]):
    if st.button(f"Join {event['name']}", key=f"join_{i}"):
        if event["signed_up"] < event["capacity"]:
            st.session_state["events"][i]["signed_up"] += 1
            st.success(f"You joined the event: {event['name']}")
        else:
            st.warning(f"Event '{event['name']}' is already full!")
