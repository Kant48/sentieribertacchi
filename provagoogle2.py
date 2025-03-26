import streamlit as st

# Inserisci la tua API Key qui
GOOGLE_MAPS_API_KEY = "AIzaSyDDVLkAq-Sy3ZCmHaFcKZJSAxYIVn9UMe4"

# Coordinate iniziali della mappa
latitude = 45.85
longitude = 9.40

# Dizionario delle località con difficoltà
localita = [
    {"nome": "Sasso di PREGUDA", "lat": 45.86401, "lng": 9.35976, "difficolta": "Facile"},
    {"nome": "Lecco RESEGONE", "lat": 45.86460, "lng": 9.45, "difficolta": "Medio"},
    {"nome": "Valmadrera San Tommaso", "lat": 45.849, "lng": 9.343, "difficolta": "FacileB"}
]

# Mappatura difficoltà visibile all'utente
mappa_difficolta = {
    "1 - Facile anche per bambini": "FacileB",
    "2 - Facile per adulti": "Facile",
    "3 - Impegnativo": "Medio",
    "4 - Impervio": "Difficile"
}

# Sidebar per selezionare la difficoltà
st.sidebar.header("Seleziona il livello di difficoltà")
scelta_difficolta = st.sidebar.selectbox(
    "Che tipo di escursione vuoi fare?",
    list(mappa_difficolta.keys())
)

# Traduzione della scelta utente nella difficoltà
difficolta_filtrata = mappa_difficolta[scelta_difficolta]

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

        var locations = {localita};  // Lista delle località

        locations.forEach(function(loc) {{
          var markerColor = loc.difficolta === "{difficolta_filtrata}" ? "http://maps.google.com/mapfiles/ms/icons/blue-dot.png" 
                                                                       : "http://maps.google.com/mapfiles/ms/icons/red-dot.png";

          var marker = new google.maps.Marker({{
            position: {{lat: loc.lat, lng: loc.lng }},
            map: map,
            title: loc.nome,
            icon: markerColor
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
st.components.v1.html(map_html, height=500)
