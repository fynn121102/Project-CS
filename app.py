import streamlit as st
import folium
from streamlit_folium import st_folium
import sqlite3
from datetime import datetime
import random

# Database setup for events
def setup_events_database():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            name TEXT,
            organizer TEXT,
            location_lat REAL,
            location_lng REAL,
            date TEXT,
            time TEXT,
            description TEXT,
            participants INTEGER,
            max_participants INTEGER,
            event_type TEXT,
            cancellation_prob INTEGER,
            weather_forecast TEXT,
            weather_temp INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Database setup for user event enrollment
def setup_user_events_database():
    conn = sqlite3.connect("user_events.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_events (
            user_id INTEGER,
            event_id INTEGER,
            PRIMARY KEY (user_id, event_id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    ''')
    conn.commit()
    conn.close()

# Insert an event into the database
def insert_event(event):
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (name, organizer, location_lat, location_lng, date, time, description,
                            participants, max_participants, event_type, cancellation_prob, weather_forecast, weather_temp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        event["name"], event["organizer"], event["location"][0], event["location"][1],
        event["date"], event["time"], event["description"], event["participants"],
        event["max_participants"], event["event_type"], event["cancellation_prob"],
        event["weather"]["forecast"], event["weather"]["temp"]
    ))
    conn.commit()
    conn.close()

# Fetch all events from the database
def fetch_events():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()
    conn.close()

    events = []
    for row in rows:
        events.append({
            "id": row[0],
            "name": row[1],
            "organizer": row[2],
            "location": [row[3], row[4]],
            "date": row[5],
            "time": row[6],
            "description": row[7],
            "participants": row[8],
            "max_participants": row[9],
            "event_type": row[10],
            "cancellation_prob": row[11],
            "weather": {"forecast": row[12], "temp": row[13]}
        })
    return events

# Insert a user's event participation into the database
def insert_user_event(user_id, event_id):
    conn = sqlite3.connect("user_events.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_events (user_id, event_id)
        VALUES (?, ?)
    ''', (user_id, event_id))
    conn.commit()
    conn.close()

# Fetch a user's joined events
def fetch_user_events(user_id):
    conn = sqlite3.connect("user_events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT event_id FROM user_events WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]  # Return event IDs

# Update participants count in the events table
def update_participants(event_id, new_participants):
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET participants = ? WHERE id = ?", (new_participants, event_id))
    conn.commit()
    conn.close()

# Render map with events
def render_map(events, search_query=""):
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)
    filtered_events = [
        event for event in events
        if search_query.lower() in event["name"].lower() or search_query.lower() in event["description"].lower()
    ]
    for event in filtered_events:
        participants_ratio = event["participants"] / event["max_participants"]
        participant_bar = f'<div style="width: 100%; background-color: grey; height: 10px;">' \
                          f'<div style="width: {participants_ratio * 100}%; background-color: green; height: 10px;"></div>' \
                          f'</div>'
        cancellation_prob_bar = f'<div style="width: 100%; background-color: grey; height: 10px;">' \
                                f'<div style="width: {event["cancellation_prob"]}%; background-color: red; height: 10px;"></div>' \
                                f'</div>'
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
        </div>
        """
        folium.Marker(
            location=event["location"],
            icon=folium.Icon(color="blue", icon="info-sign"),
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=event["name"]
        ).add_to(base_map)
    return base_map

# App setup
st.title("Community-Bridger")
st.header("Connect with fellows around you!")

# Setup the databases
setup_events_database()
setup_user_events_database()

# Fetch events
events = fetch_events()

# User session handling (simulating a user)
if "user_id" not in st.session_state:
    st.session_state.user_id = random.randint(1, 1000)  # Simulate a user ID

# Handle Join Event
if "join_event_id" in st.session_state:
    event_id = st.session_state.pop("join_event_id")
    user_events = fetch_user_events(st.session_state.user_id)

    if event_id not in user_events:
        for event in events:
            if event["id"] == event_id and event["participants"] < event["max_participants"]:
                event["participants"] += 1
                update_participants(event_id, event["participants"])
                insert_user_event(st.session_state.user_id, event_id)  # Insert user-event relation
                st.success(f"Joined event '{event['name']}' successfully!")
                st.experimental_rerun()

# Search Bar
search_query = st.text_input("Search events", "")

# Display Map
map_ = render_map(events, search_query=search_query)
st_folium(map_, width=700)

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
    location_lat = st.number_input("Latitude", format="%.6f")
    location_lng = st.number_input("Longitude", format="%.6f")
    cancellation_prob = random.randint(5, 30)
    weather_forecast = random.choice(["Sunny 🌞", "Cloudy ☁️", "Partly Cloudy ⛅"])
    weather_temp = random.randint(5, 20)

    if st.form_submit_button("Add Event"):
        if name and organizer and description and location_lat and location_lng:
            new_event = {
                "name": name,
                "organizer": organizer,
                "location": [location_lat, location_lng],
                "date": date.strftime("%Y-%m-%d"),
                "time": time.strftime("%H:%M"),
                "description": description,
                "participants": 0,
                "max_participants": max_participants,
                "event_type": event_type,
                "cancellation_prob": cancellation_prob,
                "weather": {"forecast": weather_forecast, "temp": weather_temp}
            }
            try:
                insert_event(new_event)
                st.success(f"Event '{name}' added successfully!")
                st.experimental_rerun()  # Reload the page to show updated events
            except Exception as e:
                st.error(f"Error adding event: {e}")
        else:
            st.error("Please fill in all fields!")

# Display all Events next to the map
st.subheader("All Events")
for event in events:
    st.write(f"- {event['name']} | {event['date']} | {event['time']} | Organized by {event['organizer']}")

# Display Joined Events
st.subheader("Your Joined Events")
user_events = fetch_user_events(st.session_state.user_id)
if user_events:
    for event_id in user_events:
        event = next((e for e in events if e["id"] == event_id), None)
        if event:
            st.write(f"- {event['name']} on {event['date']} at {event['time']} (Organized by {event['organizer']})")
else:
    st.write("You have not joined any events yet.")
