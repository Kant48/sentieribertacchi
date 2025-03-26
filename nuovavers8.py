import folium
import streamlit as st
import pandas as pd
import json

latzona = 45.85
longzona = 9.40

# Caricamento del file Excel
file_path = r"C:\APP\inputapp.xlsx"
df = pd.read_excel(file_path)

# Sostituisci la virgola con il punto per le colonne Latitudine e Longitudine
for col in ['Latitudine Località', 'Longitudine Località', 'Latitudine Passaggio', 'Longitudine Passaggio']:
    df[col] = df[col].apply(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Dizionario delle località
localita = {}
diztelefoni = {}

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
    colore_sentiero = row["colore sentiero"]

    # Se il sentiero non esiste in questa località, lo creiamo
    if nome_sentiero not in localita[nome_localita]["sentieri"]:
        localita[nome_localita]["sentieri"][nome_sentiero] = {
            "difficolta": row["Difficoltà"],
            "colore": colore_sentiero,
            "percorso": []
        }

    # Aggiungiamo il passaggio ordinato per sequenza
    localita[nome_localita]["sentieri"][nome_sentiero]["percorso"].append({
        "sequenza": row["Sequenza"],
        "lat": row["Latitudine Passaggio"],
        "lng": row["Longitudine Passaggio"],
        "note": row["Note"],
        "immagine": row["Immagine"]
    })

    # Dizionario per il numero di telefono e le note pratiche
    diztelefoni[nome_localita] = {
        "numero_telefono": row["Numero Telefono"],
        "note": row.get("NOTELOC", "")
    }

# Riordinare i passaggi per ogni sentiero in base alla sequenza
for nome_localita in localita:
    for nome_sentiero in localita[nome_localita]["sentieri"]:
        localita[nome_localita]["sentieri"][nome_sentiero]["percorso"].sort(key=lambda x: x["sequenza"])

# Creazione della mappa
mappa = folium.Map(location=[latzona, longzona], zoom_start=12)
folium.TileLayer("OpenStreetMap", name="Civile").add_to(mappa)
folium.TileLayer("Esri.WorldImagery", name="Boschivo").add_to(mappa)

# Convertire dizionario telefoni in JSON
diztelefoni_json = json.dumps(diztelefoni)

# Aggiungere marcatori
for nome_localita, dati_localita in localita.items():
    folium.Marker(
        location=[dati_localita["lat"], dati_localita["lng"]],
        popup=f"<b>{nome_localita}</b>",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(mappa)

    # Aggiungere sentieri
    for nome_sentiero, dati_sentiero in dati_localita["sentieri"].items():
        punti_sentiero = []
        for i, passaggio in enumerate(dati_sentiero["percorso"]):
            lat, lng = passaggio["lat"], passaggio["lng"]
            punti_sentiero.append([lat, lng])

            # Crea l'HTML del popup con immagine
            immagine = passaggio["immagine"]
            img_tag = f'<a href="{immagine}" target="_blank"><img src="{immagine}" width="100"></a>' if immagine else "(Nessuna immagine disponibile)"

            # Crea il popup HTML con lo script incluso
            popup_html = f"""
            <b style="color: blue;">{nome_localita}</b><br>
            <b>{nome_sentiero}</b><br>
            Difficoltà: {dati_sentiero["difficolta"]}<br>
            Sequenza: {passaggio["sequenza"]}<br>
            Note: {passaggio["note"]}<br>
            {img_tag}<br>
            <a href="javascript:void(0);" onclick="showAlert('{nome_localita}')">Vuoi una guida?</a>

            <script>
                var numeri = {diztelefoni_json};

                function showAlert(localita) {{
                    if (numeri[localita]) {{
                        alert('Chiama il numero: ' + numeri[localita].numero_telefono + ' per una guida!');
                        if (numeri[localita].note) {{
                            alert('Note pratiche: ' + numeri[localita].note);
                        }}
                    }} else {{
                        alert('Numero di telefono non disponibile per questa località.');
                    }}
                }}
            </script>
            """

            # Imposta colore del marker
            marker_color = "blue" if i == len(dati_sentiero["percorso"]) - 1 else dati_sentiero["colore"]

            # Aggiungi marker del passaggio
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(color=marker_color, icon="flag")
            ).add_to(mappa)

        # Disegnare il percorso del sentiero
        folium.PolyLine(punti_sentiero, color=dati_sentiero["colore"], weight=3, opacity=0.7, tooltip=nome_sentiero).add_to(mappa)

# Aggiungi il controllo dei layer
folium.LayerControl().add_to(mappa)

# Mostrare la mappa con Streamlit
st.title("Mappa dei Sentieri")
st.write("Visualizzazione delle località e dei sentieri con passaggi.")

# Convertire la mappa in HTML e mostrarla con Streamlit
from streamlit_folium import st_folium
st_folium(mappa, width=700, height=500)
