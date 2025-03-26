import streamlit as st

# Inserisci la tua API Key qui
GOOGLE_MAPS_API_KEY = "AIzaSyDDVLkAq-Sy3ZCmHaFcKZJSAxYIVn9UMe4"


# Coordinate iniziali della mappa
latitude = 45.85
longitude = 9.40

# Dizionario delle località con sentieri
localita = [
    {
        "nome": "Sasso di PREGUDA",
        "lat": 45.86401,
        "lng": 9.35976,
        "sentieri": [
            {"nome": "Sentiero 1", "difficolta": "Facile", "note": "Adatto ai bambini", "coordinata": [[45.8476, 9.35806], [45.85496, 9.35723], [45.85505, 9.35754],[45.85616, 9.35683],[45.86401, 9.35976]]},
            {"nome": "Sentiero 2", "difficolta": "Medio", "note": "Dislivello moderato", "coordinata": [[45.867, 9.341], [45.869, 9.350]]}
        ]
    },
    {
        "nome": "Lecco RESEGONE",
        "lat": 45.86460,
        "lng": 9.45,
        "sentieri": [
            {"nome": "Sentiero 3", "difficolta": "Facile", "note": "Panorama bellissimo", "coordinata": [[45.86460, 9.45], [45.865, 9.460]]},
            {"nome": "Sentiero 4", "difficolta": "Difficile", "note": "Passaggi esposti", "coordinata": [[45.86460, 9.45], [45.867, 9.480]]}
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

# Mappatura difficoltà
mappa_difficolta = {
    "1 - Facile anche per bambini": "FacileB",
    "2 - Facile per adulti": "Facile",
    "3 - Impegnativo": "Medio",
    "4 - Impervio": "Difficile"
}

# Sidebar per selezionare la difficoltà
st.sidebar.header("Seleziona il livello di difficoltà")
scelta_difficolta = st.sidebar.selectbox("Che tipo di escursione vuoi fare?", list(mappa_difficolta.keys()))

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

        var sentieriLayer = [];
        var locations = {localita};

        locations.forEach(function(loc) {{
          var markerColor = "http://maps.google.com/mapfiles/ms/icons/red-dot.png";
          var hasFilteredPath = false;
          var popupContent = "<b>" + loc.nome + "</b><br>";

          loc.sentieri.forEach(function(sentiero) {{
            var sentieroColor = (sentiero.difficolta === "{difficolta_filtrata}") ? "blue" : "red";
            if (sentiero.difficolta === "{difficolta_filtrata}") {{
              hasFilteredPath = true;
            }}
            popupContent += sentiero.nome + " (" + sentiero.difficolta + ")<br>";

            var sentieroPath = sentiero.coordinata.map(coord => {{
              return {{ lat: coord[0], lng: coord[1] }};
            }});

            var sentieroLine = new google.maps.Polyline({{
              path: sentieroPath,
              geodesic: true,
              strokeColor: sentieroColor,
              strokeOpacity: 1.0,
              strokeWeight: 3
            }});
            sentieriLayer.push(sentieroLine);
            sentieroLine.setMap(map);
          }});

          if (hasFilteredPath) {{
            markerColor = "http://maps.google.com/mapfiles/ms/icons/blue-dot.png";
          }}

          var marker = new google.maps.Marker({{
            position: {{lat: loc.lat, lng: loc.lng }},
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

        var toggleSentieri = document.createElement("button");
        toggleSentieri.textContent = "Mostra/Nascondi Sentieri";
        toggleSentieri.style.position = "absolute";
        toggleSentieri.style.top = "10px";
        toggleSentieri.style.left = "10px";
        toggleSentieri.style.padding = "8px";
        toggleSentieri.style.backgroundColor = "#fff";
        toggleSentieri.style.border = "1px solid #ccc";
        toggleSentieri.style.cursor = "pointer";
        toggleSentieri.style.zIndex = "5";

        map.controls[google.maps.ControlPosition.TOP_LEFT].push(toggleSentieri);

        var sentieriVisibili = true;
        toggleSentieri.addEventListener("click", function() {{
          sentieriVisibili = !sentieriVisibili;
          sentieriLayer.forEach(function(line) {{
            line.setMap(sentieriVisibili ? map : null);
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
