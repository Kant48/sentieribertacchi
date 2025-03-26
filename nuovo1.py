import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Scegli il sentiero III° BERTACCHI")



















# Creiamo la mappa
m = folium.Map(location=[46.0, 11.0], zoom_start=8)

# Aggiungi il tile layer "Stamen Terrain" con l'attribuzione corretta
stamen_layer = folium.TileLayer(
    tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
    attr="Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors",
    name="Terreno",  # Nome da visualizzare nel LayerControl
    overlay=True,
    control=True  # Permette di selezionare il layer nel controllo
).add_to(m)

# Aggiungi OpenStreetMap (default)
osm_layer = folium.TileLayer(
    "OpenStreetMap",
    name="OpenStreetMap",  # Nome da visualizzare nel LayerControl
    control=True  # Permette di selezionare il layer nel controllo
).add_to(m)

# Aggiungi OpenTopoMap per visualizzare dettagli geografici (boschi, case, strade, ecc.)
opentopomap_layer = folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="Map tiles by OpenTopoMap, CC BY-SA 3.0 — Map data © OpenStreetMap contributors",
    name="OpenTopoMap",  # Nome da visualizzare nel LayerControl
    overlay=True,
    control=True  # Permette di selezionare il layer nel controllo
).add_to(m)

# Aggiungi anche CartoDB positron (un altro stile di mappa)
cartodb_layer = folium.TileLayer(
    tiles="CartoDB positron",
    name="CartoDB Positron",  # Nome da visualizzare nel LayerControl
    control=True  # Permette di selezionare il layer nel controllo
).add_to(m)

# Dati dei rifugi e sentieri (aggiungiamo coordinate per i sentieri)
rifugi = [
    {
        "nome": "Sasso di PREGUDA",
        "lat": 45.8643,
        "lng": 9.3596,
        "sentieri": [
            {"nome": "Sentiero 1", "difficolta": "Facile", "note": "Adatto ai principianti", "coordinata": [[45.8553, 9.3555], [45.856, 9.3577], [45.8572, 9.3581], [45.8643, 9.3596]]},
            {"nome": "Sentiero 2", "difficolta": "Medio", "note": "Dislivello moderato", "coordinata": [[45.867, 9.341], [45.869, 9.350]]},
            {"nome": "Sentiero 3", "difficolta": "Difficile", "note": "Solo per esperti", "coordinata": [[45.867, 9.341], [45.870, 9.355]]}
        ]
    },
    {
        "nome": "Lecco RESEGONE",
        "lat": 45.86460,
        "lng": 9.45,
        "sentieri": [
            {"nome": "Sentiero 4", "difficolta": "Facile", "note": "Panorama bellissimo", "coordinata": [[45.86460, 9.45], [45.865, 9.460]]},
            {"nome": "Sentiero 5", "difficolta": "Medio", "note": "Alcuni tratti ripidi", "coordinata": [[45.86460, 9.45], [45.866, 9.470]]},
            {"nome": "Sentiero 6", "difficolta": "Difficile", "note": "Passaggi esposti", "coordinata": [[45.86460, 9.45], [45.867, 9.480]]}
        ]
    }
]

# Aggiungiamo i rifugi alla mappa con i Tooltips e i sentieri come polilinee
for rifugio in rifugi:
    sentieri_popup = ""
    for sentiero in rifugio["sentieri"]:
        sentieri_popup += f"<b>{sentiero['nome']}</b> ({sentiero['difficolta']}): {sentiero['note']}<br>"

        # Aggiungiamo la polilinea per ogni sentiero
        color = 'green' if sentiero['difficolta'] == 'Facile' else 'orange' if sentiero['difficolta'] == 'Medio' else 'red'
        folium.PolyLine(sentiero['coordinata'], color=color, weight=4, opacity=0.7).add_to(m)

    # Marker per il rifugio
    folium.Marker(
        location=[rifugio["lat"], rifugio["lng"]],
        popup=sentieri_popup,  # Mostra i sentieri nel popup
        tooltip=rifugio["nome"],  # Tooltip con il nome del rifugio
        icon=folium.Icon(color="blue")
    ).add_to(m)

# Aggiungi il controllo per i vari layer
folium.LayerControl().add_to(m)

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
