import streamlit as st
import folium
from streamlit_folium import st_folium
import sqlite3
from datetime import datetime
import random

# Database setup
def setup_database():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()

    # Create the events table if it doesn't exist
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

    # Create the user_joined_events table to track joined events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_joined_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            event_name TEXT,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Insert a new event into the database
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

# Update participants count in the database
def update_participants(event_id, new_participants):
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET participants = ? WHERE id = ?", (new_participants, event_id))
    conn.commit()
    conn.close()

# Add an event to the user's joined events
def join_event(event_id, event_name):
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_joined_events (event_id, event_name) VALUES (?, ?)
    ''', (event_id, event_name))
    conn.commit()
    conn.close()

# Fetch all joined events
def fetch_joined_events():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT event_id, event_name FROM user_joined_events")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1]} for row in rows]

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
            <a href="?join_event={event['id']}">Join Event</a>
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

# Setup the database
setup_database()

# Fetch events and joined events
events = fetch_events()
joined_events = fetch_joined_events()

# Handle Join Events
params = st.experimental_get_query_params()
if "join_event" in params:
    event_id = int(params["join_event"][0])
    for event in events:
        if event["id"] == event_id and event["participants"] < event["max_participants"]:
            event["participants"] += 1
            update_participants(event_id, event["participants"])
            join_event(event["id"], event["name"])
    st.experimental_set_query_params()

# Search Bar
search_query = st.text_input("Search events", "")

# Display Map
map_ = render_map(events, search_query=search_query)
st_folium(map_, width=700)

# List of all events next to the map
st.subheader("All Events")
for event in events:
    st.write(f"- **{event['name']}** (by {event['organizer']}, at {event['time']})")

# Display Joined Events
st.subheader("Your Joined Events")
if joined_events:
    for event in joined_events:
        st.write(f"- {event['name']}")
else:
    st.write("You have not joined any events yet.")



