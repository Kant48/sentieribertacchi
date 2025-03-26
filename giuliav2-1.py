import streamlit as st
import folium
from streamlit_folium import st_folium


st.title("Scegli il sentiero III° BERTACCHI")

# Dizionario per mappare la difficoltà selezionata con il database
mappa_difficolta = {
    "1 - Facile anche per bambini": "FacileB",
    "2 - Facile per adulti": "Facile",
    "3 - Impegnativo": "Medio",
    "4 - Impervio": "Difficile"
}

# Sidebar per selezionare la difficoltà
st.sidebar.header("Seleziona il livello di difficoltà del sentiero")
scelta_difficolta = st.sidebar.selectbox(
    "Che tipo di escursione vuoi fare ? :",
    list(mappa_difficolta.keys())  # Mostra i nomi completi
)

# Traduzione della scelta utente nella difficoltà del database
difficolta_filtrata = mappa_difficolta[scelta_difficolta]

# Creiamo la mappa con il layer "Stamen Terrain"
m = folium.Map(location=[45.85, 9.40], zoom_start=15)

# Aggiungi anche OpenStreetMap (default)
#folium.TileLayer("OpenStreetMap", name="OpenStreetMap", control=True).add_to(m)
# Aggiungi OpenTopoMap per visualizzare dettagli geografici (boschi, case, strade, ecc.)
opentopomap_layer = folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="Map tiles by OpenTopoMap, CC BY-SA 3.0 — Map data © OpenStreetMap contributors",
    name="OpenTopoMap",  # Nome da visualizzare nel LayerControl
    overlay=True,
    control=True ,
    zindex=3 # Permette di selezionare il layer nel controllo
).add_to(m)
# Aggiungi il tile layer "ESRI Satellite"
esri_satellite_layer = folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="ESRI, USGS, NOAA",
    name="Satellite",
    overlay=True,
    control=True,
    zindex=2
).add_to(m)
# Aggiungi il tile layer "Stamen Terrain" con l'attribuzione corretta
stamen_layer = folium.TileLayer(
    tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
    attr="Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors",
    name="Terreno",
    overlay=True,
    control=True,
    zindex=1
).add_to(m)                   

# Dati dei rifugi e sentieri
rifugi = [
    {
        "nome": "Sasso di PREGUDA",
        "lat": 45.86401,
        "lng": 9.35976,
        "sentieri": [
            {"nome": "Sentiero 1", "difficolta": "Facile", "note": "Adatto ai bambini", "coordinata": [[45.8476, 9.35806], [45.85496, 9.35723], [45.85505, 9.35754],[45.85616, 9.35683],[45.86401, 9.35976]]},
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
    },
    {
        "nome": "Valmadrera San Tommaso",
        "lat": 45.86460,
        "lng": 9.45,
        "sentieri": [
            {"nome": "Sentiero 4", "difficolta": "FacileB", "note": "Panorama bellissimo", "coordinata": [[45.849, 9.343]]},
            {"nome": "Sentiero 5", "difficolta": "Medio", "note": "Alcuni tratti ripidi", "coordinata": [[45.86460, 9.45], [45.866, 9.470]]},
            {"nome": "Sentiero 6", "difficolta": "Difficile", "note": "Passaggi esposti", "coordinata": [[45.86460, 9.45], [45.867, 9.480]]}
        ]
    },
]

# Filtriamo i rifugi che hanno almeno un sentiero con la difficoltà selezionata
rifugi_filtrati = []
for rifugio in rifugi:
    sentieri_filtrati = [s for s in rifugio["sentieri"] if s["difficolta"] == difficolta_filtrata]
    if sentieri_filtrati:  # Se ci sono sentieri compatibili, includiamo il rifugio
        rifugi_filtrati.append({"nome": rifugio["nome"], "lat": rifugio["lat"], "lng": rifugio["lng"], "sentieri": sentieri_filtrati})

# Aggiungiamo i rifugi filtrati alla mappa con i Tooltips e i sentieri come polilinee
for rifugio in rifugi_filtrati:
    sentieri_popup = ""
    for sentiero in rifugio["sentieri"]:
        sentieri_popup += f"<b>{sentiero['nome']}</b> ({sentiero['difficolta']}): {sentiero['note']}<br>"
        
        # Aggiungiamo la polilinea per ogni sentiero filtrato
        color = 'blue' if sentiero['difficolta'] == 'Facile' else 'orange' if sentiero['difficolta'] == 'Medio' else 'red'
        folium.PolyLine(sentiero['coordinata'], color=color, weight=4, opacity=0.7).add_to(m)

    # Marker per il rifugio filtrato
    folium.Marker(
        location=[rifugio["lat"], rifugio["lng"]],
        popup=sentieri_popup,
        tooltip=rifugio["nome"],
        icon=folium.Icon(color="blue")
    ).add_to(m)
    # Percorso dell'immagine locale (ad esempio, nella cartella "assets" del tuo progetto)
    image_path = "C:/app/fotopreguda.jpeg"  # Sostituisci con il percorso della tua immagine

# Crea un popup con l'immagine loca
popup_html = f'<img src="file:///{image_path}" width="300" height="200">'

# Aggiungi un marker con il popup dell'immagine
folium.Marker([45.86401, 9.35976], popup=popup_html).add_to(m)

# Aggiungi il controllo per i vari layer
folium.LayerControl().add_to(m)

# Mostriamo la mappa con solo i rifugi e i sentieri corrispondenti alla scelta dell'utente
st_folium(m, width=700, height=500)

# Mostriamo i sentieri disponibili per i rifugi filtrati
if rifugi_filtrati:
    st.subheader(f"Sentieri disponibili con difficoltà: {difficolta_filtrata}")
    for rifugio in rifugi_filtrati:
        st.markdown(f"### {rifugio['nome']}")
        for sentiero in rifugio["sentieri"]:
            st.write(f"- **{sentiero['nome']}** ({sentiero['difficolta']}): {sentiero['note']}")
else:
    st.warning("Nessun sentiero disponibile per la difficoltà selezionata.")
