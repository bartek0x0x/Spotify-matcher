import streamlit as st
import requests
import pandas as pd

CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

def get_token():
    r = requests.post(
        'https://accounts.spotify.com/api/token',
        data={'grant_type': 'client_credentials'},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    return r.json().get("access_token")

st.title("🎧 Znajdź podobne piosenki na Spotify")

title = st.text_input("Tytuł piosenki", "Blinding Lights")
artist = st.text_input("Wykonawca", "The Weeknd")
limit = st.slider("Ile podobnych utworów chcesz?", 1, 20, 10)

if st.button("Szukaj podobnych"):
    token = get_token()
    if not token:
        st.error("Nie udało się pobrać tokena Spotify.")
        st.stop()

    headers = {"Authorization": f"Bearer {token}"}

    # Szukanie piosenki
    search = requests.get(
        f"https://api.spotify.com/v1/search?q={title} {artist}&type=track&limit=1",
        headers=headers
    )
    try:
        track = search.json()["tracks"]["items"][0]
    except:
        st.error("Nie znaleziono utworu.")
        st.stop()

    track_id = track["id"]
    st.success(f"Znaleziono: {track['name']} – {track['artists'][0]['name']}")

    # Rekomedacje – z debugiem
    url = f"https://api.spotify.com/v1/recommendations?limit={limit}&seed_tracks={track_id}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.error(f"Spotify error {response.status_code}: {response.text}")
        st.stop()

    try:
        tracks = response.json()["tracks"]
        results = []
        for t in tracks:
            results.append({
                "Tytuł": t["name"],
                "Artysta": t["artists"][0]["name"],
                "Link": t["external_urls"]["spotify"]
            })
        st.dataframe(pd.DataFrame(results))
        for r in results:
            st.markdown(f"[{r['Tytuł']} – {r['Artysta']}]({r['Link']})")
    except Exception as e:
        st.error(f"Błąd przy parsowaniu odpowiedzi: {str(e)}")
        st.write("Odpowiedź z API:")
        st.text(response.text)
