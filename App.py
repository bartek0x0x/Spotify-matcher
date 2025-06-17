import streamlit as st
import requests
import pandas as pd

# Dane logowania do API Spotify
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

# Funkcja pobierająca token
def get_token():
    auth_response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={'grant_type': 'client_credentials'},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    return auth_response.json().get("access_token")

# Tytuł aplikacji
st.title("🎧 Znajdź podobne piosenki na Spotify")
st.write("Wpisz tytuł i wykonawcę, a znajdziemy muzyczne dusze pokrewne.")

# Dane wejściowe
tytul = st.text_input("Tytuł piosenki", "Blinding Lights")
artysta = st.text_input("Wykonawca", "The Weeknd")
limit = st.slider("Ile podobnych utworów chcesz?", 1, 20, 10)

if st.button("Szukaj podobnych"):
    access_token = get_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    # Wyszukiwanie piosenki
    query = f"{tytul} {artysta}"
    search_url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
    result = requests.get(search_url, headers=headers).json()

    try:
        track = result["tracks"]["items"][0]
    except IndexError:
        st.error("Nie znaleziono takiej piosenki.")
        st.stop()

    track_id = track["id"]
    st.success(f"Znaleziono: {track['name']} – {track['artists'][0]['name']}")

    # Pobieranie podobnych
    rec_url = f"https://api.spotify.com/v1/recommendations?limit={limit}&seed_tracks={track_id}"
    rec_result = requests.get(rec_url, headers=headers).json()

    try:
        tracks = rec_result["tracks"]
        lista = []
        for t in tracks:
            lista.append({
                "Tytuł": t["name"],
                "Artysta": t["artists"][0]["name"],
                "Link": t["external_urls"]["spotify"]
            })

        df = pd.DataFrame(lista)
        st.dataframe(df)
        for row in lista:
            st.markdown(f"[{row['Tytuł']} – {row['Artysta']}]({row['Link']})")
    except KeyError:
        st.error("Nie udało się pobrać rekomendacji. Prawdopodobnie Spotify znowu coś kombinuje.")
