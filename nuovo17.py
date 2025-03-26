import folium
import streamlit as st
import pandas as pd

latzona = 45.85
longzona = 9.40

# Caricamento del file Excel
file_path = r"C:\APP\inputapp.xlsx"
df = pd.read_excel(file_path)

# Sostituisci la virgola con il punto per le colonne Latitudine e Longitudine
df['Latitudine Località'] = df['Latitudine Località'].apply(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)
df['Longitudine Località'] = df['Longitudine Località'].apply(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)

# Converti le colonne in tipo float
df['Latitudine Località'] = pd.to_numeric(df['Latitudine Località'], errors='coerce')
df['Longitudine Località'] = pd.to_numeric(df['Longitudine Località'], errors='coerce')

# Sostituisci la virgola con il punto per le colonne Latitudine e Longitudine
df['Latitudine Passaggio'] = df['Latitudine Passaggio'].apply(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)
df['Longitudine Passaggio'] = df['Longitudine Passaggio'].apply(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)

# Converti le colonne in tipo float
df['Latitudine Passaggio'] = pd.to_numeric(df['Latitudine Passaggio'], errors='coerce')
df['Longitudine Passaggio'] = pd.to_numeric(df['Longitudine Passaggio'], errors='coerce')

# Dizionario delle località
localita = {}

# Scorrere il DataFrame riga per riga
for _, row in df.iterrows():
    nome_localita = row["Nome Località"]

    # Se la località non esiste, la creiamo
    if nome_localita not in localita:
        localita[nome_localita] = {
            "lat": row["Latitudine Località"],
            "lng": row["Longitudine Località"],
            "sentieri": {}
        }

    # Nome del sentiero
    nome_sentiero = row["Nome Sentiero"]
    colore_sentiero = row["colore sentiero"]  # Legge il colore dal file Excel

    # Se il sentiero non esiste in questa località, lo creiamo
    if nome_sentiero not in localita[nome_localita]["sentieri"]:
        localita[nome_localita]["sentieri"][nome_sentiero] = {
            "difficolta": row["Difficoltà"],
            "colore": colore_sentiero,  # Salviamo il colore
            "percorso": []
        }

    # Aggiungiamo il passaggio ordinato per sequenza
    localita[nome_localita]["sentieri"][nome_sentiero]["percorso"].append({
        "sequenza": row["Sequenza"],
        "lat": row["Latitudine Passaggio"],
        "lng": row["Longitudine Passaggio"],
        "note": row["Note"],
        "immagine": row["Immagine"],  # Salva il link immagine nel dizionario
    })

# Riordinare i passaggi per ogni sentiero in base alla sequenza
for nome_localita in localita:
    for nome_sentiero in localita[nome_localita]["sentieri"]:
        localita[nome_localita]["sentieri"][nome_sentiero]["percorso"].sort(key=lambda x: x["sequenza"])

# Creazione della mappa centrata sulla prima località
centro_mappa = [latzona, longzona]  # Latitudine, Longitudine
mappa = folium.Map(location=centro_mappa, zoom_start=12)

# Aggiungi vari tipi di tiles
folium.TileLayer("OpenStreetMap", name="Civile").add_to(mappa)
folium.TileLayer("Esri.WorldImagery", name="Boschivo").add_to(mappa)

# Aggiungere marcatori per ogni località
for nome_localita, dati_localita in localita.items():
    folium.Marker(
        location=[dati_localita["lat"], dati_localita["lng"]],
        popup=f"<b>{nome_localita}</b>",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(mappa)

    # Aggiungere sentieri separati
    for nome_sentiero, dati_sentiero in dati_localita["sentieri"].items():
        punti_sentiero = []  # Ogni sentiero ha una propria lista di punti

        for i, passaggio in enumerate(dati_sentiero["percorso"]):
            lat, lng = passaggio["lat"], passaggio["lng"]
            punti_sentiero.append([lat, lng])  # Solo per il sentiero corrente

            # Ottieni il percorso dell'immagine
            immagine = passaggio["immagine"]  # Ottieni il link immagine
            img_tag = f'<a href="{immagine}" target="_blank"><img src="{immagine}" width="100"></a>' if immagine else "(Nessuna immagine disponibile)"

            # Crea l'HTML del popup con il link immagine
            popup_html = f"""
            <b>{nome_sentiero}</b><br>
            Difficoltà: {dati_sentiero["difficolta"]}<br>
            Sequenza: {passaggio["sequenza"]}<br>
            Note: {passaggio["note"]}<br>
            {img_tag}
            """

            # Se è l'ultimo punto del sentiero, il marker è blu
            marker_color = "blue" if i == len(dati_sentiero["percorso"]) - 1 else "green"

            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(color=marker_color, icon="flag")
            ).add_to(mappa)

        # Disegnare il percorso del singolo sentiero
        folium.PolyLine(punti_sentiero, color=dati_sentiero["colore"], weight=3, opacity=0.7, tooltip=nome_sentiero).add_to(mappa)

# Aggiungi il controllo dei layer
folium.LayerControl().add_to(mappa)

# Mostrare la mappa con Streamlit
st.title("Mappa dei Sentieri")
st.write("Visualizzazione delle località e dei sentieri con passaggi.")

# Convertire la mappa in HTML e mostrarla con Streamlit
from streamlit_folium import st_folium
st_folium(mappa, width=700, height=500)
