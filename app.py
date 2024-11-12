import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime, timedelta
import random

# API URL and default city coordinates
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_LAT, DEFAULT_LON = 47.4239, 9.3748  # St. Gallen

# Pre-existing events with updated dates
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
    # Additional events here...
]

# Function to get weather forecast from Open-Meteo API
def get_weather_forecast(lat, lon, date):
    date_str = date.strftime("%Y-%m-%d")
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,temperature_2m_min,temperature_2m_max",
        "start_date": date_str,
        "end_date": date_str,
        "timezone": "Europe/Zurich",
    }
    response = requests.get(WEATHER_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        forecast = data.get("daily", {})
        weather = {
            "precipitation": forecast.get("precipitation_sum", [0])[0],
            "temp_min": forecast.get("temperature_2m_min", [0])[0],
            "temp_max": forecast.get("temperature_2m_max", [0])[0],
        }
        return weather
    else:
        st.error("Error retrieving weather data.")
        return None

# Function to calculate cancellation probability based on weather
def calculate_cancellation_probability(precipitation):
    if precipitation > 15:  # Heavy rain
        return 0.8
    elif precipitation > 5:  # Moderate rain
        return 0.5
    else:  # Light or no rain
        return 0.1

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
location_lat = st.sidebar.number_input("Latitude", min_value=47.0, max_value=48.0, value=DEFAULT_LAT)
location_lon = st.sidebar.number_input("Longitude", min_value=9.0, max_value=10.0, value=DEFAULT_LON)

if st.sidebar.button("Add Event"):
    weather_data = get_weather_forecast(location_lat, location_lon, date)
    if weather_data:
        precipitation = weather_data["precipitation"]
        temp_min = weather_data["temp_min"]
        temp_max = weather_data["temp_max"]
        weather = f"{temp_max}°C/{temp_min}°C, Precipitation: {precipitation} mm"
        cancellation_prob = calculate_cancellation_probability(precipitation)
        emoji = "☀️" if cancellation_prob < 0.3 else "🌧️" if cancellation_prob > 0.6 else "☁️"
        
        events.append({
            "name": name,
            "organizer": organizer,
            "location": [location_lat, location_lon],
            "date": date.strftime("%Y-%m-%d"),
            "time": time.strftime("%H:%M"),
            "description": description,
            "participants": 0,
            "max_participants": max_participants,
            "weather": weather,
            "weather_emoji": emoji,
            "cancellation_prob": cancellation_prob,
        })
        st.sidebar.success("Event added successfully!")

# Display map
map_center = [47.4239, 9.3748]
m = folium.Map(location=map_center, zoom_start=13)

for event in events:
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

# Sidebar for joining events
st.sidebar.title("Join an Event")
event_to_join = st.sidebar.selectbox("Select an event to join", [event["name"] for event in events])

if st.sidebar.button("Join Event"):
    for event in events:
        if event["name"] == event_to_join:
            if event["participants"] < event["max_participants"]:
                event["participants"] += 1
                st.sidebar.success(f"You have joined {event_to_join}!")
            else:
                st.sidebar.error(f"Sorry, {event_to_join} is fully booked.")


