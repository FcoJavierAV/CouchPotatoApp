import requests
from bs4 import BeautifulSoup

animeName = 'dragon-ball'
website = "https://www.thetvdb.com/series/"

url = website + animeName + '#seasons'

# Realizar la solicitud HTTP para obtener el HTML de la página
response = requests.get(url)
html = response.text

# Crear un objeto BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Encontrar la tabla que contiene la información de las temporadas
tabla_temporadas = soup.find('table', class_='table table-bordered table-hover table-colored')

temp = []

# Iterar sobre las filas de la tabla
for fila in tabla_temporadas.find_all('tr'):
    columnas = fila.find_all('td')
    # Si hay columnas en la fila y el número de columnas es igual a 4
    if columnas and len(columnas) == 4:
        temporada = columnas[0].text.strip()
        if temporada not in ["Specials", "All Seasons", "Unassigned Episodes"]:
            numero_capitulos = columnas[3].text.strip()
            temp.append(numero_capitulos)
