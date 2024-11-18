import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, db
import folium
from streamlit_folium import st_folium
import random
from datetime import datetime

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://console.firebase.google.com/project/join-my/database/join-my-default-rtdb/data/~2F?fb_gclid=Cj0KCQiAouG5BhDBARIsAOc08RSkfEvSB4DqIbUON4PJUzZnnotd03Bqiq57vMeJx8WR9jQx7PW_DVQaAu9bEALw_wcB'
    })

# Firebase database references
events_ref = db.reference("events")
user_joined_ref = db.reference("user_joined")

# Initialize user session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# Helper functions
def register_user(email, password):
    """Register a new user."""
    try:
        user = auth.create_user(email=email, password=password)
        st.success(f"User '{email}' registered successfully!")
        return user
    except firebase_admin._auth_utils.EmailAlreadyExistsError:
        st.error("Email already exists. Please log in.")
    except Exception as e:
        st.error(f"Error: {e}")

def login_user(email, password):
    """Log in an existing user."""
    try:
        user = auth.get_user_by_email(email)
        # Here, Firebase Admin SDK doesn't handle password verification.
        # You'd typically implement a separate API endpoint with Firebase Authentication client SDK.
        st.session_state["logged_in"] = True
        st.session_state["user_email"] = email
        st.success(f"Welcome back, {email}!")
    except firebase_admin._auth_utils.UserNotFoundError:
        st.error("User not found. Please register.")
    except Exception as e:
        st.error(f"Error: {e}")

def logout_user():
    """Log out the current user."""
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.success("Logged out successfully!")

def render_map(events, joined_events):
    """Render map with events."""
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)
    for event_key, event in events.items():
        participants_ratio = event["participants"] / event["max_participants"]
        participant_bar = f'<div style="width: 100%; background-color: grey; height: 10px;">' \
                          f'<div style="width: {participants_ratio * 100}%; background-color: green; height: 10px;"></div>' \
                          f'</div>'
        if event_key in joined_events.values():
            action_button = f'<button onclick="window.location.href=\'?leave_event={event_key}\'">Leave Event</button>'
        else:
            action_button = f'<button onclick="window.location.href=\'?join_event={event_key}\'">Join Event</button>'
        popup_content = f"""
        <div style="font-family:Arial; width:250px;">
            <h4>{event['name']}</h4>
            <p><b>Organized by:</b> {event['organizer']}</p>
            <p><b>Date:</b> {event['date']} at {event['time']}</p>
            <p><b>Description:</b> {event['description']}</p>
            <p><b>Participants:</b></p>
            {participant_bar}
            <p>{event['participants']} / {event['max_participants']}</p>
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

# Streamlit app
st.title("Community-Bridger")
st.header("Connect with fellows around you!")

if not st.session_state["logged_in"]:
    # Registration/Login Form
    auth_option = st.radio("Choose an option", ["Log In", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if auth_option == "Register" and st.button("Register"):
        register_user(email, password)
    
    if auth_option == "Log In" and st.button("Log In"):
        login_user(email, password)
else:
    st.sidebar.subheader(f"Logged in as {st.session_state['user_email']}")
    if st.sidebar.button("Log Out"):
        logout_user()

    # Event search
    search_query = st.text_input("Search events", "")

    # Fetch events
    events = fetch_events()
    joined_events = fetch_joined_events()

    # Display map
    map_ = render_map(events, joined_events)
    st_folium(map_, width=700)

    # Add a new event
    with st.form("add_event_form"):
        st.subheader("Add a New Event")
        name = st.text_input("Event Name")
        organizer = st.text_input("Organizer Name")
        description = st.text_area("Event Description")
        date = st.date_input("Event Date", value=datetime.now())
        time = st.time_input("Event Time", value=datetime.now().time())
        max_participants = st.number_input("Max Participants", min_value=1, step=1)
        event_type = st.selectbox("Event Type", ["outdoor", "indoor"])
        location = [47.4239 + random.uniform(-0.01, 0.01), 9.3748 + random.uniform(-0.01, 0.01)]  # Random location for demo
        if st.form_submit_button("Add Event"):
            event_data = {
                "name": name,
                "organizer": organizer,
                "location": location,
                "date": date.strftime("%Y-%m-%d"),
                "time": time.strftime("%H:%M"),
                "description": description,
                "participants": 0,
                "max_participants": max_participants,
                "event_type": event_type
            }
            add_event_to_firebase(event_data)
            st.success(f"Event '{name}' added successfully!")
