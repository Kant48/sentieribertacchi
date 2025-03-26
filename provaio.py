import folium
import streamlit as st
import pandas as pd
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
        "immagine": row["Immagine"],  # URL dell'immagine
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
sentieribertacchi = folium.Map(location=[latzona, longzona], zoom_start=12)
folium.TileLayer("OpenStreetMap", name="Civile").add_to(sentieribertacchi)
folium.TileLayer("Esri.WorldImagery", name="Boschivo").add_to(sentieribertacchi)
sentieribertacchi.save(sentieribertacchi.html)
# Aggiunta località alla mappa
for nome_localita, dati_localita in localita.items():
    folium.Marker(
        location=[dati_localita["lat"], dati_localita["lng"]],
        popup=f"<b>{nome_localita}</b>",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(sentieri.html)

# Aggiungi il filtro per difficoltà
difficolta_opzioni = sorted(set([sentiero["difficolta"] for localita_data in localita.values() for sentiero in localita_data["sentieri"].values()]))
difficolta_opzioni.insert(0, "Tutti")  # Opzione per vedere tutti i sentieri

# Disposizione a colonne (colonna 1 per il filtro difficoltà, colonna 2 per la sentieri.html)
col1, col2 = st.columns([2, 10])  # 2 per il filtro difficoltà, 10 per la sentieri.html (maggiore spazio per la sentieri.html)

with col1:
    st.header("Seleziona la difficoltà del sentiero:")
    scelta_difficolta = st.selectbox("Scegli la difficoltà", difficolta_opzioni)

    # Mostra descrizione della difficoltà
    if scelta_difficolta != "Tutti":
        descrizione_difficolta = f"Sentieri con difficoltà {scelta_difficolta}."
        st.write(descrizione_difficolta)

with col2:
    # Aggiungi marker solo per i sentieri che corrispondono alla difficoltà selezionata
    for nome_localita, dati_localita in localita.items():
        for nome_sentiero, dati_sentiero in dati_localita["sentieri"].items():
            if scelta_difficolta == "Tutti" or dati_sentiero["difficolta"] == scelta_difficolta:
                punti_sentiero = []

                for i, passaggio in enumerate(dati_sentiero["percorso"]):
                    lat, lng = passaggio["lat"], passaggio["lng"]
                    punti_sentiero.append([lat, lng])

                    # Costruisci il popup con informazioni sul sentiero, l'immagine e le note
                    immagine_url = passaggio["immagine"]  # Otteniamo l'URL dell'immagine dalla colonna
                    immagine_html = f'<a href="{immagine_url}" target="_blank"><img src="{immagine_url}" style="max-width: 200px; max-height: 150px; display: block; margin: 0 auto;"></a>' if immagine_url else ''
                    popup_html = f"""
                    <b>{nome_sentiero}</b><br>
                    <strong>Note del passaggio:</strong><br>
                    {passaggio['note']}<br><br>
                    {immagine_html}<br>
                    <span style="color: blue; cursor: pointer;" onclick="alert('Chiama il numero: {diztelefoni[nome_localita]['numero_telefono']}');">Vuoi una guida?</span>
                    """
                    marker_color = "blue" if i == len(dati_sentiero["percorso"]) - 1 else dati_sentiero["colore"]
                    folium.Marker(
                        location=[lat, lng],
                        popup=folium.Popup(popup_html, max_width=250),
                        icon=folium.Icon(color=marker_color, icon="flag")
                    ).add_to(sentieri.html)

                folium.PolyLine(punti_sentiero, color=dati_sentiero["colore"], weight=3, opacity=0.7, tooltip=nome_sentiero).add_to(sentieri.html)

    folium.LayerControl().add_to(sentieri.html)

    # Mostrare la sentieri.html con Streamlit
    st.title("sentieri.html dei Sentieri")

    # Visualizza la sentieri.html
    st_folium(sentieri.html, width=1500, height=700)  # La sentieri.html ora occupa tutta la larghezza disponibile
