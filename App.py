import streamlit as st
import requests
import pandas as pd
from urllib.parse import urlencode

# Wczytanie danych logowania z pliku secrets.toml
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

# Funkcja pobierająca token dostępu
def get_token():
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={'grant_type': 'client_credentials'},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    return response.json().get("access_token")

# Interfejs użytkownika
st.title("🎧 Znajdź podobne piosenki na Spotify")
st.write("Wpisz tytuł i wykonawcę, a znajdziemy muzyczne dusze pokrewne.")

title = st.text_input("Tytuł piosenki", "Blinding Lights")
artist = st.text_input("Wykonawca", "The Weeknd")
limit = st.slider("Ile podobnych utworów chcesz?", 1, 20, 10)

if st.button("Szukaj podobnych"):
    token = get_token()
    if not token:
        st.error("Nie udało się uzyskać tokena dostępu.")
        st.stop()

    headers = {"Authorization": f"Bearer {token}"}

    # Wyszukiwanie utworu
    search_url = f"https://api.spotify.com/v1/search?q={title} {artist}&type=track&limit=1"
    search_response = requests.get(search_url, headers=headers)
    if search_response.status_code != 200:
        st.error(f"Błąd wyszukiwania: {search_response.status_code} – {search_response.text}")
        st.stop()

    try:
        track = search_response.json()["tracks"]["items"][0]
    except IndexError:
        st.error("Nie znaleziono takiego utworu.")
        st.stop()

    track_id = track["id"]
    st.success(f"Znaleziono: {track['name']} – {track['artists'][0]['name']}")

    # Pobieranie rekomendacji
    rec_url = f"https://api.spotify.com/v1/recommendations?" + urlencode({
        "limit": limit,
        "seed_tracks": track_id
    })

    rec_response = requests.get(rec_url, headers=headers)

    if rec_response.status_code != 200:
        st.error(f"Spotify error {rec_response.status_code}: {rec_response.text}")
        st.stop()

    try:
        tracks = rec_response.json()["tracks"]
        results = []
        for t in tracks:
            results.append({
                "Tytuł": t["name"],
                "Artysta": t["artists"][0]["name"],
                "Link": t["external_urls"]["spotify"]
            })

        df = pd.DataFrame(results)
        st.dataframe(df)

        for r in results:
            st.markdown(f"[{r['Tytuł']} – {r['Artysta']}]({r['Link']})")
    except Exception as e:
        st.error(f"Błąd przy parsowaniu danych: {str(e)}")
        st.text(rec_response.text)
