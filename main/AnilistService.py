import os
import json
import requests

# CONSTANTS
JSON_DIR = 'json'
ANILIST_DIR= os.path.join(JSON_DIR, 'credentials.json')
TOKEN_DIR = 'tokens'
TOKEN_FILE = os.path.join(TOKEN_DIR,'access_token.dat')



def getCredentials():
    # Verificar si el archivo credentials.json existe
    if not os.path.exists(ANILIST_DIR):
        return _askUserCredentials()
    else:
        return  _readUserCredentials()
    
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
    return None


def notifyChange():
    print('hola')

def setStatusAnime():

    mutation = '''
    mutation ($id: Int, $status: MediaListStatus) {
        SaveMediaListEntry (mediaId: $id, status: $status) {
            status
        }
    }
    '''

def get_anime_id(anime_full):
     
    headers = {
        'Authorization': f'Bearer {load_access_token()}',
        'Content-Type': 'application/json'
    }
     
    if not load_access_token():
        return print('No existe el token')

    query = '''
        query ($search: String) {
            Media(search: $search, type: ANIME) {
                id
            }
        }
        '''
    variables = {"search": anime_full}
    response = requests.post("https://graphql.anilist.co", json={'query': query, 'variables': variables}, headers=headers)

    return response

def get_user_id():

    if not load_access_token():
        return print('No existe el token')

    headers = {
        'Authorization': f'Bearer {load_access_token()}',
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

    return response    
