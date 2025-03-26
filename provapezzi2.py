import streamlit as st
import pandas as pd

# Inserisci la tua API Key qui
GOOGLE_MAPS_API_KEY = "AIzaSyDDVLkAq-Sy3ZCmHaFcKZJSAxYIVn9UMe4"

# Coordinate iniziali della mappa
latitude = 45.85
longitude = 9.40

# Carica il file Excel
file_path = "C:\\APP\\inputapp.xlsx"
df = pd.read_excel(file_path, engine="openpyxl")

# Sostituire le virgole con i punti nelle colonne Latitudine e Longitudine
df['Latitudine Località'] = df['Latitudine Località'].astype(str).str.replace(',', '.').astype(float)
df['Longitudine Località'] = df['Longitudine Località'].astype(str).str.replace(',', '.').astype(float)
df['Latitudine Passaggio'] = df['Latitudine Passaggio'].astype(str).str.replace(',', '.').astype(float)
df['Longitudine Passaggio'] = df['Longitudine Passaggio'].astype(str).str.replace(',', '.').astype(float)

# Organizza le località in una lista
localita = []

for nome_localita, gruppo in df.groupby('Nome Località'):
    lat = gruppo['Latitudine Località'].iloc[0]
    lng = gruppo['Longitudine Località'].iloc[0]
    sentieri = []
    
    for _, riga in gruppo.iterrows():
        if pd.isna(riga['Latitudine Passaggio']) or pd.isna(riga['Longitudine Passaggio']):
            continue  # Salta questa riga e passa alla successiva

        try:
            lat_passaggio = float(str(riga['Latitudine Passaggio']).replace(",", "."))
            lon_passaggio = float(str(riga['Longitudine Passaggio']).replace(",", "."))
        except ValueError:
            continue  # Salta questa riga e passa alla successiva

        sentiero = {
            "nome": riga['Nome Sentiero'],
            "difficolta": riga['Difficoltà'],
            "note": riga['Note'],
            "coordinata": [lat_passaggio, lon_passaggio],
            "immagine": riga['Percorso Immagine Passaggio'] if pd.notna(riga['Percorso Immagine Passaggio']) else None
        }
        sentieri.append(sentiero)
    
    localita.append({
        "nome": nome_localita,
        "lat": lat,
        "lng": lng,
        "sentieri": sentieri
    })

# Mappatura difficoltà
mappa_difficolta = {
    "1 - Facile anche per bambini": "FacileB",
    "2 - Facile per adulti": "FacileA",
    "3 - Impegnativo": "mediadifficoltà",
    "4 - Impervio": "impegnativo",
    "5 - Percorsi con ferrate": "impervioXesperti"
}

# Sidebar per selezionare la difficoltà
st.sidebar.header("Che tipo di escursione vuoi fare ?")
scelta_difficolta = st.sidebar.selectbox("seleziona il livello di difficolta", list(mappa_difficolta.keys()))

# Traduzione della scelta utente nella difficoltà
difficolta_filtrata = mappa_difficolta[scelta_difficolta]

# Mappatura dei dati in formato JSON
localita_json = f"""
{localita}
"""

# Visualizza i dati delle località in Streamlit
st.write("Dati delle località:", localita_json)


# Costruzione della mappa in HTML
map_html = f"""
<!DOCTYPE html>
<html>
  <head>
    <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&callback=initMap" async defer></script>
    <script>
      function initMap() {{
        var map = new google.maps.Map(document.getElementById('map'), {{
          center: {{lat: {latitude}, lng: {longitude} }},
          zoom: 12,
          mapTypeId: 'terrain'
        }});

        var locations = {localita};

        locations.forEach(function(loc) {{
          var marker = new google.maps.Marker({{
            position: {{lat: loc.lat, lng: loc.lng }},
            map: map,
            title: loc.nome
          }});

          var infoWindow = new google.maps.InfoWindow({{
            content: "<b>" + loc.nome + "</b><br>"
          }});

          marker.addListener('click', function() {{
            infoWindow.open(map, marker);
          }});
        }});
      }}
    </script>
  </head>
  <body>
    <div id="map" style="height: 500px; width: 100%;"></div>
  </body>
</html>
"""
