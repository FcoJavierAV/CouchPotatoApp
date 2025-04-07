import os

TOKEN_DIR = 'tokens'
TOKEN_FILE = os.path.join(TOKEN_DIR, 'access_token_TVDB.dat')

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

def getAccessToken():
    token = loadAccessToken()
    if token is None:
        token = input("Ingrese su token de acceso: ").strip()
        save_access_token(token)
        print("Token guardado correctamente.")
    return token
