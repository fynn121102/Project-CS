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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_enrollments (
            user_id TEXT,
            event_id INTEGER
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

# Update participants count in the database
def update_participants(event_id, new_participants):
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET participants = ? WHERE id = ?", (new_participants, event_id))
    conn.commit()
    conn.close()

# Fetch user enrolled events
def fetch_user_enrolled_events(user_id):
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT event_id FROM user_enrollments WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]

# Enroll a user in an event
def enroll_user_in_event(user_id, event_id):
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_enrollments (user_id, event_id) VALUES (?, ?)", (user_id, event_id))
    conn.commit()
    conn.close()

# Unenroll a user from an event
def unenroll_user_from_event(user_id, event_id):
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_enrollments WHERE user_id = ? AND event_id = ?", (user_id, event_id))
    conn.commit()
    conn.close()

# Render map with events
def render_map(events, user_enrolled_events, search_query=""):
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
        if event["id"] in user_enrolled_events:
            action_button = f'<button onclick="window.location.href=\'?leave_event={event["id"]}\'">Leave Event</button>'
        else:
            action_button = f'<button onclick="window.location.href=\'?join_event={event["id"]}\'">Join Event</button>'
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

# App setup
st.title("Community-Bridger")
st.header("Connect with fellows around you!")

# Setup the database
setup_database()

# Fetch events
events = fetch_events()

# User's enrolled events (for this session only)
user_enrolled_events = []

# Handle user input (username/user_id)
user_input = st.text_input("Enter your username", value="user1")

# Check if the user input is a valid number (user_id)
if user_input.isdigit():
    user_id = int(user_input)
else:
    user_id = user_input  # Use the username as the user ID if not a number
    st.error("Please enter a valid user ID (integer) or username.")

# Proceed if the user_id is valid
if user_id:
    # Fetch enrolled events for the user
    user_enrolled_events = fetch_user_enrolled_events(user_id)

    # Handle Join/Leave Events
    params = st.experimental_get_query_params()
    if "join_event" in params:
        event_id = int(params["join_event"][0])
        if event_id not in user_enrolled_events:
            enroll_user_in_event(user_id, event_id)
            user_enrolled_events.append(event_id)
            event = next((event for event in events if event["id"] == event_id), None)
            if event:
                event["participants"] += 1
                update_participants(event_id, event["participants"])
        st.experimental_set_query_params()  # Refresh the page after joining

    if "leave_event" in params:
        event_id = int(params["leave_event"][0])
        if event_id in user_enrolled_events:
            unenroll_user_from_event(user_id, event_id)
            user_enrolled_events.remove(event_id)
            event = next((event for event in events if event["id"] == event_id), None)
            if event:
                event["participants"] -= 1
                update_participants(event_id, event["participants"])
        st.experimental_set_query_params()  # Refresh the page after leaving

    # Search Bar
    search_query = st.text_input("Search events", "")

    # Display Map
    map_ = render_map(events, user_enrolled_events, search_query=search_query)
    st_folium(map_, width=700)

    # Display Events List
    st.write("Upcoming Events:")
    for event in events:
        if event["id"] not in user_enrolled_events:
            join_leave_button = st.button(f"Join {event['name']}", key=f"join_{event['id']}")
            if join_leave_button:
                enroll_user_in_event(user_id, event["id"])
                update_participants(event["id"], event["participants"] + 1)
                st.experimental_rerun()  # Refresh the page after joining
        else:
            leave_button = st.button(f"Leave {event['name']}", key=f"leave_{event['id']}")
            if leave_button:
                unenroll_user_from_event(user_id, event["id"])
                update_participants(event["id"], event["participants"] - 1)
                st.experimental_rerun()  # Refresh the page after leaving
else:
    st.write("Please enter a valid user ID to proceed.")

