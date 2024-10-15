import requests
import os

TOKEN_DIR = 'tokens'
TOKEN_FILE = os.path.join(TOKEN_DIR,'tvdb_access_token.dat')

def loadAccessToken():
    if os.path.exists(APIKEY):
        with open(APIKEY, 'r') as file:
            return file.read().strip()
    else:
        os.makedirs(TOKEN_DIR, exist_ok=True)
        return None
    
APIKEY = loadAccessToken()

def getTVDBToken(APIKEY):
    url = 'https://api4.thetvdb.com/v4/login'
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'apikey': APIKEY
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()['data']['token']


def findSeriesByName(name, token):
    url = f'https://api4.thetvdb.com/v4/search?query={name}'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    try:
        # Buscar la serie por nombre
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json().get('data', [])
        
        if not result:
            print("No se encontraron resultados de búsqueda.")
            return None
        
        series = result[0]
        id = series['id']
        
        # Verificar y construir la URL de detalles correctamente
        if not id:
            print("No se encontró el ID de la serie.")
            return None
        
        findSeriesUrl = f'https://api4.thetvdb.com/v4/series/{id}'
        print(f"URL de detalles: {findSeriesUrl}")  # Imprimir la URL para depuración
        
        # Obtener más detalles de la serie usando el series_id
        response = requests.get(findSeriesUrl, headers=headers)
        response.raise_for_status()
        seriesDetails = response.json().get('data', {})
        
        return seriesDetails
    
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        return None

# Ejemplo de uso
token = getTVDBToken(APIKEY)
name = 'Breaking Bad'
detalles = findSeriesByName(name, token)
if detalles:
    print(detalles)
else:
    print("No se encontraron detalles para la serie especificada.")
