# Import necessary libraries
import streamlit as st
import folium
from streamlit_folium import st_folium

# Sample data for events
events = [
    {
        "name": "Football Match",
        "date": "31st October, 14:15",
        "organizer": "Max Mustermann",
        "capacity": 20,
        "signed_up": 7,
        "description": "Friendly football match open to all!",
        "location": [47.425, 9.376],  # Coordinates in St. Gallen
        "weather": "Sunny, 18°C",
        "cancellation_probability": 10  # % chance of cancellation
    },
    {
        "name": "Ride to Zurich",
        "date": "25th October, 10:15",
        "organizer": "Tanja Musterfrau",
        "capacity": 3,
        "signed_up": 2,
        "description": "Carpool to Zurich - 1 seat left!",
        "location": [47.431, 9.378],  # Slightly different coordinates
        "weather": "Cloudy, 15°C",
        "cancellation_probability": 5  # % chance of cancellation
    }
]

# Streamlit app title
st.title("Community Event App")

# Create a Folium map centered on St. Gallen
m = folium.Map(location=[47.4239, 9.3748], zoom_start=13)

# Add markers for each event
for event in events:
    # HTML content for the popup
    popup_html = f"""
    <b>{event['name']}</b><br>
    <i>{event['date']}</i><br>
    Organizer: {event['organizer']}<br>
    Capacity: {event['signed_up']}/{event['capacity']}<br>
    Weather: {event['weather']}<br>
    Cancellation Probability: {event['cancellation_probability']}%<br>
    Description: {event['description']}
    """
    # Create the popup
    popup = folium.Popup(popup_html, max_width=300)
    
    # Add a marker with the popup
    folium.Marker(
        location=event["location"],
        popup=popup,
        tooltip=event["name"],
        icon=folium.Icon(color="blue" if event["cancellation_probability"] < 20 else "red", icon="info-sign")
    ).add_to(m)

# Display the map in Streamlit
st_folium(m, width=700, height=500)

# Optional: Add a sidebar for filtering events or other interactive features
st.sidebar.title("Event Filters")
st.sidebar.write("This is a placeholder sidebar. You can add filters or search here.")

