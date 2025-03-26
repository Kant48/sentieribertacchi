import streamlit as st

# La tua API Key di Google Maps (devi ottenere la tua da Google Cloud)
GOOGLE_MAPS_API_KEY = "AIzaSyDDVLkAq-Sy3ZCmHaFcKZJSAxYIVn9UMe4"

# Dati dei rifugi e sentieri
rifugi = [
    {
        "nome": "Sasso di PREGUDA",
        "lat": 45.86401,
        "lng": 9.35976,
        "sentieri": [
            {"nome": "Sentiero 1", "difficolta": "Facile", "note": "Adatto ai bambini", "coordinata": [[45.8476, 9.35806], [45.85496, 9.35723], [45.85505, 9.35754],[45.85616, 9.35683],[45.86401, 9.35976]]},
            {"nome": "Sentiero 2", "difficolta": "Medio", "note": "Dislivello moderato", "coordinata": [[45.867, 9.341], [45.869, 9.350]]},
            {"nome": "Sentiero 3", "difficolta": "Difficile", "note": "Solo per esperti", "coordinata": [[45.867, 9.341], [45.870, 9.355]]}
        ]
    },
     {
        "nome": "Lecco RESEGONE",
        "lat": 45.86460,
        "lng": 9.44935,
        "sentieri": [
            {"nome": "Sentiero 4", "difficolta": "Facile", "note": "Panorama bellissimo", "coordinata": [[45.86460, 9.45], [45.865, 9.460]]},
            {"nome": "Sentiero 5", "difficolta": "Medio", "note": "Alcuni tratti ripidi", "coordinata": [[45.86460, 9.45], [45.866, 9.470]]},
            {"nome": "Sentiero 6", "difficolta": "Difficile", "note": "Passaggi esposti", "coordinata": [[45.86460, 9.45], [45.867, 9.480]]}
        ]
    },
    {
        "nome": "Valmadrera San Tommaso",
        "lat": 45.84911,
        "lng": 9.34219,
        "sentieri": [
            {"nome": "Sentiero 4", "difficolta": "FacileB", "note": "Panorama bellissimo", "coordinata": [[45.849, 9.343]]},
            {"nome": "Sentiero 5", "difficolta": "Medio", "note": "Alcuni tratti ripidi", "coordinata": [[45.86460, 9.45], [45.866, 9.470]]},
            {"nome": "Sentiero 6", "difficolta": "Difficile", "note": "Passaggi esposti", "coordinata": [[45.86460, 9.45], [45.867, 9.480]]}
        ]
    },	  
]

# La logica per la difficoltà dei sentieri (selezionata via sidebar)
mappa_difficolta = {
    "1 - Facile anche per bambini": "FacileB",
    "2 - Facile per adulti": "Facile",
    "3 - Impegnativo": "Medio",
    "4 - Impervio": "Difficile"
}

st.sidebar.header("Seleziona il livello di difficoltà del sentiero")
scelta_difficolta = st.sidebar.selectbox(
    "Che tipo di escursione vuoi fare?",
    list(mappa_difficolta.keys())  
)

difficolta_filtrata = mappa_difficolta[scelta_difficolta]

# Filtra i rifugi in base alla difficoltà selezionata
rifugi_filtrati = []
for rifugio in rifugi:
    sentieri_filtrati = [s for s in rifugio["sentieri"] if s["difficolta"] == difficolta_filtrata]
    if sentieri_filtrati:
        rifugi_filtrati.append({"nome": rifugio["nome"], "lat": rifugio["lat"], "lng": rifugio["lng"], "sentieri": sentieri_filtrati})

# Creazione del codice HTML per Google Maps
map_html = f"""
<!DOCTYPE html>
<html>
  <head>
    <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&callback=initMap" async defer></script>
    <script>
      function initMap() {{
        var map = new google.maps.Map(document.getElementById('map'), {{
          center: {{lat: 45.86401, lng: 9.35976}},
          zoom: 13,
          mapTypeId: 'terrain'
        }});

        var rifugi = {str(rifugi_filtrati)};
        rifugi.forEach(function(rifugio) {{
          var marker = new google.maps.Marker({{
            position: {{lat: rifugio.lat, lng: rifugio.lng}},
            map: map,
            title: rifugio.nome
          }});

          var infoContent = "<h3>" + rifugio.nome + "</h3><ul>";
          rifugio.sentieri.forEach(function(sentiero) {{
            infoContent += "<li><b>" + sentiero.nome + "</b> (" + sentiero.difficolta + "): " + sentiero.note + "</li>";
          }});
          infoContent += "</ul>";

          var infoWindow = new google.maps.InfoWindow({{
            content: infoContent
          }});

          marker.addListener('click', function() {{
            infoWindow.open(map, marker);
          }});

          // Aggiungi le polilinee per i sentieri
          rifugio.sentieri.forEach(function(sentiero) {{
            var percorso = sentiero.coordinata.map(coord => {{
                return {{ lat: coord[0], lng: coord[1] }};
            }});

            var polyline = new google.maps.Polyline({{
              path: percorso,
              geodesic: true,
              strokeColor: sentiero.difficolta === 'Facile' ? 'blue' : sentiero.difficolta === 'Medio' ? 'orange' : 'red',
              strokeOpacity: 1.0,
              strokeWeight: 3
            }});
            polyline.setMap(map);
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

# Mostra la mappa in Streamlit
st.components.v1.html(map_html, height=500)

# Mostra i sentieri filtrati nella sidebar
if rifugi_filtrati:
    st.subheader(f"Sentieri disponibili con difficoltà: {difficolta_filtrata}")
    for rifugio in rifugi_filtrati:
        st.markdown(f"### {rifugio['nome']}")
        for sentiero in rifugio["sentieri"]:
            st.write(f"- **{sentiero['nome']}** ({sentiero['difficolta']}): {sentiero['note']}")
else:
    st.warning("Nessun sentiero disponibile per la difficoltà selezionata.")
