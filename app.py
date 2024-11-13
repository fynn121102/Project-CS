import streamlit as st
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests
import random
import matplotlib.pyplot as plt
from io import BytesIO

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
            "location": [47.42391, 9.37477],
            "date": datetime(2024, 11, 20, 15, 30),
            "description": "Join us for a friendly football match at the city park.",
            "capacity": 20,
            "signed_up": 5,
            "outdoor": True
        },
        {
            "name": "Study Group Meetup",
            "organizer": "Bob",
            "location": [47.42456, 9.37616],
            "date": datetime(2024, 11, 24, 18, 0),
            "description": "Study session for upcoming exams.",
            "capacity": 15,
            "signed_up": 8,
            "outdoor": False
        }
    ]

# Fetch real-time weather forecast for the event location
def get_weather_forecast(lat, lon, date):
    endpoint = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,precipitation_hours",
        "start_date": date.strftime("%Y-%m-%d"),
        "end_date": date.strftime("%Y-%m-%d"),
        "timezone": "auto"
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        if "daily" in data and "precipitation_sum" in data["daily"]:
            precip = data["daily"]["precipitation_sum"][0]
            precip_hours = data["daily"]["precipitation_hours"][0]
            return precip, precip_hours
    return None, None

# Calculate cancellation probability based on weather
def calculate_cancellation_probability(event):
    precip, precip_hours = get_weather_forecast(event["location"][0], event["location"][1], event["date"])
    if event["outdoor"] and precip is not None:
        if precip > 5 or precip_hours > 3:
            return 80
        elif precip > 1:
            return 50
    return 10

# Generate graphical bar plot for participant and cancellation probability
def generate_event_graphs(event):
    fig, ax = plt.subplots(figsize=(2, 1.2))
    cancellation_prob = calculate_cancellation_probability(event)
    participant_count = event["signed_up"] / event["capacity"] * 100
    
    ax.bar(["Participants", "Cancellation"], [participant_count, cancellation_prob], color=["green", "red"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Percentage")
    
    # Save plot to a BytesIO object
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format="png")
    img_bytes.seek(0)
    plt.close(fig)
    
    return img_bytes

# Render map with events and search functionality
def render_map(center=[47.42391, 9.37477], zoom_start=13, search_query=""):
    map_ = folium.Map(location=center, zoom_start=zoom_start)
    for event in st.session_state["events"]:
        cancellation_prob = calculate_cancellation_probability(event)
        graph_image = generate_event_graphs(event)
        
        # Highlight marker if search query matches
        marker_color = "blue" if search_query.lower() in event["name"].lower() or search_query.lower() in event["description"].lower() else "green"
        
        popup_html = f"""
        <b style="font-family: Arial, sans-serif;">{event['name']}</b><br>
        Organizer: {event['organizer']}<br>
        Date & Time: {event['date']}<br>
        Participants: {event['signed_up']} / {event['capacity']}<br>
        Description: {event['description']}<br>
        <b>Cancellation Probability:</b> {cancellation_prob}%<br>
        <img src="data:image/png;base64,{graph_image.getvalue().decode()}" width="100%">
        <button>Join Event</button>
        """
        
        iframe = folium.IFrame(popup_html, width=300, height=180)
        folium.Marker(
            event["location"],
            popup=folium.Popup(iframe),
            icon=folium.Icon(color=marker_color)
        ).add_to(map_)
    return map_

# Event Creation Sidebar Form
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

    # Geolocation and map addition
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

# Search bar for events
search_query = st.text_input("Search Events by Name or Description", "").lower()

# Display the map with events
map_ = render_map(search_query=search_query)
st_folium(map_, width=700, height=500)

# Join Event Button
for i, event in enumerate(st.session_state["events"]):
    if st.button(f"Join {event['name']}", key=f"join_{i}"):
        if event["signed_up"] < event["capacity"]:
            st.session_state["events"][i]["signed_up"] += 1
            st.success(f"You joined the event: {event['name']}")
        else:
            st.warning(f"Event '{event['name']}' is already full!")
