import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime
import random

# Hardcode data
events = [
    {
        "name": "Football Match",
        "organizer": "Cristiano Ronaldo",
        "location": [47.4239, 9.3748],
        "date": "2024-11-20",
        "time": "15:00",
        "description": "Join us for a friendly football match!",
        "participants": 15,
        "max_participants": 20,
        "event_type": "outdoor",
        "cancellation_prob": 30,
        "weather": {"forecast": "Sunny 🌞", "temp": 12}
    },
    {
        "name": "Study Group",
        "organizer": "Bill Gates",
        "location": [47.4245, 9.3769],
        "date": "2024-11-22",
        "time": "10:00",
        "description": "Group study session for computer science exams.",
        "participants": 8,
        "max_participants": 10,
        "event_type": "indoor",
        "cancellation_prob": 5,
        "weather": {"forecast": "Cloudy ☁️", "temp": 7}
    },
    {
        "name": "Yoga in the Park",
        "organizer": "Pamela Reif",
        "location": [47.4215, 9.3740],
        "date": "2024-11-25",
        "time": "08:00",
        "description": "Start your day with a refreshing yoga session.",
        "participants": 10,
        "max_participants": 15,
        "event_type": "outdoor",
        "cancellation_prob": 10,
        "weather": {"forecast": "Sunny 🌞", "temp": 8}
    },
    {
        "name": "Tech Meetup",
        "organizer": "Elon Musk",
        "location": [47.4270, 9.3765],
        "date": "2024-11-26",
        "time": "18:00",
        "description": "Discuss the latest in tech and innovation.",
        "participants": 20,
        "max_participants": 25,
        "event_type": "indoor",
        "cancellation_prob": 0,
        "weather": {"forecast": "Partly Cloudy ⛅", "temp": 10}
    },
    {
        "name": "Painting Workshop",
        "organizer": "Leonardo da Vinci",
        "location": [47.4250, 9.3730],
        "date": "2024-11-28",
        "time": "14:00",
        "description": "Express your creativity with colors!",
        "participants": 5,
        "max_participants": 10,
        "event_type": "indoor",
        "cancellation_prob": 5,
        "weather": {"forecast": "Cloudy ☁️", "temp": 9}
    },
    {
        "name": "Cooking Class",
        "organizer": "Gordon Ramsay",
        "location": [47.4265, 9.3720],
        "date": "2024-11-30",
        "time": "17:00",
        "description": "Learn to cook a delicious three-course meal.",
        "participants": 12,
        "max_participants": 15,
        "event_type": "indoor",
        "cancellation_prob": 2,
        "weather": {"forecast": "Cloudy ☁️", "temp": 7}
    },
    {
        "name": "Hiking Trip",
        "organizer": "Andre Schürrle",
        "location": [47.4200, 9.3775],
        "date": "2024-12-01",
        "time": "09:00",
        "description": "Explore the beautiful trails around St. Gallen.",
        "participants": 8,
        "max_participants": 12,
        "event_type": "outdoor",
        "cancellation_prob": 15,
        "weather": {"forecast": "Partly Cloudy ⛅", "temp": 6}
    },
    {
        "name": "Book Club",
        "organizer": "J.K. Rowling",
        "location": [47.4248, 9.3752],
        "date": "2024-12-03",
        "time": "16:00",
        "description": "Discuss the latest bestseller with fellow readers.",
        "participants": 6,
        "max_participants": 10,
        "event_type": "indoor",
        "cancellation_prob": 0,
        "weather": {"forecast": "Cloudy ☁️", "temp": 8}
    },
    {
        "name": "Chess Tournament",
        "organizer": "Magnus Carlsen",
        "location": [47.4232, 9.3745],
        "date": "2024-12-05",
        "time": "10:00",
        "description": "Compete with the best chess players in the city.",
        "participants": 14,
        "max_participants": 16,
        "event_type": "indoor",
        "cancellation_prob": 0,
        "weather": {"forecast": "Cloudy ☁️", "temp": 7}
    },
    {
        "name": "Photography Walk",
        "organizer": "Ansel Adams",
        "location": [47.4228, 9.3738],
        "date": "2024-12-08",
        "time": "15:00",
        "description": "Capture the beauty of St. Gallen with your camera.",
        "participants": 9,
        "max_participants": 12,
        "event_type": "outdoor",
        "cancellation_prob": 20,
        "weather": {"forecast": "Sunny 🌞", "temp": 10}
    }
]

user_enrolled_events = []

# Geocoding function using OpenCage Geocoder API
def geocode_address(address, api_key="YOUR_OPENCAGE_API_KEY"):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            coordinates = results[0]['geometry']
            return [coordinates['lat'], coordinates['lng']]
    return None

# Render map with events
def render_map(search_query=""):
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)
    filtered_events = [
        event for event in events
        if search_query.lower() in event["name"].lower() or search_query.lower() in event["description"].lower()
    ]
    for idx, event in enumerate(filtered_events):
        participants_ratio = event["participants"] / event["max_participants"]
        participant_bar = f'<div style="width: 100%; background-color: grey; height: 10px; position: relative;">' \
                          f'<div style="width: {participants_ratio * 100}%; background-color: green; height: 10px;"></div>' \
                          f'</div>'
        cancellation_prob_bar = f'<div style="width: 100%; background-color: grey; height: 10px; position: relative;">' \
                                f'<div style="width: {event["cancellation_prob"]}%; background-color: red; height: 10px;"></div>' \
                                f'</div>'
        if event in user_enrolled_events:
            action_button = f'<button onclick="window.location.href=\'?leave_event={idx}\'">Leave Event</button>'
        else:
            action_button = f'<button onclick="window.location.href=\'?join_event={idx}\'">Join Event</button>'
        popup_content = f"""
        <div style="font-family:Arial; width:250px;">
            <h4>{event['name']}</h4>
            <p><b>Organized by:</b> {event['organizer']}</p>
            <p><b>Date:</b> {event['date']} at {event['time']}</p>
            <p><b>Description:</b> {event['description']}</p>
            <p><b>Weather:</b> {event['weather']['forecast']} ({event['weather']['temp']}°C)</p>
            <p><b>Participants:</b></p>
            {participant_bar}
            <p>{event['participants']} / {event['max_participants']}</p>
            <p><b>Cancellation Probability:</b> {event['cancellation_prob']}%</p>
            {cancellation_prob_bar}
            {action_button}
        </div>
        """
        folium.Marker(
            location=event["location"],
            icon=folium.Icon(color="blue", icon="info-sign"),
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=event["name"]
        ).add_to(base_map)
    return base_map

# Streamlit layout
st.title("JoinMy")
st.header("Connect with fellows around you!")
search_query = st.text_input("Search events", "")

# Join/Leave Event Handling
params = st.experimental_get_query_params()
if "join_event" in params:
    event_idx = int(params["join_event"][0])
    event = events[event_idx]
    if event not in user_enrolled_events and event["participants"] < event["max_participants"]:
        event["participants"] += 1
        user_enrolled_events.append(event)
    st.experimental_set_query_params()

if "leave_event" in params:
    event_idx = int(params["leave_event"][0])
    event = events[event_idx]
    if event in user_enrolled_events:
        event["participants"] -= 1
        user_enrolled_events.remove(event)
    st.experimental_set_query_params()

# Display Map
map_ = render_map(search_query=search_query)
st_data = st_folium(map_, width=700)

# Add a New Event
with st.form("add_event_form"):
    st.subheader("Add a New Event")
    name = st.text_input("Event Name")
    organizer = st.text_input("Organizer Name")
    description = st.text_area("Event Description")
    date = st.date_input("Event Date", value=datetime.now())
    time = st.time_input("Event Time", value=datetime.now().time())
    max_participants = st.number_input("Max Participants", min_value=1, step=1)
    event_type = st.selectbox("Event Type", ["outdoor", "indoor"])
    address = st.text_input("Event Address (Street and Number)")

    if st.form_submit_button("Add Event"):
        if address:
            location = geocode_address(address)
            if location:
                new_event = {
                    "name": name,
                    "organizer": organizer,
                    "location": location,
                    "date": date.strftime("%Y-%m-%d"),
                    "time": time.strftime("%H:%M"),
                    "description": description,
                    "participants": 0,
                    "max_participants": max_participants,
                    "event_type": event_type,
                    "cancellation_prob": random.randint(5, 30),
                    "weather": {"forecast": "Partly Cloudy ⛅", "temp": random.randint(15, 25)}
                }
                events.append(new_event)
                st.success(f"Event '{name}' added successfully!")
                st.experimental_rerun()
            else:
                st.error("Could not find location. Please try again.")
        else:
            st.error("Address is required.")

# User's Joined Events
st.subheader("Your Joined Events")
if user_enrolled_events:
    for event in user_enrolled_events:
        st.write(f"- {event['name']} on {event['date']} at {event['time']}")
else:
    st.write("You have not joined any events yet.")
