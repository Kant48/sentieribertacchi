import streamlit as st
import pandas as pd
import pydeck as pdk

# Carica il file Excel
file_path = "C:\\APP\\inputapp.xlsx"
df = pd.read_excel(file_path, engine="openpyxl")

# Sostituire le virgole con i punti nelle colonne Latitudine e Longitudine
df['Latitudine Località'] = df['Latitudine Località'].astype(str).str.replace(',', '.').astype(float)
df['Longitudine Località'] = df['Longitudine Località'].astype(str).str.replace(',', '.').astype(float)
df['Latitudine Passaggio'] = df['Latitudine Passaggio'].astype(str).str.replace(',', '.').astype(float)
df['Longitudine Passaggio'] = df['Longitudine Passaggio'].astype(str).str.replace(',', '.').astype(float)

# Mappatura difficoltà e colori
mappa_difficolta = {
    "1 - Facile anche per bambini": ("FacileB", [0, 255, 0]),  # Verde
    "2 - Facile per adulti": ("FacileA", [0, 200, 100]),  # Verde più scuro
    "3 - Impegnativo": ("mediadifficoltà", [255, 165, 0]),  # Arancione
    "4 - Impervio": ("impegnativo", [255, 69, 0]),  # Rosso
    "5 - Percorsi con ferrate": ("impervioXesperti", [139, 0, 0])  # Rosso scuro
}

# Sidebar per selezionare la difficoltà
st.sidebar.header("Che tipo di escursione vuoi fare?")
scelta_difficolta = st.sidebar.selectbox("Seleziona il livello di difficoltà", list(mappa_difficolta.keys()))

# Traduzione della scelta utente
difficolta_filtrata, colore_filtrato = mappa_difficolta[scelta_difficolta]

# Filtrare i sentieri per difficoltà
df_filtrato = df[df['Difficoltà'] == difficolta_filtrata]

# Creazione di dati per i punti dei passaggi
punti_passaggio = []

for _, riga in df_filtrato.iterrows():
    if pd.isna(riga['Latitudine Passaggio']) or pd.isna(riga['Longitudine Passaggio']):
        continue  # Salta i punti senza coordinate
    
    punti_passaggio.append({
        "lat": riga['Latitudine Passaggio'],
        "lon": riga['Longitudine Passaggio'],
        "nome": riga["Nome Sentiero"],
        "difficolta": riga["Difficoltà"],
        "note": riga["Note"],
        "colore": colore_filtrato
    })

# Creazione delle linee per collegare i passaggi di ogni sentiero
linee_sentieri = []

for nome_sentiero, gruppo in df_filtrato.groupby("Nome Sentiero"):
    gruppo = gruppo.sort_values(by=["Latitudine Passaggio", "Longitudine Passaggio"])  # Ordinare i punti
    coord_list = gruppo[['Longitudine Passaggio', 'Latitudine Passaggio']].values.tolist()
    
    if len(coord_list) > 1:  # Solo se ci sono almeno due punti
        linee_sentieri.append({
            "path": coord_list,
            "colore": colore_filtrato
        })

# Creazione del layer per i punti dei passaggi
layer_punti = pdk.Layer(
    "ScatterplotLayer",
    data=punti_passaggio,
    get_position=["lon", "lat"],
    get_color="colore",
    get_radius=100,  # Grandezza del punto
    pickable=True,  # Popup interattivo
)

# Creazione del layer per le linee dei sentieri
layer_linee = pdk.Layer(
    "PathLayer",
    data=linee_sentieri,
    get_path="path",
    get_color="colore",
    width_min_pixels=3  # Spessore della linea
)

# Creazione della mappa
view_state = pdk.ViewState(
    latitude=df_filtrato["Latitudine Località"].mean() if not df_filtrato.empty else 45.85,
    longitude=df_filtrato["Longitudine Località"].mean() if not df_filtrato.empty else 9.40,
    zoom=10,
    pitch=0
)

# Mostra la mappa con punti e linee
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/outdoors-v11",
    initial_view_state=view_state,
    layers=[layer_punti, layer_linee],
    tooltip={"html": "<b>{nome}</b><br>Difficoltà: {difficolta}<br>Note: {note}", "style": {"color": "white"}}
))

# Mostrare i dettagli dei sentieri
st.subheader(f"Sentieri con difficoltà: {scelta_difficolta}")

for sentiero in punti_passaggio:
    st.write(f"**{sentiero['nome']}** - {sentiero['difficolta']}")
    st.write(f"📌 {sentiero['lat']}, {sentiero['lon']}")
    if sentiero["note"]:
        st.write(f"📝 {sentiero['note']}")
    st.markdown("---")  # Separatore tra sentieri
