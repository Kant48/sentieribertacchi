import streamlit as st
import pandas as pd
import pydeck as pdk
import base64
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

# Sidebar per selezionare il tipo di mappa
st.sidebar.header("Scegli il tipo di mappa")
scelta_mappa = st.sidebar.selectbox("Seleziona lo stile della mappa", ["Outdoor", "Satellite + Strade", "Satellite Puro"])

# Traduzione della scelta utente
difficolta_filtrata, colore_filtrato = mappa_difficolta[scelta_difficolta]

# Mappatura degli stili di mappa
mappa_stili = {
    "Outdoor": "mapbox://styles/mapbox/outdoors-v11",
    "Satellite + Strade": "mapbox://styles/mapbox/satellite-streets-v11",
    "Satellite Puro": "mapbox://styles/mapbox/satellite-v9"
}

# Stile selezionato dall'utente
stile_mappa = mappa_stili[scelta_mappa]

# Filtrare i sentieri per difficoltà
df_filtrato = df[df['Difficoltà'] == difficolta_filtrata]

# Creazione di dati per i punti dei passaggi
punti_passaggio = []

for _, riga in df_filtrato.iterrows():
    if pd.isna(riga['Latitudine Passaggio']) or pd.isna(riga['Longitudine Passaggio']):
        continue  # Salta i punti senza coordinate
    
    immagine_html = ""
    if pd.notna(riga["Percorso Immagine Passaggio"]):
        immagine_html = f'<br><img src="{riga["Percorso Immagine Passaggio"]}" width="200px">'

    punti_passaggio.append({
        "lat": riga['Latitudine Passaggio'],
        "lon": riga['Longitudine Passaggio'],
        "nome": riga["Nome Sentiero"],
        "difficolta": riga["Difficoltà"],
        "note": riga["Note"],
        "immagine": immagine_html,
        "colore": colore_filtrato
    })

# Creazione delle linee per collegare i passaggi di ogni sentiero
linee_sentieri = []

for nome_sentiero, gruppo in df_filtrato.groupby("Nome Sentiero"):
    # Assicuriamoci che i punti siano ordinati nel giusto ordine
    gruppo = gruppo.sort_values(by="Sequenza")  # Ordina in base ordine dei passaggi
    coord_list = gruppo[['Longitudine Passaggio', 'Latitudine Passaggio']].values.tolist()
    
    if len(coord_list) > 1:  # Solo se ci sono almeno due punti
        linee_sentieri.append({
            "path": coord_list,
            "colore": colore_filtrato
        })

# Creazione dei segnaposti per le località (usiamo un'icona personalizzata)
# Funzione per convertire SVG in Base64
def svg_to_base64(svg_code):
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg_code.encode('utf-8')).decode('utf-8')

# Icone SVG per le località: goccia o triangolo rovesciato
svg_goccia = '<svg width="50" height="50" xmlns="http://www.w3.org/2000/svg"><circle cx="25" cy="25" r="20" fill="red"/></svg>'
svg_triangolo = '<svg width="50" height="50" xmlns="http://www.w3.org/2000/svg"><polygon points="25,5 45,45 5,45" fill="blue"/></svg>'

# Codifica gli SVG come immagini Base64
base64_goccia = svg_to_base64(svg_goccia)
base64_triangolo = svg_to_base64(svg_triangolo)

# Crea le icone per ogni località (alternando goccia e triangolo)
icone_localita = [base64_goccia if i % 2 == 0 else base64_triangolo for i in range(len(df))]

# Creazione dei punti per le località con le icone
localita_punti = [
    {"lat": riga["Latitudine Località"], "lon": riga["Longitudine Località"], "nome": riga["Nome Località"], "icona": icona}
    for i, (index, riga) in enumerate(df.drop_duplicates(subset=["Nome Località"]).iterrows())
    for icona in [icone_localita[i]]  # Associa l'icona giusta per la località
]

# Controlla che la lista dei dati delle località e le icone siano corrette
st.write(localita_punti)  # Aggiungi questa linea per vedere cosa contiene `localita_punti`

# Layer per i punti delle località con le icone
layer_punti = pdk.Layer(
    "IconLayer",
    localita_punti,
    get_position=["lon", "lat"],
    get_icon={"url": "icona", "width": 50, "height": 50, "anchorY": 50},
    get_icon_size=50,  # Imposta la dimensione dell'icona
    pickable=True,
    auto_highlight=True,
)

# Layer per le linee dei sentieri
layer_linee = pdk.Layer(
    "PathLayer",
    data=linee_sentieri,
    get_path="path",
    get_color="colore",
    width_min_pixels=3  # Spessore della linea
)

# Layer per le località (usiamo un'icona personalizzata)
layer_localita = pdk.Layer(
    "IconLayer",
    data=localita_punti,
    get_position=["lon", "lat"],
    get_icon="marker",
    get_size=50,
    get_color=[255, 0, 0],  # Rosso per la località
										  
    pickable=True
)

# Creazione della mappa
view_state = pdk.ViewState(
    latitude=df["Latitudine Località"].mean(),
    longitude=df["Longitudine Località"].mean(),
    zoom=10,
    pitch=0
)

# Mostra la mappa con punti, linee e località
st.pydeck_chart(pdk.Deck(
    map_style=stile_mappa,
    initial_view_state=view_state,
    layers=[layer_localita, layer_punti, layer_linee],
    tooltip={
        "html": "<b>{nome}</b><br>Difficoltà: {difficolta}<br>Note: {note}{immagine}",
        "style": {"color": "white"}
    }
))

# Mostrare i dettagli dei sentieri
st.subheader(f"Sentieri con difficoltà: {scelta_difficolta}")

for sentiero in punti_passaggio:
    st.write(f"**{sentiero['nome']}** - {sentiero['difficolta']}")
    st.write(f"📌 {sentiero['lat']}, {sentiero['lon']}")
    if sentiero["note"]:
        st.write(f"📝 {sentiero['note']}")
    if sentiero["immagine"]:
        st.image(sentiero["immagine"].replace('<br><img src="', "").replace('" width="200px">', ""), width=300)
    st.markdown("---")  # Separatore tra sentieri
