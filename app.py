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

    return [row[0] for row in rows]  # Return only the event IDs

# Update participants count in the events table
def update_participants(event_id, new_participants):
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET participants = ? WHERE id = ?", (new_participants, event_id))
    conn.commit()
    conn.close()

# Handle Join Event Action
def handle_join_event(user_id, event_id):
    events = fetch_events()
    user_events = fetch_user_events(user_id)

    for event in events:
        if event["id"] == event_id:
            if event_id in user_events:
                st.warning("You have already joined this event.")
            elif event["participants"] >= event["max_participants"]:
                st.error("This event is already full!")
            else:
                event["participants"] += 1
                update_participants(event_id, event["participants"])
                insert_user_event(user_id, event_id)
                st.success(f"Successfully joined '{event['name']}'!")
            break

    st.experimental_rerun()

# Render map with events
def render_map(events, user_id):
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)
    for event in events:
        popup_content = f"""
        <div>
            <h4>{event['name']}</h4>
            <p><b>Organizer:</b> {event['organizer']}</p>
            <p><b>Date:</b> {event['date']} at {event['time']}</p>
            <p><b>Description:</b> {event['description']}</p>
        </div>
        """
        folium.Marker(
            location=event["location"],
            icon=folium.Icon(color="blue"),
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(base_map)
    return base_map

# Display All Events
def display_events(events, user_id):
    user_events = fetch_user_events(user_id)
    st.subheader("Available Events")
    for event in events:
        st.markdown(f"""
        **Name**: {event['name']}  
        **Date**: {event['date']}  
        **Time**: {event['time']}  
        **Organizer**: {event['organizer']}  
        **Description**: {event['description']}  
        """)
        if event["id"] in user_events:
            st.button("Already Joined", disabled=True, key=f"joined_{event['id']}")
        elif event["participants"] >= event["max_participants"]:
            st.button("Event Full", disabled=True, key=f"full_{event['id']}")
        else:
            if st.button(f"Join '{event['name']}'", key=f"join_{event['id']}"):
                handle_join_event(user_id, event["id"])

# App setup
st.title("Community-Bridger")
st.header("Connect with fellows around you!")

setup_events_database()
setup_user_events_database()

if "user_id" not in st.session_state:
    st.session_state.user_id = random.randint(1, 1000)

events = fetch_events()

map_ = render_map(events, st.session_state.user_id)
st_folium(map_, width=700)

display_events(events, st.session_state.user_id)
