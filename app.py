pip install folium streamlit-folium

# weather_map_app_free.py
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime

# Open-Meteo API endpoint
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Fetch weather forecast data from Open-Meteo
def get_weather_forecast(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "timezone": "auto"  # Automatically adjust the timezone based on location
    }
    response = requests.get(FORECAST_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch data. Please try again later.")
        return None

# Streamlit App Layout
st.title("Global Weather Forecast Map (Free API)")
st.write("Explore the map to select a location and view the daily weather forecast.")

# Set up Folium map in Streamlit
m = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodbpositron")

# Add a click handler to the map
map_data = st_folium(m, width=700, height=500)

if map_data and map_data["last_clicked"]:
    # Get the coordinates of the last clicked location
    lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
    st.write(f"**Selected Location:** {lat:.2f}, {lon:.2f}")
    
    # Fetch and display weather forecast
    forecast_data = get_weather_forecast(lat, lon)
    if forecast_data:
        st.subheader("5-Day Weather Forecast")

        # Extract daily forecast data
        daily_data = forecast_data["daily"]
        dates = daily_data["time"]
        temps_max = daily_data["temperature_2m_max"]
        temps_min = daily_data["temperature_2m_min"]
        precip = daily_data["precipitation_sum"]
        wind_speeds = daily_data["windspeed_10m_max"]
        
        # Display the forecast data
        for i in range(len(dates)):
            date = datetime.strptime(dates[i], "%Y-%m-%d").strftime("%A, %B %d")
            max_temp = temps_max[i]
            min_temp = temps_min[i]
            precipitation = precip[i]
            wind_speed = wind_speeds[i]
            
            st.write(f"**{date}**")
            st.write(f"Max Temperature: {max_temp}°C, Min Temperature: {min_temp}°C")
            st.write(f"Precipitation: {precipitation} mm")
            st.write(f"Wind Speed: {wind_speed} m/s")
            st.write("---")  # Divider between days

