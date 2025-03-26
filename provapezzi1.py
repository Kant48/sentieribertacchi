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
print(df.columns)

# Sostituire le virgole con i punti nelle colonne Latitudine e Longitudine

# Converti latitudine e longitudine località, gestendo sia numeri che stringhe con virgola
df['Latitudine Località'] = df['Latitudine Località'].astype(str).str.replace(',', '.').astype(float)
df['Longitudine Località'] = df['Longitudine Località'].astype(str).str.replace(',', '.').astype(float)
df['Latitudine Passaggio'] = df['Latitudine Passaggio'].astype(str).str.replace(',', '.').astype(float)
df['Longitudine Passaggio'] = df['Longitudine Passaggio'].astype(str).str.replace(',', '.').astype(float)

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
print(localita)
