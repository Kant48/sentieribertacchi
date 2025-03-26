import streamlit as st
import folium
from streamlit_folium import st_folium

# Creazione della mappa
mappa = folium.Map(location=[45.85, 9.40], zoom_start=12)
folium.TileLayer("OpenStreetMap", name="Civile").add_to(mappa)
folium.TileLayer("Esri.WorldImagery", name="Boschivo").add_to(mappa)
folium.LayerControl().add_to(mappa)

# CSS per rimuovere bordi e forzare larghezza massima
st.markdown(
    """
    <style>
        .st-emotion-cache-1kyxreq, .block-container {
            padding: 0;
            margin: 0;
            max-width: 100%;
        }
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Mostra solo la mappa
st_folium(mappa, width=1600, height=900)
