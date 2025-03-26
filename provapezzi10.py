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


localita = []  # Inizializza la lista delle località

for nome_localita, gruppo in df.groupby('Nome Località'):
	
	lat = gruppo['Latitudine Località'].iloc[0]
	lng = gruppo['Longitudine Località'].iloc[0]	
	print(f"Processing località: {nome_localita}")  # Verifica che stai entrando nel gruppo

	# Se il gruppo è vuoto, stampa un messaggio
	if gruppo.empty:
		print(f"Attenzione: Il gruppo per {nome_localita} è vuoto.")
		continue

	
	sentieri = []
	for _, riga in gruppo.iterrows():
		print(f"Processando sentiero: {riga['Nome Sentiero']}") 
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
		# Spostato il codice per il percorso immagine dentro il ciclo dove 'riga' è definito
		# Verifica se 'Percorso Immagine Passaggio' è una stringa valida
		percorso_immagine = riga['Percorso Immagine Passaggio']
			
		# Aggiungi una stampa per controllare il valore prima del replace
		print(f"Valore prima del replace: {percorso_immagine}")
			
		if pd.notna(percorso_immagine):
			percorso_immagine = str(percorso_immagine).replace("\\", "/")
			# Aggiungi una stampa per vedere se il replace è avvenuto correttamente
			print(f"Valore dopo il replace: {percorso_immagine}")
		else:
			percorso_immagine = None  # Se il valore è NaN o vuoto, imposta None

		sentiero = {
			"nome": riga['Nome Sentiero'],
			"difficolta": riga['Difficoltà'],
			"note": riga['Note'],
			"coordinata": [lat_passaggio, lon_passaggio],  # Lista con coordinate corrette
			"immagine": percorso_immagine if pd.notna(percorso_immagine) else None
		}
		sentieri.append(sentiero)
		print ("stampa lista località zero ! ")
		print(localita)
	localita.append({
		"nome": nome_localita,
		"lat": lat,
		"lng": lng,
		"sentieri": sentieri
		
	})
	print ("stampa lista località zerouno ! ")
	print(localita)
# Visualizza il risultato finale
print ("stampa lista località ! ")
print(localita)
mappa_difficolta = {
	"1 - Facile anche per bambini": ("FacileB", [0, 255, 0]),  # Verde
	"2 - Facile per adulti": ("FacileA", [0, 200, 100]),  # Verde più scuro
	"3 - Impegnativo": ("mediadifficoltà", [255, 165, 0]),  # Arancione
	"4 - Impervio": ("Impegnativo", [255, 69, 0]),  # Rosso
	"5 - Percorsi con ferrate": ("impervioXesperti", [139, 0, 0])  # Rosso scuro
}

# Sidebar per selezionare la difficoltà
st.sidebar.header("Che tipo di escursione vuoi fare?")
scelta_difficolta = st.sidebar.selectbox("Seleziona il livello di difficoltà", list(mappa_difficolta.keys()))
# Ottieni la chiave della difficoltà corrispondente
difficolta_filtrata, colore_filtrato = mappa_difficolta[scelta_difficolta]
# Debugging per verificare che il valore sia corretto
print("Difficoltà selezionata (testo completo):", scelta_difficolta)
print("Difficoltà filtrata (valore chiave):", difficolta_filtrata)
# Sidebar per selezionare il tipo di mappa
st.sidebar.header("Scegli il tipo di mappa")
scelta_mappa = st.sidebar.selectbox("Seleziona lo stile della mappa", ["Outdoor", "Satellite + Strade", "Satellite Puro"])

# Traduzione della scelta utente
difficolta_filtrata, colore_filtrato = mappa_difficolta[scelta_difficolta]
# Serializza i dati localita in formato JSON
print ("stampa lista località DUE! ")
print(localita)
localita_json = json.dumps(localita, ensure_ascii=False)

localita_json = localita_json.replace("\\", "/")
  # Evita problemi con caratteri speciali
print ("lista località jomìnson")
print(localita_json)
# Creazione della mappa HTML con i dati delle località e sentieri
# Creazione della mappa HTML con i dati delle località e sentieri
map_html = f"""
<html>
  <head>    
	<script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&callback=initMap" async defer></script>
	<style>
	  #map {{
		height: 500px;
		width: 100%;
	  }}
	  .legend {{
		background: white;
		padding: 10px;
		font-family: Arial, sans-serif;
		position: absolute;
		bottom: 20px;
		left: 20px;
		z-index: 1000;
		border-radius: 5px;
		box-shadow: 0 0 5px rgba(0,0,0,0.3);
	  }}
	  .legend div {{
		display: flex;
		align-items: center;
		margin-bottom: 5px;
	  }}
	  .legend span {{
		width: 20px;
		height: 20px;
		display: inline-block;
		margin-right: 5px;
		border: 1px solid black;
	  }}
	</style>
	<script>
	  function rgbToHex(r, g, b) {{
		return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
	  }}

	  function initMap() {{
		var map = new google.maps.Map(document.getElementById('map'), {{
		  center: {{lat: 45.89934, lng: 9.44916}}, 
		  zoom: 12,
		  mapTypeId: 'terrain'
		}});

		var mappa_difficolta = {{
		  "1 - Facile anche per bambini": ["FacileB", [0, 255, 0]],  
		  "2 - Facile per adulti": ["FacileA", [0, 200, 100]],  
		  "3 - Impegnativo": ["mediadifficoltà", [255, 165, 0]],  
		  "4 - Impervio": ["Impegnativo", [255, 69, 0]],  
		  "5 - Percorsi con ferrate": ["impervioXesperti", [139, 0, 0]]  
		}};
	   
		var locations = {localita_json};
		console.log("Località JSON:", locations);

		var scelta_difficolta = "{ difficolta_filtrata }";
		console.log(locations);
		locations.forEach(function(loc) {{
		  var markerColor = "http://maps.google.com/mapfiles/ms/icons/red-dot.png";
		  var hasFilteredPath = false;
		  var popupContent = "<b>" + loc.nome + "</b><br>";

		  loc.sentieri.forEach(function(sentiero) {{
			var sentieroColor = "gray";  
			var difficolta = sentiero.difficolta;
			var sentieroPath = [];
			if (difficolta === scelta_difficolta) {{
			  var colorRGB = mappa_difficolta[difficolta][1];
			  sentieroColor = rgbToHex(colorRGB[0], colorRGB[1], colorRGB[2]);
			  hasFilteredPath = true;
			}}
			console.log("Difficoltà sentiero:", difficolta);
			popupContent += sentiero.nome + " (" + difficolta + ")<br>";

			if (sentiero.coordinata && Array.isArray(sentiero.coordinata)) {{
				sentieroPath = sentiero.coordinata
				  .map(function(coord) {{
					var lat = parseFloat(coord[0]);
					var lng = parseFloat(coord[1]);
					return isNaN(lat) || isNaN(lng) ? null : {{ lat: lat, lng: lng }};
				  }})
				  .filter(coord => coord !== null);
				
				console.log("Sono qui 1", difficolta, "Path:", sentieroPath);

				if (sentieroPath.length > 0) {{
					new google.maps.Polyline({{
						path: sentieroPath,
						geodesic: true,
						strokeColor: sentieroColor,
						strokeOpacity: 1.0,
						strokeWeight: 3,
						map: map
					}});
					console.log("Sono qui 2", difficolta);
				}}
			}}

			console.log("Sentiero path:", sentieroPath);
			if (hasFilteredPath) {{
				markerColor = "http://maps.google.com/mapfiles/ms/icons/green-dot.png";
			}}

			var marker = new google.maps.Marker({{
				position: {{ lat: loc.lat, lng: loc.lng }},
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

		// Aggiunta della legenda
		var legend = document.createElement('div');
		legend.classList.add('legend');
		legend.innerHTML = "<b>Legenda Difficoltà</b><br>";

		for (var key in mappa_difficolta) {{
		  var colorRGB = mappa_difficolta[key][1];  
		  legend.innerHTML += `<div><span style="background: {{color}}"></span>{{key}}</div>`;

		}}

		map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(legend);
	  }}
	</script>
  </head>
  <body>
	<div id="map"></div>
  </body>
</html>
"""

# Visualizza la mappa in Streamlit
st.components.v1.html(map_html, height=600)