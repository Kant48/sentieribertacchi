import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Scegli il sentiero III° BERTACCHI")

# Creiamo la mappa
m = folium.Map(location=[46.0, 11.0], zoom_start=8)

# Dati dei rifugi e sentieri
rifugi = [
    {
        "nome": "Sasso di PREGUDA",
        "lat": 45.867,
        "lng": 9.341,
        "sentieri": [
            {"nome": "Sentiero 1", "difficolta": "Facile", "note": "Adatto ai principianti"},
            {"nome": "Sentiero 2", "difficolta": "Medio", "note": "Dislivello moderato"},
            {"nome": "Sentiero 3", "difficolta": "Difficile", "note": "Solo per esperti"}
        ]
    },
    {
        "nome": "Lecco RESEGONE",
        "lat": 45.86460,
        "lng": 9.45,
        "sentieri": [
            {"nome": "Sentiero 4", "difficolta": "Facile", "note": "Panorama bellissimo"},
            {"nome": "Sentiero 5", "difficolta": "Medio", "note": "Alcuni tratti ripidi"},
            {"nome": "Sentiero 6", "difficolta": "Difficile", "note": "Passaggi esposti"}
        ]
    }
]

# Aggiungiamo i rifugi alla mappa con i Tooltips
for rifugio in rifugi:
    # Costruisci il contenuto del popup per ciascun rifugio
    sentieri_popup = ""
    for sentiero in rifugio["sentieri"]:
        sentieri_popup += f"<b>{sentiero['nome']}</b> ({sentiero['difficolta']}): {sentiero['note']}<br>"

    folium.Marker(
        location=[rifugio["lat"], rifugio["lng"]],
        popup=sentieri_popup,  # Mostra i sentieri nel popup
        tooltip=rifugio["nome"],  # Tooltip con il nome del rifugio
        icon=folium.Icon(color="blue")
    ).add_to(m)

# Mostriamo la mappa
st_folium(m, width=700, height=500)

# Selezione della meta
st.sidebar.header("Seleziona una meta")
scelta_meta = st.sidebar.selectbox("Scegli una destinazione:", [r["nome"] for r in rifugi])

# Mostra i sentieri disponibili
for rifugio in rifugi:
    if rifugio["nome"] == scelta_meta:
        st.subheader(f"Sentieri per {scelta_meta}:")
        for sentiero in rifugio["sentieri"]:
            st.write(f"- **{sentiero['nome']}** ({sentiero['difficolta']}): {sentiero['note']}")
