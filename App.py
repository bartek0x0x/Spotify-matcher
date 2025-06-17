# Wyszukiwanie utworu
search_url = f"https://api.spotify.com/v1/search?q={title} {artist}&type=track&limit=1"
search_response = requests.get(search_url, headers=headers)

st.write("🔍 URL wyszukiwania:", search_url)
st.write("📦 Odpowiedź z wyszukiwania:", search_response.json())

if search_response.status_code != 200:
    st.error(f"Błąd wyszukiwania: {search_response.status_code} – {search_response.text}")
    st.stop()

try:
    track = search_response.json()["tracks"]["items"][0]
    track_id = track["id"]
    st.success(f"Znaleziono: {track['name']} – {track['artists'][0]['name']}")
    st.write("🎯 Track ID:", track_id)
except Exception as e:
    st.error(f"Nie udało się znaleźć utworu. Błąd: {str(e)}")
    st.stop()

# Pobieranie rekomendacji
rec_url = f"https://api.spotify.com/v1/recommendations?limit={limit}&seed_tracks={track_id}"
st.write("📡 URL rekomendacji:", rec_url)

rec_response = requests.get(rec_url, headers=headers)

if rec_response.status_code != 200:
    st.error(f"Spotify error {rec_response.status_code}: {rec_response.text}")
    st.stop()

# Wyświetlenie wyniku
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
