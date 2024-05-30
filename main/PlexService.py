import plexapi
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import os
import json
import base64
from cryptography.fernet import Fernet

# CONSTANTS
SERVER_NAME = 'Javflix'
PLEX_USER_NAME = 'thejav53'
JSON_DIR = 'json'
KEY_DIR = 'bin'
PLEX_URL = 'http://127.0.0.1:32400'
PLEX_TOKEN = 'Mt6r87gvwmMgjSgApgW7'

PLEX_DIR= os.path.join(JSON_DIR, 'plexUser.json')
KEY_FILE = os.path.join(KEY_DIR, 'secret.key')

# VARIABLES
account = None
account_connection = None
plex_server = None

class PlexSession:
    def __init__(self, rating_key, serie_name, episode_number, season_title, season_number, duration, viewOffset):
        self.rating_key = rating_key
        self.serie_name = serie_name
        self.episode_number = episode_number
        self.season_title = season_title
        self.season_number = season_number
        self.duration = duration
        self.viewOffset = viewOffset

    def toString(self):   
        return f'Titulo de la serie: {self.serie_name} Numero de capitulo: {self.episode_number} Titulo de la temporada: {self.season_title} Numero de temporada: {self.season_number}'

def getCredentials():
    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(KEY_DIR, exist_ok=True)

    if not os.path.exists(PLEX_DIR):
        return _askUserCredentials()
    else:
        return _readUserCredentials()
    

def connectServer(self, credentials):
    self.account = MyPlexAccount(credentials['email'], credentials['password'])
    self.account_connection = account.resource(SERVER_NAME).connect()
    self.plex_server = PlexServer(PLEX_URL, PLEX_TOKEN)

#2. Obtener sessions (funciones propias)
def getCompletedSessions():
    if _checkUserHasActiveSessions():
        # Obtener las sesiones activas
        sessions = account_connection.sessions()
        # Verificar si hay sesiones activas
        if sessions:
            sessions_list = []
            # Iterar sobre cada sesión de medios activa
            for session in sessions:
                # Obtener los detalles de la sesión
                plex_session = PlexSession(session.key, session.grandparentTitle, session.index, session.parentTitle, session.parentIndex, session.duration, session.viewOffset)
                sessions_list.append(plex_session)
                if _percentajeComplete(plex_session.viewOffset, plex_session.duration):
                    show = _getShow(plex_session)                    
                    if _isAnime(show):
                        return show.originalTitle                             
        else:
            print(' * No hay sesiones de medios activas en este momento.')
    else:
        print(f' *  No existe sesión')
    return None

def _checkUserHasActiveSessions():
    if account.username == PLEX_USER_NAME:
        sessions = account_connection.sessions()
        return sessions
    return False

def _getShow(plex_session):
    episode = plex_server.fetchItem(plex_session.rating_key)
    if isinstance(episode, plexapi.video.Episode):
        showKey = episode.grandparentKey
        return plex_server.fetchItem(showKey)
        
def _isAnime(show):
    return len([show.genres for show_genre in show.genres if show_genre.tag == 'Anime']) > 0

def _askUserCredentials():
    print("El archivo no existe. Por favor, ingrese las credenciales requeridas:")
    email = input("Email: ")
    password = input("Password: ")
    credentials = {'email': email, 'password': password}
    _saveEncryptedCredentials(credentials)

    return credentials

def _saveEncryptedCredentials(credentials):
    encrypted_credentials = {
        "email": _encrypt_message(credentials.email),
        "password": _encrypt_message(credentials.password)
    }
    # Escribir las credenciales en el archivo
    with open(PLEX_DIR, 'w') as f:
        json.dump(encrypted_credentials, f, indent=4)
    print("Las credenciales se han guardado encriptadas.")
        
def _readUserCredentials():
    with open(PLEX_DIR) as f:
        encrypted_credentials = json.load(f)
    credentials = {k: _decrypt_message(v) for k, v in encrypted_credentials.items()}
    
    return credentials

def _generate_key():
    """Genera una clave y la guarda en un archivo."""
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def _load_key():
    """Carga la clave de encriptación desde el archivo."""
    if not os.path.exists(KEY_FILE):
        _generate_key()
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

def _encrypt_message(message):
    """Encripta un mensaje con la clave de encriptación."""
    key = _load_key()
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message.encode())
    return base64.urlsafe_b64encode(encrypted_message).decode()

def _decrypt_message(encrypted_message):
    """Desencripta un mensaje con la clave de encriptación."""
    key = _load_key()
    fernet = Fernet(key)
    encrypted_message = base64.urlsafe_b64decode(encrypted_message.encode())
    return fernet.decrypt(encrypted_message).decode()

def _percentajeComplete(viewOffset, duration, umbral=0.87):
    if duration == 0:
        return False 
    return (viewOffset / duration) >= umbral


def getSessionDetails():
    if _checkUserHasActiveSessions():
        sessions = account_connection.sessions()
        if sessions:
            session = sessions[0]
            session_detail = {
                'index': session.index,
                'parentTitle': session.parentTitle,
                'parentIndex': session.parentIndex
            }
            return session_detail
        else:
            print(' * No hay sesiones de medios activas en este momento.')
    else:
        print(' * No existe sesión')
    return None