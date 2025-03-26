import folium
import streamlit as st
import pandas as pd
import json
from streamlit_folium import st_folium

# Centro mappa
latzona = 45.85
longzona = 9.40

# Caricamento del file Excel
file_path = r"C:\APP\inputapp.xlsx"
df = pd.read_excel(file_path)

# Sostituisci la virgola con il punto nelle coordinate
df['Latitudine Località'] = df['Latitudine Località'].astype(str).str.replace(',', '.').astype(float)
df['Longitudine Località'] = df['Longitudine Località'].astype(str).str.replace(',', '.').astype(float)
df['Latitudine Passaggio'] = df['Latitudine Passaggio'].astype(str).str.replace(',', '.').astype(float)
df['Longitudine Passaggio'] = df['Longitudine Passaggio'].astype(str).str.replace(',', '.').astype(float)

# Dizionario delle località e telefoni
localita = {}
diztelefoni = {}

# Costruzione del dizionario
for _, row in df.iterrows():
    nome_localita = row["Nome Località"]
    
    if nome_localita not in localita:
        localita[nome_localita] = {
            "lat": row["Latitudine Località"],
            "lng": row["Longitudine Località"],
            "sentieri": {}
        }
    
    nome_sentiero = row["Nome Sentiero"]
    colore_sentiero = row["colore sentiero"]

    if nome_sentiero not in localita[nome_localita]["sentieri"]:
        localita[nome_localita]["sentieri"][nome_sentiero] = {
            "difficolta": row["Difficoltà"],
            "colore": colore_sentiero,
            "percorso": []
        }
    
    localita[nome_localita]["sentieri"][nome_sentiero]["percorso"].append({
        "sequenza": row["Sequenza"],
        "lat": row["Latitudine Passaggio"],
        "lng": row["Longitudine Passaggio"],
        "note": row["Note"],
        "immagine": row["Immagine"],
    })

    diztelefoni[nome_localita] = {
        "numero_telefono": row["Numero Telefono"],
        "note": row.get("NOTELOC", "")
    }

# Riordinare i passaggi per sequenza
for nome_localita in localita:
    for nome_sentiero in localita[nome_localita]["sentieri"]:
        localita[nome_localita]["sentieri"][nome_sentiero]["percorso"].sort(key=lambda x: x["sequenza"])

# Creazione mappa con Folium
mappa = folium.Map(location=[latzona, longzona], zoom_start=12)
folium.TileLayer("OpenStreetMap", name="Civile").add_to(mappa)
folium.TileLayer("Esri.WorldImagery", name="Boschivo").add_to(mappa)

# Aggiunta località alla mappa
for nome_localita, dati_localita in localita.items():
    folium.Marker(
        location=[dati_localita["lat"], dati_localita["lng"]],
        popup=f"<b>{nome_localita}</b>",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(mappa)

    for nome_sentiero, dati_sentiero in dati_localita["sentieri"].items():
        punti_sentiero = []

        for i, passaggio in enumerate(dati_sentiero["percorso"]):
            lat, lng = passaggio["lat"], passaggio["lng"]
            punti_sentiero.append([lat, lng])

            # Costruisci il popup con informazioni sul sentiero
            popup_html = f"""
            <b>{nome_sentiero}</b><br>
            {passaggio['note']}<br>
            <span style="color: blue; cursor: pointer;" onclick="alert('Chiama il numero: {diztelefoni[nome_localita]['numero_telefono']}');">Vuoi una guida?</span>
            """
            marker_color = "blue" if i == len(dati_sentiero["percorso"]) - 1 else dati_sentiero["colore"]
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(color=marker_color, icon="flag")
            ).add_to(mappa)

        folium.PolyLine(punti_sentiero, color=dati_sentiero["colore"], weight=3, opacity=0.7, tooltip=nome_sentiero).add_to(mappa)

folium.LayerControl().add_to(mappa)

# Mostrare la mappa con Streamlit
st.title("Mappa dei Sentieri")

# Controlliamo se c'è un parametro "guida" nell'URL
query_params = st.query_params
if "guida" in query_params:
    localita_richiesta = query_params["guida"]
    if localita_richiesta in diztelefoni:
        st.warning(f"Chiama il numero: {diztelefoni[localita_richiesta]['numero_telefono']} per una guida!")
        if diztelefoni[localita_richiesta]["note"]:
            st.info(f"Note pratiche: {diztelefoni[localita_richiesta]['note']}")
    else:
        st.error("Numero di telefono non disponibile per questa località.")

# Visualizza la mappa
st_folium(mappa, width=700, height=500)

