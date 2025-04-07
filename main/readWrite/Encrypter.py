import os
import json
import base64
from cryptography.fernet import Fernet

JSON_DIR = 'json'
KEY_DIR = 'bin'

PLEX_DIR= os.path.join(JSON_DIR, 'plexUser.json')
KEY_FILE = os.path.join(KEY_DIR, 'secret.key')


def _askUserCredentials():
    print("El archivo no existe. Por favor, ingrese el token requerido:")
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
