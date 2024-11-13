import streamlit as st
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime, time
import random

# Initialize events list with sample data
events = [
    {
        "name": "Football Match",
        "organizer": "John Doe",
        "location": [47.4239, 9.3748],
        "date": "2024-11-20",
        "time": "15:00",
        "description": "Join us for a friendly football match!",
        "participants": 15,
        "max_participants": 20,
        "event_type": "outdoor",
        "cancellation_prob": 30,
        "weather": {"forecast": "Sunny", "temp": 20}
    },
    {
        "name": "Study Group",
        "organizer": "Jane Smith",
        "location": [47.4245, 9.3769],
        "date": "2024-11-22",
        "time": "10:00",
        "description": "Group study session for exams.",
        "participants": 8,
        "max_participants": 10,
        "event_type": "indoor",
        "cancellation_prob": 5,
        "weather": {"forecast": "Cloudy", "temp": 18}
    }
]

# List to store events user has joined
user_enrolled_events = []

# Function to render the map with events and search functionality
def render_map(search_query=""):
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)

    # Filter events based on search query
    filtered_events = [
        event for event in events
        if search_query.lower() in event["name"].lower() or search_query.lower() in event["description"].lower()
    ]

    # Display each event on the map
    for event in filtered_events:
        # Create participant and cancellation probability bars
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(3, 3))
        ax1.barh([""], [event["max_participants"]], color="grey", edgecolor="black")
        ax1.barh([""], [event["participants"]], color="green", edgecolor="black")
        ax1.text(event["participants"], 0, f"{event['participants']}/{event['max_participants']}", va='center')
        ax1.set_xlim(0, event["max_participants"])
        ax1.set_title("Participants", fontsize=10)
        ax1.axis("off")

        ax2.barh([""], [event["cancellation_prob"]], color="red", edgecolor="black")
        ax2.text(event["cancellation_prob"], 0, f"{event['cancellation_prob']}%", va='center')
        ax2.set_xlim(0, 100)
        ax2.set_title("Cancellation Probability", fontsize=10)
        ax2.axis("off")

        # Convert matplotlib graph to image
        graph_image = BytesIO()
        plt.tight_layout()
        plt.savefig(graph_image, format="png")
        plt.close(fig)
        graph_image_base64 = base64.b64encode(graph_image.getvalue()).decode("utf-8")

        # Popup content with participant and cancellation info
        popup_content = f"""
        <div style="font-family:Arial; width:200px;">
            <h4>{event['name']}</h4>
            <p><b>Organized by:</b> {event['organizer']}</p>
            <p><b>Date:</b> {event['date']} at {event['time']}</p>
            <p><b>Description:</b> {event['description']}</p>
            <p><b>Weather:</b> {event['weather']['forecast']} ({event['weather']['temp']}°C)</p>
            <img src="data:image/png;base64,{graph_image_base64}" width="100%">
            <form action="" method="post">
                <button type="submit" style="margin-top:10px;">Join Event</button>
            </form>
        </div>
        """

        folium.Marker(
            location=event["location"],
            icon=folium.Icon(color="blue", icon="info-sign"),
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=event["name"]
        ).add_to(base_map)

    return base_map

# Streamlit app layout
st.title("Community-Bridger")
st.header("Connect with fellows around you!")

# Event search bar
search_query = st.text_input("Search events", "")

# Display the map
map_ = render_map(search_query=search_query)
st_data = st_folium(map_, width=700)

# Form to add a new event
with st.form("add_event_form"):
    st.subheader("Add a New Event")
    name = st.text_input("Event Name")
    organizer = st.text_input("Organizer Name")
    description = st.text_area("Event Description")
    date = st.date_input("Event Date", value=datetime.now())
    time = st.time_input("Event Time", value=datetime.now().time())
    max_participants = st.number_input("Max Participants", min_value=1, step=1)
    event_type = st.selectbox("Event Type", ["outdoor", "indoor"])

    location_choice = st.radio("Select event location", ["Click on Map", "Enter Address"])
    if location_choice == "Click on Map":
        location = st_data["last_clicked"] if st_data else None
    else:
        address = st.text_input("Event Address (Street and Number)")
        location = {"lat": 47.4245, "lng": 9.3769}  # Placeholder for actual geolocation API

    if st.form_submit_button("Add Event"):
        if not location:
            st.warning("Please select a location on the map or enter an address for the event.")
        else:
            new_event = {
                "name": name,
                "organizer": organizer,
                "location": [location["lat"], location["lng"]],
                "date": date.strftime("%Y-%m-%d"),
                "time": time.strftime("%H:%M"),
                "description": description,
                "participants": 0,
                "max_participants": max_participants,
                "event_type": event_type,
                "cancellation_prob": random.randint(5, 30),
                "weather": {"forecast": "Cloudy", "temp": random.randint(15, 25)}  # Placeholder weather
            }
            events.append(new_event)
            st.success(f"Event '{name}' added successfully!")
            st.experimental_rerun()

# Display user's joined events
st.subheader("Your Joined Events")
if user_enrolled_events:
    for enrolled_event in user_enrolled_events:
        st.write(f"- {enrolled_event['name']} on {enrolled_event['date']} at {enrolled_event['time']}")
else:
    st.write("You have not joined any events yet.")
