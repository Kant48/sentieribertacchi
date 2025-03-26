import streamlit as st
import folium
from folium.plugins import MarkerCluster

# Definisci i dati delle località e sentieri
localita = [
    {
        "nome": "Rifugio A",
        "lat": 45.85,
        "lng": 9.40,
        "sentieri": [
            {"nome": "Sentiero 1", "difficolta": "Facile", "coordinata": [45.85, 9.405]},
            {"nome": "Sentiero 2", "difficolta": "Impegnativo", "coordinata": [45.855, 9.41]}
        ]
    },
    {
        "nome": "Rifugio B",
        "lat": 45.86,
        "lng": 9.41,
        "sentieri": [
            {"nome": "Sentiero 3", "difficolta": "Difficile", "coordinata": [45.86, 9.415]},
            {"nome": "Sentiero 4", "difficolta": "Facile", "coordinata": [45.865, 9.42]}
        ]
    }
]

# Crea una mappa centrata su un punto
mappa = folium.Map(location=[45.85, 9.40], zoom_start=13)

# Aggiungi vari tipi di tiles
folium.TileLayer("OpenStreetMap", name="Civile").add_to(mappa)
folium.TileLayer("Esri.WorldImagery", name="Boschivo").add_to(mappa)

# Aggiungi MarkerCluster per raggruppare i marker vicini
marker_cluster = MarkerCluster().add_to(mappa)

# Aggiungi i marker per ogni località e sentiero
for loc in localita:
    # Marker per la località
    localita_marker = folium.Marker(
        location=[loc['lat'], loc['lng']],
        popup=loc['nome'],
        icon=folium.Icon(color="blue")
    ).add_to(marker_cluster)

    # Aggiungi i sentieri per ogni località
    for sentiero in loc['sentieri']:
        folium.Marker(
            location=sentiero['coordinata'],
            popup=f"{sentiero['nome']} - Difficoltà: {sentiero['difficolta']}",
            icon=folium.Icon(color="green" if sentiero['difficolta'] == "Facile" else "red")
        ).add_to(marker_cluster)

# Aggiungi il controllo per i layer
folium.LayerControl().add_to(mappa)

# Mostra la mappa in Streamlit
st.title("Mappa dei Rifugi e Sentieri")
st.subheader("Visualizza il terreno e i sentieri")

# Mostra la mappa in Streamlit
st.components.v1.html(mappa._repr_html_(), height=600)
