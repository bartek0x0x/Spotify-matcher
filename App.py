import streamlit as st import requests import base64

Sekcja autoryzacji

CLIENT_ID = st.secrets["CLIENT_ID"] CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

AUTH_URL = 'https://accounts.spotify.com/api/token' auth_response = requests.post(AUTH_URL, { 'grant_type': 'client_credentials', 'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, })

auth_response_data = auth_response.json() access_token = auth_response_data['access_token'] headers = { 'Authorization': f'Bearer {access_token}' }

st.title("🎧 Znajdź podobne piosenki na Spotify") st.write("Wpisz tytuł i wykonawcę, a znajdziemy muzyczne dusze pokrewne.")

title = st.text_input("Tytuł piosenki", "Blinding Lights") artist = st.text_input("Wykonawca", "The Weeknd") limit = st.slider("Ile podobnych utworów chcesz?", 1, 20, 10)

if st.button("Szukaj podobnych"): # Wyszukiwanie ID utworu search_url = f"https://api.spotify.com/v1/search?q={title}%20{artist}&type=track&limit=1" search_response = requests.get(search_url, headers=headers)

if search_response.status_code != 200:
    st.error(f"Nie udało się znaleźć utworu: {search_response.status_code}")
else:
    search_results = search_response.json()
    items = search_results.get('tracks', {}).get('items', [])

    if not items:
        st.warning("Nie znaleziono takiego utworu.")
    else:
        track = items[0]
        track_id = track['id']
        track_name = track['name']
        track_artist = track['artists'][0]['name']
        st.success(f"Znaleziono: {track_name} – {track_artist}")

        # Pobieranie rekomendacji
        rec_url = f"https://api.spotify.com/v1/recommendations?limit={limit}&seed_tracks={track_id}"
        rec_response = requests.get(rec_url, headers=headers)

        if rec_response.status_code != 200:
            st.error(f"Spotify error {rec_response.status_code}:")
        else:
            rec_data = rec_response.json()
            rec_tracks = rec_data.get('tracks', [])

            if not rec_tracks:
                st.warning("Brak rekomendacji.")
            else:
                st.subheader("🎵 Podobne utwory:")
                for rec in rec_tracks:
                    name = rec['name']
                    artist = rec['artists'][0]['name']
                    url = rec['external_urls']['spotify']
                    st.markdown(f"[{name} – {artist}]({url})")

