import streamlit as st
import pandas as pd
import pydeck as pdk
import base64
import json
# Inserisci la tua API Key qui
GOOGLE_MAPS_API_KEY = "AIzaSyDDVLkAq-Sy3ZCmHaFcKZJSAxYIVn9UMe4"

 # Coordinate iniziali della mappa
latitude = 45.85
longitude = 9.40
# Carica il file Excel
file_path = "C:\\APP\\inputapp.xlsx"
df = pd.read_excel(file_path, engine="openpyxl")
print ("stampa i nomi colonne")
print(df.columns)


# Sostituire le virgole con i punti nelle colonne Latitudine e Longitudine


# Verifica e correggi le coordinate nei dataframe
df['Latitudine Località'] = pd.to_numeric(df['Latitudine Località'], errors='coerce')
df['Longitudine Località'] = pd.to_numeric(df['Longitudine Località'], errors='coerce')
df['Latitudine Passaggio'] = pd.to_numeric(df['Latitudine Passaggio'], errors='coerce')
df['Longitudine Passaggio'] = pd.to_numeric(df['Longitudine Passaggio'], errors='coerce')

# Filtra eventuali valori non validi (NaN)
df = df.dropna(subset=['Latitudine Località', 'Longitudine Località', 'Latitudine Passaggio', 'Longitudine Passaggio'])

# Assicurati che le coordinate siano finite (non infini)
df = df[(df['Latitudine Località'].apply(pd.api.types.is_numeric_dtype)) & 
        (df['Longitudine Località'].apply(pd.api.types.is_numeric_dtype)) & 
        (df['Latitudine Passaggio'].apply(pd.api.types.is_numeric_dtype)) & 
        (df['Longitudine Passaggio'].apply(pd.api.types.is_numeric_dtype))]



localita = []  # Inizializza la lista delle località

for nome_localita, gruppo in df.groupby('Nome Località'):
	lat = gruppo['Latitudine Località'].iloc[0]
	lng = gruppo['Longitudine Località'].iloc[0]
	percorso_immagine = gruppo['Percorso Immagine Passaggio'].iloc[0]
	
	sentieri = []
	for _, riga in gruppo.iterrows():
		# Gestisci eventuali valori mancanti per latitudine e longitudine
		if pd.isna(riga['Latitudine Passaggio']) or pd.isna(riga['Longitudine Passaggio']):
			print(f"Attenzione: Coordinate mancanti per {riga['Nome Sentiero']} - Riga saltata")
			continue  # Salta questa riga e passa alla successiva

		try:
			lat_passaggio = float(str(riga['Latitudine Passaggio']).replace(",", "."))  # Converti e sostituisci la virgola
			lon_passaggio = float(str(riga['Longitudine Passaggio']).replace(",", "."))
		except ValueError as e:
			print(f"Errore nella conversione delle coordinate per {riga['Nome Sentiero']}: {e}")
			continue  # Salta questa riga e passa alla successiva

		sentiero = {
			"nome": riga['Nome Sentiero'],
			"difficolta": riga['Difficoltà'],
			"note": riga['Note'],
			"coordinata": [lat_passaggio, lon_passaggio],  # Lista con coordinate corrette
			"immagine": riga['Percorso Immagine Passaggio'] if pd.notna(riga['Percorso Immagine Passaggio']) else None
		}
		sentieri.append(sentiero)
	
	localita.append({
		"nome": nome_localita,
		"lat": lat,
		"lng": lng,
		"sentieri": sentieri
		
	})

# Visualizza il risultato finale
print ("stampa lista località ! ")
print(localita)
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
# Serializza i dati localita in formato JSON
localita_json = json.dumps(localita)
print ("lista località jomìnson")
print(localita_json)
# Creazione della mappa HTML con i dati delle località e sentieri
# Creazione della mappa HTML con i dati delle località e sentieri
map_html = f"""
<html>
  <head>
    <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&callback=initMap" async defer></script>
    <script>
      function rgbToHex(r, g, b) {{
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
      }}

      function initMap() {{
        var map = new google.maps.Map(document.getElementById('map'), {{
          center: {{lat: 45.89934, lng: 9.44916}},  // Posizione centrale (esempio)
          zoom: 12,
          mapTypeId: 'terrain'
        }});

        var mappa_difficolta = {{
          "1 - Facile anche per bambini": ["FacileB", [0, 255, 0]],  // Verde
          "2 - Facile per adulti": ["FacileA", [0, 200, 100]],  // Verde più scuro
          "3 - Impegnativo": ["mediadifficoltà", [255, 165, 0]],  // Arancione
          "4 - Impervio": ["impegnativo", [255, 69, 0]],  // Rosso
          "5 - Percorsi con ferrate": ["impervioXesperti", [139, 0, 0]]  // Rosso scuro
        }};

        var sentieriLayer = [];
        var locations = {localita_json};  // Dati delle località JSON
        var scelta_difficolta = "{scelta_difficolta}";  // Difficoltà scelta dall'utente

        locations.forEach(function(loc) {{
          var markerColor = "http://maps.google.com/mapfiles/ms/icons/red-dot.png";
          var hasFilteredPath = false;
          var popupContent = "<b>" + loc.nome + "</b><br>";

          loc.sentieri.forEach(function(sentiero) {{
            var sentieroColor;
            var difficolta = sentiero.difficolta;

            // Se la difficoltà del sentiero corrisponde a quella selezionata
            if (difficolta === scelta_difficolta) {{
              // Usa il colore RGB dalla mappa delle difficoltà
              var colorRGB = mappa_difficolta[difficolta][1];
              sentieroColor = rgbToHex(colorRGB[0], colorRGB[1], colorRGB[2]);
              hasFilteredPath = true;
            }} else {{
              sentieroColor = "gray";  // Colore di default se non corrisponde
            }}

            popupContent += sentiero.nome + " (" + sentiero.difficolta + ")<br>";

            // Verifica le coordinate
            var sentieroPath = sentiero.coordinata.map(function(coord) {{
              var lat = coord[0];
              var lng = coord[1];

              // Aggiungi il controllo per assicurarti che lat e lng siano numeri validi
              if (isNaN(lat) || isNaN(lng) || !isFinite(lat) || !isFinite(lng)) {{
                console.log("Errore: coordinate non valide per il sentiero", sentiero.nome, "Lat:", lat, "Lng:", lng);
                return null;  // Ritorna null se le coordinate non sono valide
              }}

              return {{lat: lat, lng: lng}};  // Restituisce il punto se le coordinate sono valide
            }}).filter(function(coord) {{
              return coord !== null;  // Filtra eventuali coordinate invalide (null)
            }});

            console.log("Sentiero path:", sentieroPath);  // Debug: stampa le coordinate del sentiero

            if (sentieroPath.length > 0) {{
              var sentieroLine = new google.maps.Polyline({{
                path: sentieroPath,  // Corretto: path deve essere definito in questo contesto JavaScript
                geodesic: true,
                strokeColor: sentieroColor,
                strokeOpacity: 1.0,
                strokeWeight: 3
              }});
              sentieriLayer.push(sentieroLine);
              sentieroLine.setMap(map);
            }}
          }});

          if (hasFilteredPath) {{
            markerColor = "http://maps.google.com/mapfiles/ms/icons/" + mappa_difficolta[scelta_difficolta][1] + "-dot.png";
          }}

          var marker = new google.maps.Marker({{
            position: {{lat: loc.lat, lng: loc.lng}},
            map: map,
            title: loc.nome,
            icon: markerColor
          }});

          var infoWindow = new google.maps.InfoWindow({{
            content: popupContent
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

# Visualizza la mappa in Streamlit
st.components.v1.html(map_html, height=600)
