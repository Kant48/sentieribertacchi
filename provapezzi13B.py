import streamlit as st
import pandas as pd
import pydeck as pdk
import base64
import json
# Inserisci la tua API Key qui
GOOGLE_MAPS_API_KEY = "AIzaSyDDVLkAq-Sy3ZCmHaFcKZJSAxYIVn9UMe4"
 # Coordinate iniziali della mappa
latitude = 45.85
longitudine = 9.40

# Carica il file Excel
file_path = "C:\\APP\\inputapp.xlsx"
df = pd.read_excel(file_path, engine="openpyxl")
print ("stampa i nomi colonne")
print(df.columns)
# Converti colonne in numerico per evitare errori di ordinamento
df['prog'] = pd.to_numeric(df['prog'], errors='coerce')
df['Sequenza'] = pd.to_numeric(df['Sequenza'], errors='coerce')

print("DF PRIMA sort:")
print(df.to_string())  # Mostra tutte le colonne e righe
# Controlla se le colonne 'prog' e 'Sequenza' esistono prima di ordinare
if 'prog' in df.columns and 'Sequenza' in df.columns:
	# Ordina i passaggi per 'prog' e 'Sequenza'
	df = df.sort_values(by=['prog', 'Sequenza'], na_position='last')
else:
	print("Attenzione: Le colonne 'prog' e/o 'Sequenza' non sono presenti nel DataFrame.")
print("DF DOPO sort:")
print(df.to_string())  # Mostra tutte le colonne e righe

# Verifica e correggi le coordinate nei dataframe (sostituisce la virgola con il punto)
df['Latitudine Località'] = df['Latitudine Località'].astype(str).str.replace(',', '.')
df['Longitudine Località'] = df['Longitudine Località'].astype(str).str.replace(',', '.')
# Converti le coordinate in valori numerici
df['Latitudine Località'] = pd.to_numeric(df['Latitudine Località'], errors='coerce')
df['Longitudine Località'] = pd.to_numeric(df['Longitudine Località'], errors='coerce')

df['Latitudine Passaggio'] = df['Latitudine Passaggio'].astype(str).str.replace(',', '.')
df['Longitudine Passaggio'] = df['Longitudine Passaggio'].astype(str).str.replace(',', '.')
df['Latitudine Passaggio'] = pd.to_numeric(df['Latitudine Passaggio'], errors='coerce')
df['Longitudine Passaggio'] = pd.to_numeric(df['Longitudine Passaggio'], errors='coerce')


# Lista per memorizzare le località
localita = []

# Raggruppa per nome della località
for nome_localita, gruppo in df.groupby('Nome Località'):
	lat = gruppo['Latitudine Località'].iloc[0]
	lng = gruppo['Longitudine Località'].iloc[0]
	print(f"Processing località: {nome_localita}")  # Verifica che stai entrando nel gruppo

	# Se il gruppo è vuoto, stampa un messaggio
	if gruppo.empty:
		print(f"Attenzione: Il gruppo per {nome_localita} è vuoto.")
		continue

	sentieri = []  # Lista che conterrà i sentieri per questa località

	# Raggruppa per nome del sentiero
	for nome_sentiero, gruppo_sentiero in gruppo.groupby('prog'):
		print(f"Processando sentiero: {nome_sentiero}")
		

		# Lista per memorizzare i passaggi ordinati di questo sentiero
		sentiero = []

		# Itera sui passaggi del sentiero
		for _, riga in gruppo_sentiero.iterrows():
			print(f"Elaborando passaggio: {riga['Nome Sentiero']}, Sequenza: {riga['Sequenza']}")

			# Gestisci eventuali valori mancanti per latitudine e longitudine
			if pd.isna(riga['Latitudine Passaggio']) or pd.isna(riga['Longitudine Passaggio']):
				print(f"Attenzione: Coordinate mancanti per {riga['Nome Sentiero']} - Riga saltata")
				continue  # Salta questa riga e passa alla successiva

			try:
				# Converti e sostituisci la virgola con il punto
				lat_passaggio = float(str(riga['Latitudine Passaggio']).replace(",", "."))
				lon_passaggio = float(str(riga['Longitudine Passaggio']).replace(",", "."))
			except ValueError as e:
				print(f"Errore nella conversione delle coordinate per {riga['Nome Sentiero']}: {e}")
				continue  # Salta questa riga e passa alla successiva

			# Verifica se 'Percorso Immagine Passaggio' è una stringa valida
			percorso_immagine = riga['Percorso Immagine Passaggio']
			if pd.notna(percorso_immagine):
				percorso_immagine = str(percorso_immagine).replace("\\", "/")
			else:
				percorso_immagine = None  # Se il valore è NaN o vuoto, imposta None

			# Aggiungi il passaggio alla lista di sentieri
			passaggio = {
				"nome": riga['Nome Sentiero'],
				"difficolta": riga['Difficoltà'],
				"note": riga['Note'],
				"coordinata": [lat_passaggio, lon_passaggio],  # Lista con coordinate corrette
				"immagine": percorso_immagine if pd.notna(percorso_immagine) else None
			}

			sentiero.append(passaggio)

		# Aggiungi il sentiero (con il percorso ordinato) alla lista delle località
		localita.append({
			"nome": nome_localita,
			"lat": lat,  # Usa la latitudine di base (potresti volerla calcolare)
			"lng": lng,  # Usa la longitudine di base (potresti volerla calcolare)
			"sentieri": sentiero  # Lista dei passaggi del sentiero ordinata
		})


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
mappa_difficolta = json.dumps(mappa_difficolta, ensure_ascii=False);
  # Evita problemi con caratteri speciali
print ("lista località jomìnson")
print(localita_json)
print ("mappa difficolta json")
print(mappa_difficolta)  # Controlla l'output nella console Python
# Creazione della mappa HTML con i dati delle località e sentieri
# Creazione della mappa HTML con i dati delle località e sentieri
# Assicurati che mappa_difficolta e localita_json siano già definiti come dizionari in Python
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
  </head>
  <body>
	<div id="map"></div>
	
	<!-- Legenda dinamica -->
	<div class="legend" id="legend">
	  <h3>Legenda</h3>
	</div>

	<script>
	  function initMap() {{
		var map = new google.maps.Map(document.getElementById('map'), {{
		  center: {{ lat: {latitude}, lng: {longitudine} }},
		  zoom: 12,
		  mapTypeId: 'terrain'
		}});
		console.log("Mappa inizializzata correttamente");
	  }}
	</script>

	<script>
	  // Dati della mappa di difficoltà (da Python tramite Jinja)
   
	  var mappa_difficolta = {{toJson( mappa_difficolta) }};
  
	  // Aggiungi la legenda dinamicamente
	  var legendDiv = document.getElementById('legend');
	  
	  for (var key in mappa_difficolta) {{
		if (mappa_difficolta.hasOwnProperty(key)) {{
		  var legendItem = document.createElement('div');
		  var colorBox = document.createElement('span');
		  
		  // Imposta il colore della box usando il valore rgb dalla mappa di difficoltà
		  colorBox.style.backgroundColor = "rgb(" + mappa_difficolta[key][1].join(",") + ")";
		  
		  // Aggiungi il testo accanto al colore; qui usiamo ${{
		  
		  legendItem.innerHTML = `<strong>${{key}}</strong> - ${{mappa_difficolta[key][0]}}`;
		  
		  // Aggiungi il colore e il testo nella legenda
		  legendItem.insertBefore(colorBox, legendItem.firstChild);
		  legendDiv.appendChild(legendItem);
		}}
	  }}
	</script>

  </body>
</html>
"""
# Visualizza la mappa in Streamlit
st.components.v1.html(map_html, height=600)