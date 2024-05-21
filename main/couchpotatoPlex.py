import json
import plexapi
from plexapi.myplex import MyPlexAccount
from flask import Flask, jsonify, request, redirect, session, url_for, render_template
import requests
import os
import webbrowser
import base64
from cryptography.fernet import Fernet

app = Flask(__name__)

# Variables plex
server_name = 'Javflix'
plex_user_name = 'thejav53'

# Verificar si el archivo credentials.json ya existe
if os.path.exists("json/credentials.json"):
    with open("json/credentials.json", "r") as file:
        credentials = json.load(file)
else:
    # Pedir al usuario los campos por primera vez
    CLIENT_ID = input("Introduce el CLIENT_ID: ")
    CLIENT_SECRET = input("Introduce el CLIENT_SECRET: ")
    REDIRECT_URI = input("Introduce el REDIRECT_URI: ")

    # Guardar las credenciales en el archivo credentials.json
    credentials = {
        "CLIENT_ID": CLIENT_ID,
        "CLIENT_SECRET": CLIENT_SECRET,
        "REDIRECT_URI": REDIRECT_URI
    }
    with open("json/credentials.json", "w") as file:
        json.dump(credentials, file)

# Cargar los valores de las credenciales en variables
CLIENT_ID = credentials['CLIENT_ID']
CLIENT_SECRET = credentials['CLIENT_SECRET']
REDIRECT_URI = credentials['REDIRECT_URI']

TOKEN_FILE = 'tokens/access_token.dat'

# Directorios para almacenar archivos
JSON_DIR = 'json'
KEY_DIR = 'bin'

# Archivos para almacenar el token de acceso y la clave de encriptación
PLEX_DIR= os.path.join(JSON_DIR, 'plexUser.json')
KEY_FILE = os.path.join(KEY_DIR, 'secret.key')

# Crear directorios si no existen
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(KEY_DIR, exist_ok=True)

# Funciones para encriptar y desencriptar

def generate_key():
    """Genera una clave y la guarda en un archivo."""
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    """Carga la clave de encriptación desde el archivo."""
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

def encrypt_message(message):
    """Encripta un mensaje con la clave de encriptación."""
    key = load_key()
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message.encode())
    return base64.urlsafe_b64encode(encrypted_message).decode()

def decrypt_message(encrypted_message):
    """Desencripta un mensaje con la clave de encriptación."""
    key = load_key()
    fernet = Fernet(key)
    encrypted_message = base64.urlsafe_b64decode(encrypted_message.encode())
    return fernet.decrypt(encrypted_message).decode()

# Verificar si el archivo plexUser.json existe
if not os.path.exists(PLEX_DIR):
    # Si no existe, solicitar al usuario que ingrese las credenciales
    print("El archivo no existe. Por favor, ingrese las credenciales requeridas:")
    email = input("Email: ")
    password = input("Password: ")

    # Crear el diccionario de credenciales
    credentials = {
        "email": encrypt_message(email),
        "password": encrypt_message(password)
    }

    # Escribir las credenciales en el archivo
    with open(PLEX_DIR, 'w') as f:
        json.dump(credentials, f, indent=4)
    print("Las credenciales se han guardado encriptadas.")
else:
    # Si el archivo ya existe, leer las credenciales encriptadas desde el archivo JSON
    with open(PLEX_DIR) as f:
        encrypted_credentials = json.load(f)

    # Desencriptar las credenciales
    credentials = {k: decrypt_message(v) for k, v in encrypted_credentials.items()}

    # Asignar las credenciales a variables
    email = credentials['email']
    password = credentials['password']

# Plex part
account = MyPlexAccount(email, password)

# Conectar con el servidor Plex
plex = account.resource(server_name).connect()

if account.username == plex_user_name:
    # Obtener las sesiones activas
    sessions = plex.sessions()

    # Verificar si hay sesiones activas
    if sessions:
        # Iterar sobre cada sesión de medios activa
        for session in sessions:
            # Obtener los detalles de la sesión
            serie_name = session.grandparentTitle
            episode_number = session.index
            season_title = session.parentTitle
            season_number = session.parentIndex
           
            # Imprimir los detalles de la sesión
            print(f'Titulo de la serie: {serie_name}')
            print(f'Numero de capitulo: {episode_number}')
            print(f'Titulo de la temporada: {season_title}')
            print(f'Numero de temporada: {season_number}')
            
    else:
        print('No hay sesiones de medios activas en este momento.')
else:
    print(f'El usuario no es {plex_user_name}. No se pueden obtener las sesiones activas.')

#Anilist part

def save_access_token(token):
    with open(TOKEN_FILE, 'w') as file:
        file.write(token)

def load_access_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            return file.read().strip()
    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    authorization_url = f'https://anilist.co/api/v2/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code'
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400

    token_url = 'https://anilist.co/api/v2/oauth/token'
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': code
    }
    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    if token_response.status_code == 200:
        access_token = token_response.json().get('access_token')
        save_access_token(access_token)
        return redirect(url_for('home'))
    else:
        return jsonify({'error': 'Failed to obtain access token', 'status_code': token_response.status_code, 'response': token_response.text}), token_response.status_code

@app.route('/user')
def get_user_info():
    access_token = load_access_token()
    if not access_token:
        return jsonify({'error': 'User not logged in'}), 401

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    query = '''
    query {
        Viewer {
            id
        }
    }
    '''
    response = requests.post('https://graphql.anilist.co', json={'query': query}, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch user info', 'status_code': response.status_code, 'response': response.text}), response.status_code

@app.route('/anime')
def get_anime_info():
    access_token = load_access_token()
    
    if not access_token:
            return jsonify({'error': 'User not logged in'}), 401

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    if checkSessionStatus() == True:
        anime_name = session.grandparentTitle
        season = session.parentIndex
        if season not in [0, 1]:
            str(season)
            anime_full = f"{anime_name} {season}"
        else:
            anime_full = anime_name

        if not anime_full:
            return jsonify({'error': 'Anime name is required'}), 400

        if not access_token:
            return jsonify({'error': 'User not logged in'}), 401

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        query = '''
        query ($search: String) {
            Media(search: $search, type: ANIME) {
                id
                title {
                    romaji
                    english
                }
                synonyms
            }
        }
        '''

        variables = {'search': anime_full}
        response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch user info', 'status_code': response.status_code, 'response': response.text}), response.status_code

@app.route('/animeUpdate')
def set_anime_update():
    access_token = load_access_token()

    if not access_token:
            return jsonify({'error': 'User not logged in'}), 401

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
        
    if checkSessionStatus() == True:
        viewOffset = session.viewOffset 
        duration = session.duration                 
        media_id = 235
        status = "CURRTENT"

        if percentajeComplete(viewOffset, duration):
            print("El episodio está muy cerca de ser completado")
        else:
            print("El episodio no está cerca de ser completado")

        mutation = '''
        mutation ($id: Int, $status: MediaListStatus) {
            SaveMediaListEntry (mediaId: $id, status: $status, progress: $progress) {
                status
            }
        }
        ''' 
        variables = {'id': media_id, 'status': status}
        response = requests.post('https://graphql.anilist.co', json={'query': mutation, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch user info', 'status_code': response.status_code, 'response': response.text}), response.status_code

@app.route('/animeComplete')
def set_anime_complete():
    access_token = load_access_token()

    if not access_token:
            return jsonify({'error': 'User not logged in'}), 401

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    media_id = 235
    status = "COMPLETED"

    mutation = '''
    mutation ($id: Int, $status: MediaListStatus) {
        SaveMediaListEntry (mediaId: $id, status: $status) {
            status
        }
    }
    '''
    variables = {'id': media_id, 'status': status}
    response = requests.post('https://graphql.anilist.co', json={'query': mutation, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch user info', 'status_code': response.status_code, 'response': response.text}), response.status_code

# Other operations and comprobations

def get_anime_id():
    access_token = load_access_token()
    
    if not access_token:
            return jsonify({'error': 'User not logged in'}), 401

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    if checkSessionStatus() == True:
        anime_name = session.grandparentTitle
        season = session.parentIndex
        if season not in [0, 1]:
            str(season)
            anime_full = f"{anime_name} {season}"
        else:
            anime_full = anime_name

        if not anime_full:
            return jsonify({'error': 'Anime name is required'}), 400

        if not access_token:
            return jsonify({'error': 'User not logged in'}), 401

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        query = '''
        query ($search: String) {
            Media(search: $search, type: ANIME) {
                id
            }
        }
        '''

        variables = {"search": anime_full}
        response = requests.post("https://graphql.anilist.co", json={'query': query, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'Media' in data['data']:
            anime_id = data['data']['Media']['id']
            return jsonify({'anime_id': anime_id}), 200
        else:
            return jsonify({'error': 'Anime not found'}), 404
    else:
        return jsonify({'error': f'Query failed to run with a {response.status_code} status code.', 'response': response.text}), response.status_code


def percentajeComplete(viewOffset, duration, umbral=0.85):
    """
    Calculate the percentage of the episode that has been watched
    Verify if viewOffset is within a threshold of the duration.
    :return: True if viewOffset is within the threshold of the duration, False otherwise.
"""

    if duration == 0:
        return False 
    return (viewOffset / duration) >= umbral

def checkSessionStatus():
    status = False
    if account.username == plex_user_name:
        sessions = plex.sessions()
        # Check Session
        if sessions:
            status = True
    return status 
   
def open_browser():
    webbrowser.open('http://localhost:5000')
    
if __name__ == '__main__':
    open_browser()
    app.run(debug=True)