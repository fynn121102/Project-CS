# Import necessary libraries
import streamlit as st
import folium
from streamlit_folium import st_folium

# Set the location for the map (St. Gallen, Switzerland)
ST_GALLEN_LOCATION = [47.4239, 9.3748]

# Streamlit app title
st.title("Simple Map with Folium")

# Initialize a Folium map centered on St. Gallen
m = folium.Map(location=ST_GALLEN_LOCATION, zoom_start=13)

# Add a marker at the specified location
folium.Marker(
    location=ST_GALLEN_LOCATION,
    popup="St. Gallen",
    tooltip="Click for more info",
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(m)

# Render the map in Streamlit using st_folium
st_folium(m, width=700, height=500)
