import streamlit as st
import folium
from streamlit_folium import st_folium
from firebase_admin import credentials, firestore, initialize_app
import requests
from datetime import datetime
import random

# Firebase Initialization
cred = credentials.Certificate("\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCyOUwGuy0m4HMn\nWwj7qcXL1YcW4Y6WFuoL+gRDsYqEZBel/3NZXzEcz65ZY9PTHabQLD4K9gKBLc5c\nGHrdOWip4yB6r3tSjaeuG1dfoH+f9oSD2bGkBVH1qncZV+hyMwvj53TfgIKkUbAf\nxOnFjrV2PA02/rjPAyg9XGXyclkwiQl1Dg7h9ki55pAtBHlMfpYeW5Q7UAhYtik1\n4ekwCHqIiSc1bbNhl47/p2dHGZwfQKxrpAqPQ1MSiiMXiBdEf0bxc4YrnhPSdiEd\ntye6SEOkjvlPQgmoMTugzi1xrN2i8Qi+Wr8ooR9NDDtOu2KVNA+3meur4MML1kW4\ntwzXsiVbAgMBAAECggEALD/Uk/FCFx5wCMvt8YnnzaGAzloHLFWZG4siJup8MT2m\nr3S6n2xmhbg8mf4SmB6LDbGGX/NPkOIeE7iSPL3lshRtung6Prdj8/Le4SO4vC8Z\nHKFenRIjFMMTmeu9DymEYLvVRS6jgQe1GlYqEn5JqIblYwugN+mZQo7f0u+4HDfn\np7MvAHy32k+vT1SwaI8yjoK1KoNDa8IZPYdlRqGd/OEQNnLiY2jtF9IvGQFm6mb4\nILq5IsMDvNdLL/ub1Bmo0L1hcKjIihVcWebT8LxULObLdjxU9WQ7kyd7Eicy6Rxc\nK6urIfAHpwhqCE679UQDXZNJ3PlD6iSdtPFJaFhVJQKBgQDjNqSmc646uni4sgJj\n+K/c62JsYC+TXEGoRCdm2chuPkvptIqu5NZEf+vcr8Mrg8oeixqLhrBmvwm9sBID\nSltR4LgfF2zG1kGGYyI0UA/tLFk08qP0MtXqQsvmXBhITcY5CN82IW64UoNmFPm6\nRdWLb/QbXwXL2uGLcWtVfC1o/wKBgQDIzb4AUpiCD1Oi7pM7g/Do09zpgKOt6nDC\nXjis5PNQ7uqBtLnAmj/hAU4ythqFmSTwSrzFtN0s2X/QRDLoqSmpbi7jXH+BqVVU\nhBx8SpGfxiThOTqz/SE3XsNhn7JJSkKOUmwMmApcO2STOtyIfW+bzKL3islQnIGo\nnACj/PGHpQKBgHqGhAGSzjizR9hpfeqFN+jNMjU5JU606F8h6ZGIDZKNm4g6qLKp\ninZD+V/3lCrKFdukrbrh9gxiJpGY+g22MkqUARYbHriW35zlppNJPV1rlet8kTdl\nln+OZ8Agl6Od9S/afewF2VwieuM4mnZ9pCteQufjtQ96SDhXAEeIAEDnAoGBAIkg\nz5cC0LlI5DHJQOyMzvEA9cTUH3L+PeDOXV/cvjjP33+SPqPD8smijZdd+sCvc6VR\nNJbDS6N8KKe+WxG9rADTiNulaEHQtMARtC5A8i+tLbRM08TkoVFhuoWpfCRGvSra\nKIV1MuYHfUh6Eu520sgPuF7Z/V66cmUFm/5hF0QtAoGAQIXEuC7cGLxz2t9nUVlu\nT2YX2ATJMB+goP8GZm+CGGBH5mL8+ykJWKiEcQO168nFMjfFrjLo25W8A3YPRIMN\nGra6nDA7ughEH/cUPLe1BsKAT9BW4v3XQunA+o25aDDrVrXquaKIANmZPSNkUNSD\nC5Es2Ms6QA62Yif0hm0UkA0=\n")
initialize_app(cred)
db = firestore.client()
events_ref = db.collection("events")

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

# Fetch events from Firestore
def fetch_events():
    docs = events_ref.stream()
    return [doc.to_dict() for doc in docs]

# Add event to Firestore
def add_event_to_firestore(event):
    events_ref.add(event)

# Update participants in Firestore
def update_event_participants(event_id, participants):
    event_doc = events_ref.document(event_id)
    event_doc.update({"participants": participants})

# Render map with events
def render_map(search_query=""):
    base_map = folium.Map(location=[47.4239, 9.3748], zoom_start=14)
    events = fetch_events()
    filtered_events = [
        event for event in events
        if search_query.lower() in event["name"].lower() or search_query.lower() in event["description"].lower()
    ]
    for event in filtered_events:
        participants_ratio = event["participants"] / event["max_participants"]
        participant_bar = f'<div style="width: 100%; background-color: grey; height: 10px; position: relative;">' \
                          f'<div style="width: {participants_ratio * 100}%; background-color: green; height: 10px;"></div>' \
                          f'</div>'
        cancellation_prob_bar = f'<div style="width: 100%; background-color: grey; height: 10px; position: relative;">' \
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

# Streamlit layout
st.title("JoinMy")
st.header("Connect with fellows around you!")
search_query = st.text_input("Search events", "")

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
                add_event_to_firestore(new_event)
                st.success(f"Event '{name}' added successfully!")
                st.experimental_rerun()
            else:
                st.error("Could not find location. Please try again.")
        else:
            st.error("Address is required.")
