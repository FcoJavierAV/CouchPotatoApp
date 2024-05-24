import os
import json
from flask import jsonify, redirect, url_for
import requests

# CONSTANTS
JSON_DIR = 'json'
ANILIST_DIR= os.path.join(JSON_DIR, 'credentials.json')
TOKEN_DIR = 'tokens'
TOKEN_FILE = os.path.join(TOKEN_DIR,'access_token.dat')

# VARIABLES
url = 'https://graphql.anilist.co'
token = None
headers = None

def setHeader(self):
    self.headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def init(self):
    self.token = load_access_token()
    if token == None:
        return _getCredentials()
    setHeader(self)
    return None

def getToken(self, credentials, code):
    token_url = 'https://anilist.co/api/v2/oauth/token'
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': credentials['CLIENT_ID'],
        'client_secret': credentials['CLIENT_SECRET'],
        'redirect_uri': credentials['REDIRECT_URI'],
        'code': code
    }
    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    if token_response.status_code == 200:
        self.token = token_response.json().get('access_token')
        credentials.save_access_token(self.token)
        setHeader(self.token)
        return redirect(url_for('home'))
    else:
        return jsonify({'error': 'Failed to obtain access token', 'status_code': token_response.status_code, 'response': token_response.text}), token_response.status_code

def _getCredentials():
    if not os.path.exists(ANILIST_DIR):
        return _askUserCredentials()
    else:
        return _readUserCredentials()    
    
def _askUserCredentials():
    print("Las credenciales de anilist no existen. Por favor, ingrese las credenciales requeridas:")
    CLIENT_ID = input("Introduce el CLIENT_ID: ")
    CLIENT_SECRET = input("Introduce el CLIENT_SECRET: ")
    REDIRECT_URI = input("Introduce el REDIRECT_URI: ")    
    credentials = {'CLIENT_ID': CLIENT_ID, 'CLIENT_SECRET': CLIENT_SECRET, 'REDIRECT_URI': REDIRECT_URI}
    _saveUserCredentials(credentials)

    return credentials

def _saveUserCredentials(credentials):
    # Guardar las credenciales en el archivo credentials.json
    credentials = {
        "CLIENT_ID": credentials.CLIENT_ID,
        "CLIENT_SECRET": credentials.CLIENT_SECRET,
        "REDIRECT_URI": credentials.REDIRECT_URI
    }
    with open("json/credentials.json", "w") as file:
        json.dump(credentials, file)

def  _readUserCredentials():
        with open("json/credentials.json", "r") as file:
            credentials = json.load(file)

        return credentials

def save_access_token(token):
    with open(TOKEN_FILE, 'w') as file:
        file.write(token)

def load_access_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            return file.read().strip()
    else:
        os.makedirs(TOKEN_DIR, exist_ok=True)
        return None


def notifyChange():
    print('hola')

def setStatusAnime(media_id, status):
    mutation = '''
    mutation ($id: Int, $status: MediaListStatus) {
        SaveMediaListEntry (mediaId: $id, status: $status) {
            status
        }
    }
    '''

    variables = {'id': media_id, 'status ': status}

    response = requests.post(url, json={'query': mutation, 'variables': variables}, headers=headers)

    return response


def getMediaUserStatus(user_id, anime_id):
    query = '''
    query ($userId: Int, $animeId: Int){
        MediaList(userId: 6756519, mediaId: 99263) {
            status
            progress
        }
        }
    }'''

    
    variables = {
        "userId": user_id,
        "animeId": anime_id
    }
    
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'MediaList' in data['data']:
            mediaList = data['data']['MediaList']
            media_user_status = {
                'status': mediaList.get('status'),
                'progress': mediaList['mediaList'][0].get('progress') if mediaList['mediaList'] else None
            }
            return media_user_status
        else:
            print('No se encontraron datos de anime')
            return None
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return None
    


def getAnimeInfo(anime_full):    
    query = '''
    query ($search: String) {
        Media(search: $search, type: ANIME) {
            id
            episodes
            format
        }
    }
    '''
    variables = {"search": anime_full}
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'Media' in data['data']:
            anime_info = data['data']['Media']
            return {
                'id': anime_info['id'],
                'episodes': anime_info['episodes'],
                'format': anime_info['format']
            }
        else:
            print('Anime info not found')
            return None
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return None


def get_user_id():
    query = '''
    query {
        Viewer {
            id
        }
    }
    '''

    response = requests.post(url, json={'query': query}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'Viewer' in data['data']:
            return data['data']['Viewer']['id']
        else:
            print('No se encontró la ID del usuario')
            return None
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return None   


def get_anime_user_progress(user_id, anime_id):
    query = '''
    query ($userId: Int, $animeId: Int) {
        MediaListCollection(userId: $userId, type: ANIME, status: CURRENT) {
            lists {
                entries(mediaId: $animeId) {
                    progress
                }
            }
        }
    }
    '''

    variables = {'userId': user_id, 'animeId': anime_id}

    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        progress = data['data']['MediaListCollection']['lists'][0]['entries'][0]['progress']
        return progress
    else:
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")


def setAnimeUserProgress(media_id, progress):
    mutation = '''
    mutation ($id: Int, $status: MediaListStatus, $progress: Int) {
        SaveMediaListEntry (mediaId: $id, status: CURRENT, progress: $progress) {
            status
            progress
        }
    }
    '''
    variables = {'id': media_id, 'progress': progress}
    response = requests.post(url, json={'query': mutation, 'variables': variables}, headers=headers)

    return response

