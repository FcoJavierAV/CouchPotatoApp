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
    self.token = loadAccessToken()
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

def loadAccessToken():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            return file.read().strip()
    else:
        os.makedirs(TOKEN_DIR, exist_ok=True)
        return None

def getAnimeInfo(anime_full):    
    query = '''
    query ($search: String) {
        Media(search: $search, type: ANIME) {
            id
            episodes
            format
            status
            seasonYear
            startDate{
            year
            }
            endDate{
            year
            }        
        }
    }
    '''
    variables = {"search": anime_full}
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'Media' in data['data']:
            return data['data']['Media']  
        else:
            print('Anime info not found')
            return None
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return None

def getAnimeInfoDetail(animeFull, year):
    query = '''
    query ($search: String, $year: Int) {
        Media(search: $search, type: ANIME, seasonYear: $year) {
            id
            episodes
            format
            status 
            startDate{
            year
            }
            endDate{
            year
            }
        }
    }
    '''
    variables = {"search": animeFull, "year": year}
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'Media' in data['data']:
            return data['data']['Media']    
        else:
            print('Anime info not found')
            return None
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return None


def getUserId():
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

def getAnimeUser(userId, animeId):
    query = '''
    query ($userId: Int, $animeId: Int) {
        MediaList(userId: $userId, type: ANIME, mediaId: $animeId) {
            id
            progress
            status
        }
    }
    '''

    variables = {'userId': userId, 'animeId': animeId}

    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            # Handle errors in the response
            error_message = ', '.join([error['message'] for error in data['errors']])
            raise Exception(f"Query failed with errors: {error_message}")
        elif 'data' in data and 'MediaList' in data['data'] and data['data']['MediaList'] is not None:
            return data['data']['MediaList']
        else:
            return None
    elif response.status_code == 404:
        return None
    else:
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")


def setAnimeUserStatus(id, status, progress):
    mutation = '''
    mutation ($id: Int, $status: MediaListStatus, $progress: Int){
        SaveMediaListEntry (id: $id, status: $status, progress: $progress) {
            status
            progress
        }
    }
    '''

    variables = {'id': id, 'status': status, 'progress': progress}

    response = requests.post(url, json={'query': mutation, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        return True
    else:
        raise Exception(f"Failed with status code {response.status_code}: {response.text}")

def updateAnimeAndAddCurrent(animeId):
    mutation = '''
    mutation ($animeId: Int) {
        SaveMediaListEntry(mediaId: $animeId, status: CURRENT) {
            id
            status
        }
    }
    '''
    variables = {'animeId': animeId}

    response = requests.post(url, json={'query': mutation, 'variables': variables}, headers=headers)

    if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                error_message = ', '.join([error['message'] for error in data['errors']])
                raise Exception(f"Mutation failed with errors: {error_message}")
            elif 'data' in data and 'SaveMediaListEntry' in data['data']:
                return data['data']['SaveMediaListEntry']
            else:
                return None
    else:
        raise Exception(f"Mutation failed with status code {response.status_code}: {response.text}")
