import plexapi
from plexapi.myplex import MyPlexAccount
import os
import json
import base64
from cryptography.fernet import Fernet

# CONSTANTS
SERVER_NAME = 'Javflix'
PLEX_USER_NAME = 'thejav53'
JSON_DIR = 'json'
KEY_DIR = 'bin'

PLEX_DIR= os.path.join(JSON_DIR, 'plexUser.json')
KEY_FILE = os.path.join(KEY_DIR, 'secret.key')

# VARIABLES
account = None
plex = None

class PlexSession:
    def __init__(self, video_key,serie_name, episode_number, season_title, season_number, duration, season_episode, viewOffset):
        self.video_key = video_key
        self.serie_name = serie_name
        self.episode_number = episode_number
        self.season_title = season_title
        self.season_number = season_number
        self.duration = duration
        self.season_episode = season_episode #s{int}e{int}
        self.viewOffset = viewOffset

    def toString(self):   
        # Imprimir los detalles de la sesión
        return f'Titulo de la serie: {self.serie_name} Numero de capitulo: {self.episode_number} Titulo de la temporada: {self.season_title} Numero de temporada: {self.season_number}'

def getCredentials():
    # Crear directorios si no existen
    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(KEY_DIR, exist_ok=True)

    # Verificar si el archivo plexUser.json existe
    if not os.path.exists(PLEX_DIR):
        return _askUserCredentials()
    else:
        return _readUserCredentials()
    

def connectPlex(self, credentials):
    self.account = MyPlexAccount(credentials['email'], credentials['password'])
    self.plex = account.resource(SERVER_NAME).connect()


#2. Obtener sessions (funciones propias)
def getCompletedSessions():
    if _checkUserHasActiveSessions():
        # Obtener las sesiones activas
        sessions = plex.sessions()

        # Verificar si hay sesiones activas
        if sessions:
            sessions_list = []
            # Iterar sobre cada sesión de medios activa
            for session in sessions:
                # Obtener los detalles de la sesión
                plex_session = PlexSession(session.video_key, session.grandparentTitle, session.index, session.parentTitle, session.parentIndex, session.duration, session.season_episode, session.viewOffset)
                sessions_list.append(plex_session)
                print(plex_session.toString)
                if _percentajeComplete(plex_session.viewOffset, plex_session.duration):
                    pass
                '''TODO: Obtener a partir del video_key el objeto Video que sera tipo Episode. Con el obtener el Show y el Season, que tiene los generos. A partir de ahi, filtrar por anime '''
        else:
            print(' * No hay sesiones de medios activas en este momento.')
    else:
        print(f'El usuario no es {PLEX_USER_NAME}. No se pueden obtener las sesiones activas.')

def _checkUserHasActiveSessions():
    if account.username == PLEX_USER_NAME:
        sessions = plex.sessions()
        # Check Session
        return sessions != None 
    return False

     
# Si no existe, solicitar al usuario que ingrese las credenciales
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
    # Si el archivo ya existe, leer las credenciales encriptadas desde el archivo JSON
    with open(PLEX_DIR) as f:
        encrypted_credentials = json.load(f)

    # Desencriptar las credenciales
    credentials = {k: _decrypt_message(v) for k, v in encrypted_credentials.items()}
    
    return {'email':credentials['email'], 'password': credentials['password']}

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

def _percentajeComplete(viewOffset, duration, umbral=0.85):
    """
    Calculate the percentage of the episode that has been watched
    Verify if viewOffset is within a threshold of the duration.
    :return: True if viewOffset is within the threshold of the duration, False otherwise.
"""
    if duration == 0:
        return False 
    return (viewOffset / duration) >= umbral

