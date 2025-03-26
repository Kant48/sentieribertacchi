import streamlit as st
import folium
import pandas as pd
from folium.plugins import MarkerCluster
import os

st.title("Mappa dei Rifugi e Sentieri")
st.subheader("Visualizza il terreno e i sentieri")

# Percorso del file Excel
file_path = r"C:\APP\inputapp.xlsx"

# Verifica se il file esiste
if os.path.exists(file_path):
    df = pd.read_excel(file_path)

    # Riorganizza i dati in una struttura nidificata
    localita = {}
    for _, row in df.iterrows():
        nome = row["Nome Località"]
        if nome not in localita:
            localita[nome] = {
                "lat": row["Latitudine Località"],
                "lng": row["Longitudine Località"],
                "sentieri": []
            }
        localita[nome]["sentieri"].append({
            "nome": row["Nome Sentiero"],
            "difficolta": row["Difficoltà"],
            "coordinata": [row["Latitudine Passaggio"], row["Longitudine Passaggio"]]
        })
    print (localita)
    # Crea la mappa
    latitudine = df["Latitudine"].mean()
    longitudine = df["Longitudine"].mean()
    mappa = folium.Map(location=[latitudine, longitudine], zoom_start=13)

    # Aggiungi vari tipi di tiles
    folium.TileLayer("OpenStreetMap", name="Civile").add_to(mappa)
    folium.TileLayer("Esri.WorldImagery", name="Boschivo").add_to(mappa)

    # Aggiungi MarkerCluster per raggruppare i marker vicini
    marker_cluster = MarkerCluster().add_to(mappa)

    # Aggiungi i marker
    for nome, loc in localita.items():
        folium.Marker(
            location=[loc["lat"], loc["lng"]],
            popup=nome,
            icon=folium.Icon(color="blue")
        ).add_to(marker_cluster)

        for sentiero in loc["sentieri"]:
            folium.Marker(
                location=sentiero["coordinata"],
                popup=f"{sentiero['nome']} - Difficoltà: {sentiero['difficolta']}",
                icon=folium.Icon(color="green" if sentiero["difficolta"] == "Facile" else "red")
            ).add_to(marker_cluster)

    # Aggiungi il controllo dei layer
    folium.LayerControl().add_to(mappa)

    # Mostra la mappa
    st.components.v1.html(mappa._repr_html_(), height=600)
else:
    st.error(f"⚠️ Il file '{file_path}' non esiste. Verifica il percorso.")
