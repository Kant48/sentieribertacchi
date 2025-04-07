import folium
import streamlit as st
import pandas as pd
import csv
import os
import sys  # Necessario per terminare l'app
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from io import BytesIO
from docx import Document
from docx.shared import RGBColor
from datetime import datetime
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
		.css-1l7jqpk {display: none;}  /* Nasconde il banner di avviso */
		.css-1to5xxz {display: none;}  /* Nasconde eventuali altri banner */
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
# Funzione per salvare il feedback nel CSV
def salva_feedback(feedback):
	# Mappiamo le faccine in etichette
	feedback_mappato = {
		"😊": "Ottimo",
		"😐": "Buono",
		"😞": "Scarso"
	}
	
	# Otteniamo l'etichetta corrispondente al feedback
	feedback_etichetta = feedback_mappato.get(feedback, "Sconosciuto")
	
	# Ottieni la data e l'ora correnti
	ora_corrente = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	# Verifica il percorso di lavoro corrente
	percorso = os.getcwd()
	st.write(f"Percorso di lavoro corrente: {percorso}")

	# Scrivi il feedback e la data/ora nel file CSV
	with open("feedback.csv", mode="a", newline="", encoding="utf-8") as file:
		writer = csv.writer(file)
		writer.writerow([feedback_etichetta, ora_corrente])
	st.success("Feedback salvato!")
# Funzione per caricare le note generali con allineamento a sinistra

def carica_note_generali():
	doc_path = "NOTEGENERALI.docx"
	doc = Document(doc_path)
	testo_completo = ""

	# Itera su tutti i paragrafi del documento
	for para in doc.paragraphs:
		testo_paragrafo = para.text.strip()
		# Esclude la riga se corrisponde a "Note Generali"
		if testo_paragrafo and testo_paragrafo != "Note Generali":
			if para.runs:
				paragrafo = ""
				for run in para.runs:
					# Estrai il testo e la formattazione (come il colore)
					text = run.text.replace("\n", "  \n")  # A capo in Markdown
					# Se il testo è in grassetto, aggiungi tag <b>
					if run.bold:
						text = f"<b>{text}</b>"
					# Estrai il colore del testo (se presente)
					color = run.font.color
					if color and isinstance(color.rgb, RGBColor):
						color_hex = f"#{color.rgb[0]:02x}{color.rgb[1]:02x}{color.rgb[2]:02x}"
						text = f'<span style="color: {color_hex};">{text}</span>'
#					elif color is not None:
#						print(f"Colore non gestito per il run: {color}")  # Debug per vedere il tipo di colore
					
					# Aggiungi il testo con la formattazione
					paragrafo += text
				# Aggiungi il paragrafo al testo completo, mantenendo il formato
				testo_completo += f'<p style="text-align: left;">{paragrafo}</p>\n'
	return testo_completo  # Ritorna il testo del documento

# Carico le note generali
note_generali = carica_note_generali()


# Mostro le note generali in Streamlit con HTML
#st.markdown(note_generali, unsafe_allow_html=True)


# Mostro le note generali in Streamlit
#st.markdown(note_generali)





# Centro mappa
latzona = 45.85
longzona = 9.40

# Caricamento del file Excel
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

# Riordinare i passaggi per sequenza
for nome_localita in localita:
	for nome_sentiero in localita[nome_localita]["sentieri"]:
		localita[nome_localita]["sentieri"][nome_sentiero]["percorso"].sort(key=lambda x: x["sequenza"])

# Aggiungi il filtro per difficoltà
difficolta_opzioni = sorted(set([sentiero["difficolta"] for localita_data in localita.values() for sentiero in localita_data["sentieri"].values()]))
difficolta_opzioni.insert(0, "Tutti")  # Opzione per vedere tutti i sentieri

# Sezione delle Note Generali sopra le colonne
#st.title("Sentieri e Note Generali")
#st.markdown(
#    "<h2 style='font-size: 24px; font-family: Arial; color: #4CAF50;'>Divertiti in montagna</h2>", 
#    unsafe_allow_html=True
#)

# Inizializza lo stato per le note generali
if "mostra_note" not in st.session_state:
	st.session_state["mostra_note"] = False

# Disposizione a colonne (colonna 1 per il filtro difficoltà, colonna 2 per la mappa)
col1, col2 = st.columns([2, 10])  # 2 per il filtro difficoltà, 10 per la mappa (maggiore spazio per la mappa)

# Filtro difficoltà nella colonna di sinistra
with col1:
	st.header("Seleziona la difficoltà del sentiero:")
	scelta_difficolta = st.selectbox("Scegli la difficoltà", difficolta_opzioni)

	# Pulsante per mostrare le note generali
	if st.button("NOTE sulle ESCURSIONI"):
		st.session_state["mostra_note"] = True
	if st.session_state["mostra_note"]:
		if st.button("Chiudi NOTE", key="chiudi_note"):
			st.session_state["mostra_note"] = False
		# Aggiungi il feedback delle faccine sotto il tasto "Chiudi note generali"
	st.write("Ti piace questa app?")
	feedback = st.radio("Seleziona una faccina:", ("😊", "😐", "😞"), key="feedback", index=None)


		# Salva il feedback nel file CSV
	if feedback:
			salva_feedback(feedback)
			# Mostra il feedback selezionato
			st.write(f"Hai scelto: {feedback}")
			st.success("Grazie per il tuo feedback!")   
with col2:

	# Aggiungi marker solo per i sentieri che corrispondono alla difficoltà selezionata
	for nome_localita, dati_localita in localita.items():
		lat_localita = dati_localita.get("lat", 0)
		lng_localita = dati_localita.get("lng", 0)
		descrizione_localita = dati_localita.get('descrizione', 'Nessuna descrizione')
		note_localita = dati_localita.get('Note', 'Nessuna nota')		
		immlocurl = dati_localita.get('immagine','')
		imm_localita = f'<a href="{immlocurl}" target="_blank"><img src="{immlocurl}" style="max-width: 200px; max-height: 150px; display: block; margin: 0 auto;"></a>' if immlocurl else '<i>Immagine non presente</i>'
		popup_localita = f"<b>{nome_localita}</b><br>{descrizione_localita}</b><br>{note_localita}</b><br>{imm_localita}"

		folium.Marker(
			location=[lat_localita, lng_localita],
			popup=folium.Popup(popup_localita, max_width=650),
			icon=folium.Icon(color="blue", icon="info-sign")
		).add_to(mappa)

		for nome_sentiero, dati_sentiero in dati_localita["sentieri"].items():
			if scelta_difficolta == "Tutti" or dati_sentiero["difficolta"] == scelta_difficolta:
				punti_sentiero = []
				for passaggio in dati_sentiero["percorso"]:
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
							html=f"<div style='font-family: Arial; font-size: 12px; font-weight: bold; color: black;'>{passaggio['sequenza']}</div>"
						),
						popup=folium.Popup(popup_html, max_width=650)
					).add_to(mappa)
	  

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
	st_folium(mappa, width=1000, height=500)

# Aggiunta di stile CSS per posizionare le note generali sopra la mappa
# Aggiunta di stile CSS per posizionare le note generali sopra la mappa
st.markdown(
	"""
	<style>
		.note-overlay {
			position: fixed;
			top: 20%;
			left: 50%;
			transform: translateX(-50%);
			background: rgba(255, 255, 255, 0.9);
			padding: 30px;
			border-radius: 12px;
			box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.2);
			z-index: 10;
			max-width: 600px;
			text-align: center;
			/* Altezza regolabile */
			max-height: 450px; /* Altezza massima */
			min-height: 100px; /* Altezza minima */
			overflow-y: auto; /* Aggiunge scroll se supera l'altezza massima */
		}
		.button-container {
			text-align: right;
			margin-top: 30px;
		}
	</style>
	""",
	unsafe_allow_html=True
)


# Inizializza lo stato delle note se non esiste già
if "mostra_note" not in st.session_state:
	st.session_state["mostra_note"] = False  # Le note sono nascoste di default

# Layout a colonne
#col1, _ = st.columns([1, 1])  # Solo prima colonna per visualizzare il pulsante

# Pulsante per visualizzare le note generali (appare solo quando le note sono nascoste)
#with col1:
#	if not st.session_state["mostra_note"]:
#		if st.button("Visualizza Note Generali", key="visualizza_note"):
#			st.session_state["mostra_note"] = True  # Mostra le note

if st.session_state["mostra_note"]:
	# Crea una sezione note con Streamlit (non solo HTML)
	with st.container():
		st.markdown(f"""
		<div class='note-overlay'>
			<p>{note_generali}</p>
			<div class="button-container">
			""", unsafe_allow_html=True)

	# Pulsante posizionato in basso a destra del popup
		#if st.button("Chiudi Note Generali", key="chiudi_note"):
		#	st.session_state["mostra_note"] = False  # Nascondi le note

		# Chiusura del div HTML
		st.markdown("</div></div>", unsafe_allow_html=True)

# Mostra lo stato delle note per il debug
st.write(f"Mostra Note: {st.session_state.get('mostra_note', 'Non impostato')}")













	# Pulsante "Chiudi Note Generali" FUORI dal div HTML
	#if st.button("Chiudi Note Generali"):
		#st.session_state["mostra_note"] = False
		
