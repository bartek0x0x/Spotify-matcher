import streamlit as st import requests import base64 import json

Tytuł aplikacji

st.title("🎧 Znajdź podobne piosenki na Spotify") st.write("Wpisz tytuł i wykonawcę, a znajdziemy muzyczne dusze pokrewne.")

Formularz wejściowy

title = st.text_input("Tytuł piosenki", "Blinding Lights") artist = st.text_input("Wykonawca", "The Weeknd") limit = st.slider("Ile podobnych utworów chcesz?", 1, 20, 10)

Sekrety

CLIENT_ID = st.secrets["CLIENT_ID"] CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

Funkcja autoryzacji

def get_token(): auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}" b64_auth_str = base64.b64encode(auth_str.encode()).decode() headers = { "Authorization": f"Basic {b64_auth_str}", "Content-Type": "application/x-www-form-urlencoded" } data = {"grant_type": "client_credentials"} resp = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data) return resp.json().get("access_token")

Szukanie ID piosenki

def get_track_id(token, title, artist): headers = {"Authorization": f"Bearer {token}"} query = f"track:{title} artist:{artist}" url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1" resp = requests.get(url, headers=headers) results = resp.json() items = results.get("tracks", {}).get("items", []) if items: return items[0]["id"], f"Znaleziono: {items[0]['name']} – {items[0]['artists'][0]['name']}" return None, "Nie znaleziono utworu."

Pobieranie audio features i rekomendacji

def get_recommendations(token, track_id, limit): headers = {"Authorization": f"Bearer {token}"} url = f"https://api.spotify.com/v1/recommendations?seed_tracks={track_id}&limit={limit}" resp = requests.get(url, headers=headers) if resp.status_code == 200: recs = resp.json().get("tracks", []) return [f"{t['name']} – {t['artists'][0]['name']}" for t in recs] else: return f"Spotify error {resp.status_code}: {resp.text}"

Główna akcja

if st.button("Szukaj podobnych"): token = get_token() if token: track_id, message = get_track_id(token, title, artist) st.success(message) if track_id: recs = get_recommendations(token, track_id, limit) if isinstance(recs, list): st.subheader("🎵 Podobne utwory:") for r in recs: st.write(r) else: st.error(recs) else: st.warning("Nie znaleziono ID utworu.") else: st.error("Nie udało się pobrać tokenu dostępu do Spotify.")

