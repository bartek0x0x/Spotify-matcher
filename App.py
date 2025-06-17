import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import requests

# Autoryzacja
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

st.title("🎧 Znajdź podobne piosenki na Spotify")
st.write("Wpisz tytuł i wykonawcę, a znajdziemy muzyczne dusze pokrewne.")

tytul = st.text_input("Tytuł piosenki", "Home Is Not a Place")
artysta = st.text_input("Wykonawca", "Katu")
limit = st.slider("Ile podobnych utworów chcesz?", 1, 20, 10)

if st.button("Szukaj podobnych"):
    zapytanie = f"{tytul} {artysta}"
    wynik = sp.search(q=zapytanie, type='track', limit=1)

    if not wynik["tracks"]["items"]:
        st.error("Nie znaleziono takiej piosenki.")
        st.stop()

    utwor = wynik["tracks"]["items"][0]
    track_id = utwor["id"]
    st.success(f"Znaleziono: {utwor['name']} – {utwor['artists'][0]['name']}")

    # Pobieranie tokena ręcznie
    try:
        auth_response = requests.post(
            'https://accounts.spotify.com/api/token',
            data={'grant_type': 'client_credentials'},
            auth=(CLIENT_ID, CLIENT_SECRET)
        )
        access_token = auth_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}
    except Exception as e:
        st.error(f"Nie udało się uzyskać tokena dostępu: {e}")
        st.stop()

    # Pobieranie danych audio
    try:
        r = requests.get(
            f"https://api.spotify.com/v1/audio-features/{track_id}",
            headers=headers
        )
        if r.status_code != 200:
            st.error("Nie udało się pobrać danych audio dla tego utworu.")
            st.stop()
        features = r.json()
    except Exception as e:
        st.error(f"Nie udało się pobrać danych audio: {e}")
        st.stop()

    # Szukanie podobnych
    try:
        podobne = sp.recommendations(
            seed_tracks=[track_id],
            seed_genres=["pop"],
            target_energy=features["energy"],
            target_valence=features["valence"],
            target_danceability=features["danceability"],
            target_acousticness=features["acousticness"],
            target_instrumentalness=features["instrumentalness"],
            target_tempo=features["tempo"],
            limit=limit
        )
    except Exception as e:
        st.error(f"Błąd podczas pobierania rekomendacji: {e}")
        st.stop()

    # Wyświetlanie wyników
    lista = []
    for track in podobne["tracks"]:
        lista.append({
            "Tytuł": track["name"],
            "Artysta": track["artists"][0]["name"],
            "Link": track["external_urls"]["spotify"]
        })

    df = pd.DataFrame(lista)
    st.dataframe(df)
    for piosenka in lista:
        st.markdown(f"[{piosenka['Tytuł']} – {piosenka['Artysta']}]({piosenka['Link']})")
