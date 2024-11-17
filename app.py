import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
import random
from datetime import datetime

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQCxQgO+3CAngU2F\n7Q7Fq0ng2PCL+ONWyo2JLIZWRNZhlzCmfYZZH2XCfRycRKpsjAq2WZ5yde7DYS91\ns4lqaORip9olvJwrd94JE/Zj+ME64TpZFKRNKP4I1ZuzH/hPwhicz97mxwIuKLsl\nhtZv65813n8rRvXo37X6h2tNtyJ89JhgzvCC11v6L31SuQ2/8bVsQPhUBQO60mPQ\nqhoy5rlqQUhrdXgTycvVbHWzXAcpEV8jHV2ydR0Vuva2pOlV2TAhgoLcUHVWeL62\nSgW8ouToWKalqm1RhBJi/tK0YqhYLLUYrw/y8Y9neyL/JGJMDMtLts5EsiKcszdw\nQmzOss/tAgMBAAECgf9Sp2TZgZViPXMpcqmmRWlS2uD+MuLOH+FLuC1eMoD2siK8\nnTWq8Rgp/vHA5TzDqS62dvX+paN6lAkr9ChcLiH3DLTks+biTbWOWDVn1p5L5BoA\n+nvl5u6Hr4ucsgzqIwAmGtAaVxS8/yixHFH8GmjLvFOfdgWPmt3hBDP9PqKm3gDY\n3cKQN0C8VbQEMN/SoCk/QI0FJz5OqlNfZqGquLAYZbmcpo6Ow1ZwqFnmXeJMAYtb\nLkoP85mRrTM4/mgEV9Zmu72PJi34rEG27mOOumJm0WQd8B2gjgzI1HhlDVf9rzbh\nl3ZBV3O0G933TmIbwKIJDNgMDJ40Vohcp0q+mXMCgYEA+Zx7JfCpaPjD38oyFxYs\nvC6kzkS4zHTxzqdU75E9ruy7jOAMocnPOTZU3zop2eMfnuPhWa9e0Oedi84fbpWu\nh0j4iXS3QqPWDXRgrA/S/uQ0KX0SGw7Sn61BjdSThsU0vwE7XWHU5FKMkI8eVdHv\n3cH+wbTR7Wfvy2mHlS4A37MCgYEAtct0f6mwWnU51iueytH00gpRfdFsloQ1mL/n\nqWp9qIvHa3VujMYe69r1FPjvlkUd0uzJ75VGiQiMQAYxgpReffb5fFehpyi7LWzr\nsiR+XAEYHPboE4XtcLWEt3V5N9U1tEtaqZYkjejeQEWDVjLQCzwgdZ/QHrzvFx5a\nJgqOwd8CgYBV665cRfYaox7RhsktNz3Y3Plv4yn1fv/JUcIj4MvpzaVVfb37ZvtE\nx1X5rQzA6rR0vh5Q/9PUdxW9DQu2xiFYgh7DOgDnGHxTD09DiwLnKGhoK5wy4ixQ\nOJRLHPRXPMTGRsdHgqiEm4G1NP6NLgGyRNfLl9F3NgLN8xpvmHFGjwKBgE3DpCff\n7GIldwIYUqqruTAH3egWJ38TOuIGZRBhTzND56Ad8ZYiQaPeW6wG+GWtVx6cz5y+\nnBeOIoBYpeEXmnwDo6D+01Vv5PF/gCsJ1UuB5FCvhYKkbXcjDoxzodCyUXC4MyYL\n5cMWc8vGcHH09m134OKv5BTh+NxIzYMsTPi9AoGBAOjsbHfKXZqvl9VWTtjE659y\ndoGZWIlgToaZ7CRDXbXash2GauMKoJXFXbQ0I0U6QLuWojXNBuRPaRKCFqDrTg+4\n0GWfgar4To9c8iqUA1yIvKpcI0fgfGBJlK6s9Rnl8s0ro7q5bKACuw93brtEHo7K\n5JNNwMOncYF6UjIzofb8\n-----END PRIVATE KEY-----\n")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://community-bridger-default-rtdb.europe-west1.firebasedatabase.app/'  # Replace with your Firebase DB URL
    })

# Firebase database references
events_ref = db.reference("events")
user_joined_ref = db.reference("user_joined")
names_ref = db.reference("names")

# Fetch events from Firebase
def fetch_events():
    return events_ref.get() or []

# Fetch joined events
def fetch_joined_events():
    return user_joined_ref.get() or {}

# Save a name to Firebase
def save_name(name):
    names_ref.push(name)

# Fetch all saved names
def fetch_names():
    return names_ref.get() or {}

# Add an event to Firebase
def add_event_to_firebase(event_data):
    events_ref.push(event_data)

# Join an event
def join_event(event_key):
    event_data = events_ref.child(event_key).get()
    if event_data and event_data["participants"] < event_data["max_participants"]:
        event_data["participants"] += 1
        events_ref.child(event_key).update({"participants": event_data["participants"]})
        user_joined_ref.push(event_key)

# Leave an event
def leave_event(event_key):
    event_data = events_ref.child(event_key).get()
    if event_data:
        event_data["participants"] -= 1
        events_ref.child(event_key).update({"participants": event_data["participants"]})
        joined_events = fetch_joined_events()
        for joined_key, joined_event_key in joined_events.items():
            if joined_event_key == event_key:
                user_joined_ref.child(joined_key).delete()
                break

# Display map with events
def render_map(events, joined_events, search_query=""):
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)
    for event_key, event in events.items():
        if search_query.lower() in event["name"].lower() or search_query.lower() in event["description"].lower():
            participants_ratio = event["participants"] / event["max_participants"]
            participant_bar = f'<div style="width: 100%; background-color: grey; height: 10px;">' \
                              f'<div style="width: {participants_ratio * 100}%; background-color: green; height: 10px;"></div>' \
                              f'</div>'
            cancellation_prob_bar = f'<div style="width: 100%; background-color: grey; height: 10px;">' \
                                    f'<div style="width: {event["cancellation_prob"]}%; background-color: red; height: 10px;"></div>' \
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
                <p><b>Weather:</b> {event['weather']['forecast']} ({event['weather']['temp']}°C)</p>
                <p><b>Participants:</b></p>
                {participant_bar}
                <p>{event['participants']} / {event['max_participants']}</p>
                <p><b>Cancellation Probability:</b></p>
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

# Main application
st.title("JoinMy")
st.header("Connect with fellows around you!")

# Name input
st.subheader("Add Your Name")
name_input = st.text_input("Enter your name")
if st.button("Submit"):
    save_name(name_input)
    st.success(f"Name '{name_input}' saved!")

st.subheader("Saved Names")
saved_names = fetch_names()
for name_key, name in saved_names.items():
    st.write(name)

# Event search
search_query = st.text_input("Search events", "")

# Fetch events and joined events
events = fetch_events()
joined_events = fetch_joined_events()

# Handle join/leave events
params = st.experimental_get_query_params()
if "join_event" in params:
    join_event(params["join_event"][0])
    st.experimental_set_query_params()

if "leave_event" in params:
    leave_event(params["leave_event"][0])
    st.experimental_set_query_params()

# Display map
map_ = render_map(events, joined_events, search_query)
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
    address = st.text_input("Event Address (Street and Number)")
    weather_forecast = st.text_input("Weather Forecast (e.g., Sunny 🌞, Rainy 🌧️)")
    weather_temp = st.number_input("Temperature (°C)", value=20)

    if st.form_submit_button("Add Event"):
        # Simulated geocoding logic for now
        location = [47.4239 + random.uniform(-0.01, 0.01), 9.3748 + random.uniform(-0.01, 0.01)]
        event_data = {
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
            "weather": {"forecast": weather_forecast, "temp": weather_temp}
        }
        add_event_to_firebase(event_data)
        st.success(f"Event '{name}' added successfully!")
        st.experimental_rerun()

# Display joined events
st.subheader("Your Joined Events")
for joined_key, event_key in joined_events.items():
    event = events.get(event_key, {})
    if event:
        st.write(f"- {event['name']} on {event['date']} at {event['time']}")
