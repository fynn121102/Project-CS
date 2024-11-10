# Import necessary libraries
import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# Constants
ST_GALLEN_LOCATION = [47.4239, 9.3748]  # Coordinates of St. Gallen
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# Sample event data
events = [
    {
        "name": "Football match",
        "date": "2024-10-31 14:15",
        "organizer": "Max Mustermann",
        "location": [47.425, 9.377],
        "capacity": 20,
        "signed_up": 7,
        "description": "Come join us for a friendly football match!",
        "weather_icon": "🌞",
    },
    {
        "name": "Ride to Zurich",
        "date": "2024-10-25 10:15",
        "organizer": "Tanja Musterfrau",
        "location": [47.423, 9.372],
        "capacity": 3,
        "signed_up": 2,
        "description": "Join for a ride from St. Gallen to Zurich!",
        "weather_icon": "☁️",
    },
]

# Function to get weather forecast
def get_weather_forecast(lat, lon, date):
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,temperature_2m_max",
        "timezone": "auto"
    }
    response = requests.get(WEATHER_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        forecast = data['daily']
        return forecast
    else:
        st.error("Could not fetch weather data.")
        return None

# Streamlit layout
st.title("Community Event Organizer - St. Gallen")
st.text_input("Search...", key="search")

# Initialize map
m = folium.Map(location=ST_GALLEN_LOCATION, zoom_start=13)

# Add event markers to the map
for event in events:
    # Display event details in a popup
    event_html = f"""
    <strong>{event['name']}</strong><br>
    Date: {event['date']}<br>
    Organizer: {event['organizer']}<br>
    {event['weather_icon']} Weather: Clear<br>
    Description: {event['description']}<br>
    <div style="margin-top: 5px; font-size: small;">
        Capacity: {event['signed_up']}/{event['capacity']}
        <div style="width: 100%; background-color: #ddd;">
            <div style="width: {int(event['signed_up'] / event['capacity'] * 100)}%; height: 8px; background-color: green;"></div>
        </div>
    </div>
    """

    # Add marker
    folium.Marker(
        location=event["location"],
        popup=folium.Popup(event_html, max_width=300),
        tooltip=event["name"],
        icon=folium.Icon(color="green" if event["signed_up"] < event["capacity"] else "red")
    ).add_to(m)

# Render map in Streamlit
st_folium(m, width=700, height=500)

