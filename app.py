import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime
import random

# hardcode data
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
        "weather": {"forecast": "Cloudy ☁️", "temp": 6}
    },
    {
        "name": "Study Group",
        "organizer": "Bill Gates",
        "location": [47.4245, 9.3769],
        "date": "2024-11-22",
        "time": "10:00",
        "description": "Group study session for exams.",
        "participants": 8,
        "max_participants": 10,
        "event_type": "indoor",
        "cancellation_prob": 5,
        "weather": {"forecast": "Cloudy ☁️", "temp": 7}
    },
    {
        "name": "Yoga in the Park",
        "organizer": "Anna Müller",
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
        "organizer": "Frida Kahlo",
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
        "organizer": "John Doe",
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
        "organizer": "Jane Austen",
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
    },
    {
        "name": "Dance Night",
        "organizer": "Mikhail Baryshnikov",
        "location": [47.4253, 9.3758],
        "date": "2024-12-10",
        "time": "20:00",
        "description": "Dance the night away with great music and friends.",
        "participants": 25,
        "max_participants": 30,
        "event_type": "indoor",
        "cancellation_prob": 0,
        "weather": {"forecast": "Partly Cloudy ⛅", "temp": 8}
    }
]

# The rest of your code remains unchanged.
# It uses the `events` list above.
