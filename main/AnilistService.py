import os
import json

# CONSTANTS
JSON_DIR = 'json'
ANILIST_DIR= os.path.join(JSON_DIR, 'credentials.json')



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

        return {'CLIENT_ID':credentials['CLIENT_ID'], 'CLIENT_SECRET': credentials['CLIENT_SECRET'], 'REDIRECT_URI': credentials['REDIRECT_URI']}
