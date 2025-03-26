import folium
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from io import BytesIO
from docx import Document

# Creazione della mappa
mappa = folium.Map(location=[45.85, 9.40], zoom_start=12)
folium.TileLayer("OpenStreetMap", name="Civile").add_to(mappa)
folium.TileLayer("Esri.WorldImagery", name="Boschivo").add_to(mappa)

# CSS per rimuovere bordi e forzare larghezza massima
st.markdown(
	"""
	<style>
										   
		.st-emotion-cache-1kyxreq, .block-container {
			padding: 0;
			margin: 150;
			max-width: 100%;
			margin-top: 20px;
		}

# Aggiungi il CSS personalizzato per nascondere il banner


		 .css-1l7jqpk {display: none;}  /* Nasconde il banner di avviso */
		 .css-1to5xxz {display: none;}  /* Nasconde eventuali altri banner */

	unsafe_allow_html=True
		)

# Codice Streamlit per la tua app...
	   
										 
		html, body {
			margin: 200;
			padding: 0;
			margin-top: 20px;
  
				
			  
			height: 100%;
			width: 100%;
	   
		
			overflow: hidden;
		}

																	  
										 
						 
		 
	</style>
	""",
	unsafe_allow_html=True
)
# Carico note generali
def carica_note_generali():
	doc_path = "NOTEGENERALI.docx"
	doc = Document(doc_path)
	# Unisci il testo di tutti i paragrafi
	testo_completo = "\n".join([para.text for para in doc.paragraphs])
	return testo_completo  # Ritorna il testo del documento

note_generali = carica_note_generali()  
# Centro mappa
latzona = 45.85
longzona = 9.40

# Caricamento del file Excel
#file_path = r"C:\APP\inputapp.xlsx"
file_path = "inputapp.xlsx"  # Nome file senza percorso
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
	
	# Verifica se la località è già nel dizionario
	if nome_localita not in localita:
		localita[nome_localita] = {
			"lat": row["Latitudine Località"],
			"lng": row["Longitudine Località"],
			"sentieri": {},
			"descrizione": row.get("NOTELOC", "Nessuna descrizione"),  # Aggiungi descrizione
			"Note": row.get("Note", "Nessuna nota"),  # Aggiungi note
			"immagine": row.get("Immagine", "")  # Aggiungi immagine
		}
	else:
		# Se la località esiste già, aggiorna solo i dati aggiuntivi se non sono già presenti
		localita[nome_localita]["descrizione"] = localita[nome_localita].get("descrizione", row.get("NOTELOC", "Nessuna descrizione"))
		localita[nome_localita]["Note"] = localita[nome_localita].get("Note", row.get("Note", "Nessuna nota"))
		localita[nome_localita]["immagine"] = localita[nome_localita].get("immagine", row.get("Immagine", ""))
	
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
print(localita)

# Riordinare i passaggi per sequenza
for nome_localita in localita:
	for nome_sentiero in localita[nome_localita]["sentieri"]:
		localita[nome_localita]["sentieri"][nome_sentiero]["percorso"].sort(key=lambda x: x["sequenza"])


# Aggiungi il filtro per difficoltà
difficolta_opzioni = sorted(set([sentiero["difficolta"] for localita_data in localita.values() for sentiero in localita_data["sentieri"].values()]))
difficolta_opzioni.insert(0, "Tutti")  # Opzione per vedere tutti i sentieri
# Sezione delle Note Generali sopra le colonne
st.title("Sentieri e Note Generali")

# Mostra le note generali in un expander per leggibilità
with st.expander("📜 Note Generali", expanded=True):
    st.write(note_generali)

# Disposizione a colonne (colonna 1 per il filtro difficoltà, colonna 2 per la mappa)
col1, col2 = st.columns([2, 10])  # 2 per il filtro difficoltà, 10 per la mappa (maggiore spazio per la mappa)

# Filtro difficoltà nella colonna di sinistra
with col1:
    st.header("Seleziona la difficoltà del sentiero:")
    difficolta_opzioni = sorted(set([s["difficolta"] for l in localita.values() for s in l["sentieri"].values()]))
    difficolta_opzioni.insert(0, "Tutti")
    scelta_difficolta = st.selectbox("Scegli la difficoltà", difficolta_opzioni)
with col2:
	# Aggiungi marker solo per i sentieri che corrispondono alla difficoltà selezionata
	for nome_localita, dati_localita in localita.items():
		# Estrai posizione della località (ipotizzo sia nel dizionario, se non c'è specifica dove prenderla)
		lat_localita = dati_localita.get("lat", 0)
		lng_localita = dati_localita.get("lng", 0)
		
		#Definizione del popup per la località
		descrizione_localita = dati_localita.get('descrizione', 'Nessuna descrizione')
		note_localita = dati_localita.get('Note', 'Nessuna nota')
		popup_localita = f"<b>{nome_localita}</b><br>{descrizione_localita}</b><br>{note_localita}"
		print(f"Popup sentieri {nome_localita}: {popup_localita}")
		# Icona a goccia per la località
		folium.Marker(
			location=[lat_localita, lng_localita],
			popup=folium.Popup(popup_localita, max_width=650),
			icon=folium.Icon(color="blue", icon="info-sign")
		).add_to(mappa)
		
		# Ciclo sui sentieri della località
		for nome_sentiero, dati_sentiero in dati_localita["sentieri"].items():
			if scelta_difficolta == "Tutti" or dati_sentiero["difficolta"] == scelta_difficolta:
				punti_sentiero = []

				for i, passaggio in enumerate(dati_sentiero["percorso"]):
					lat, lng = passaggio["lat"], passaggio["lng"]
					punti_sentiero.append([lat, lng])

					# Estrai dati per popup
					immagine_url = passaggio.get("immagine", "")
					note = passaggio.get("note", "Nessuna nota")
					numero_telefono = diztelefoni.get(nome_localita, {}).get("numero_telefono", "Non disponibile")
					
					# Crea HTML del popup
					immagine_html = f'<a href="{immagine_url}" target="_blank"><img src="{immagine_url}" style="max-width: 200px; max-height: 150px; display: block; margin: 0 auto;"></a>' if immagine_url else '<i>Nessuna immagine</i>'
					popup_html = f"""
					<b>{nome_sentiero}</b><br>
					<strong>Note del passaggio:</strong><br>
					{note}<br><br>
					{immagine_html}<br>
					<span style="color: blue; cursor: pointer;" onclick="alert('Chiama il numero: {numero_telefono}');">Vuoi una guida?</span>
					"""

					# Colore del cerchio basato sul sentiero
					colore_cerchio = dati_sentiero["colore"]
					
					# Cerchiolino colorato per i passaggi
					#folium.CircleMarker(
					#	location=[lat, lng],
					#	radius=10,  
					#	color="white",
					#	fill=False,
					#	weight=3

					#).add_to(mappa)
					# Cerchio interno (colorato)
					# Cerchio esterno bianco
					folium.CircleMarker(
						location=[lat, lng],
						radius=8,                   # Raggio totale del cerchio
						color="white",               # Bordo bianco
						popup=folium.Popup(popup_html, max_width=650),
						fill=True,                   # Riempito con colore
						fill_color=colore_cerchio,   # Colore interno (dinamico)
						fill_opacity=1            # Opacità del riempimento
						  # Popup visibile al click
						#tooltip=f"Passaggio {passaggio['sequenza']}"    # Tooltip visibile al passaggio del mouse
					).add_to(mappa)
					folium.Marker( 
						location=[lat, lng],
						icon=folium.DivIcon(
							html=f"""
							<div style="
								font-family: Arial;
								font-size:14px;
								color: black;
								font-weight: bold;
								background-color: rgba(255,255,255,0.5);
								border-radius: 30%;
								padding: 2px 6px;
								text-align: high;
								">
								{passaggio["sequenza"]}
							</div>
							"""),
							popup=folium.Popup(popup_html, max_width=650
						
					)).add_to(mappa)




				# Traccia la linea del sentiero
				folium.PolyLine(
					punti_sentiero, 
					color=dati_sentiero["colore"], 
					weight=3, 
					opacity=0.7, 
					tooltip=nome_sentiero
				).add_to(mappa)

	# Controlli e salvataggio
	folium.LayerControl().add_to(mappa)
	mappa.save("mappa_debug.html")

	# Mostrare la mappa con Streamlit
	st.title("Mappa dei Sentieri")

	# Mostrare la mappa senza bordi bianchi
	st_folium(mappa, width=1000, height=550)
