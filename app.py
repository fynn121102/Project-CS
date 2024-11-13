import streamlit as st
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
import random

# Initial data for events
events = [
    {
        "name": "Football Match",
        "organizer": "John Doe",
        "location": [47.4239, 9.3748],
        "date": "2024-11-20",
        "description": "Join us for a friendly football match!",
        "participants": 15,
        "max_participants": 20,
        "event_type": "outdoor",
        "cancellation_prob": 10  # placeholder for demonstration
    },
    {
        "name": "Study Group",
        "organizer": "Jane Smith",
        "location": [47.4245, 9.3769],
        "date": "2024-11-22",
        "description": "Group study session for exams.",
        "participants": 8,
        "max_participants": 10,
        "event_type": "indoor",
        "cancellation_prob": 0  # placeholder for demonstration
    }
]

# Function to create and render the map
def render_map(search_query=""):
    # Create the base map
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)

    # Filter events based on search query
    filtered_events = [
        event for event in events
        if search_query.lower() in event["name"].lower() or search_query.lower() in event["description"].lower()
    ]

    # Loop over events and add markers with popups
    for event in filtered_events:
        # Generate participant graph
        fig, ax = plt.subplots()
        ax.bar(["Joined", "Max Capacity"], [event["participants"], event["max_participants"]], color=["green", "grey"])
        ax.set_title("Participants")
        ax.set_ylabel("Count")

        # Save graph to a BytesIO object
        graph_image = BytesIO()
        plt.savefig(graph_image, format="png")
        plt.close(fig)
        graph_image_base64 = base64.b64encode(graph_image.getvalue()).decode("utf-8")  # Encode to base64 string

        # Create popup content with the event details and embedded image
        popup_content = f"""
        <div style="width:200px;">
            <h4>{event['name']}</h4>
            <p><b>Organized by:</b> {event['organizer']}</p>
            <p><b>Date:</b> {event['date']}</p>
            <p><b>Description:</b> {event['description']}</p>
            <p><b>Weather Forecast:</b> 🌤️</p>  <!-- Placeholder emoji -->
            <p><b>Cancellation Probability:</b> {event['cancellation_prob']}%</p>
            <img src="data:image/png;base64,{graph_image_base64}" width="100%">
        </div>
        """

        # Add marker with popup
        folium.Marker(
            location=event["location"],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=event["name"]
        ).add_to(base_map)

    return base_map

# Streamlit app configuration
st.title("Community Bridger")
st.header("Connect with fellows around you!")

# Event search bar
search_query = st.text_input("Search events", "")

# Render the map and display it in Streamlit
map_ = render_map(search_query=search_query)
st_data = st_folium(map_, width=700)

# Form to add new events
with st.form("add_event_form"):
    st.subheader("Add a New Event")
    name = st.text_input("Event Name")
    organizer = st.text_input("Organizer Name")
    description = st.text_area("Event Description")
    date = st.date_input("Event Date", value=datetime.now())
    max_participants = st.number_input("Max Participants", min_value=1, step=1)
    event_type = st.selectbox("Event Type", ["outdoor", "indoor"])
    location = st_data["last_clicked"] if st_data else None  # Get location from map click

    if st.form_submit_button("Add Event"):
        if not location:
            st.warning("Please select a location on the map for the event.")
        else:
            new_event = {
                "name": name,
                "organizer": organizer,
                "location": [location["lat"], location["lng"]],
                "date": date.strftime("%Y-%m-%d"),
                "description": description,
                "participants": 0,
                "max_participants": max_participants,
                "event_type": event_type,
                "cancellation_prob": random.randint(5, 30)  # Random for demo purposes
            }
            events.append(new_event)
            st.success(f"Event '{name}' added successfully!")
            st.experimental_rerun()  # Refresh the app to display the new event

# Notes for users
st.write("Click on a location on the map to set the event's location when adding a new event.")
