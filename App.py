import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Autoryzacja z secretów
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
    else:
        utwor = wynik["tracks"]["items"][0]
        track_id = utwor["id"]
        st.success(f"Znaleziono: {utwor['name']} – {utwor['artists'][0]['name']}")

        features_list = sp.audio_features([track_id])
        if not features_list or features_list[0] is None:
            st.error("Brak danych audio dla tego utworu. Spróbuj inny.")
            st.stop()

        features = features_list[0]

        try:
            podobne = sp.recommendations(
                seed_tracks=[track_id],
                seed_genres=["alternative"],  # Możesz zmienić na pop, hip-hop, itp.
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
