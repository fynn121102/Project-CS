import google.auth.exceptions

try:
    # Initialize Firebase and fetch data
    fetch_events()
except google.auth.exceptions.RefreshError as e:
    st.error(f"Refresh error: {e}")
except Exception as e:
    st.error(f"General error: {e}")
