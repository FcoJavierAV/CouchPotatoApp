import json
from flask import Flask, jsonify, redirect, request, session, url_for, render_template
import requests
import os
import webbrowser
import PlexService
import AnilistService

app = Flask(__name__)

plex_credentials = PlexService.getCredentials()
PlexService.connectServer(PlexService, plex_credentials)
PlexService.getCompletedSessions()
anilist_credentials = AnilistService.getCredentialsAnilist()




TOKEN_FILE = 'tokens/access_token.dat'

# anilist finish


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
    authorization_url = f'https://anilist.co/api/v2/oauth/authorize?client_id={anilist_credentials.CLIENT_ID}&redirect_uri={anilist_credentials.REDIRECT_URI}&response_type=code'
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400

    token_url = 'https://anilist.co/api/v2/oauth/token'
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': anilist_credentials.CLIENT_ID,
        'client_secret': anilist_credentials.CLIENT_SECRET,
        'redirect_uri': anilist_credentials.REDIRECT_URI,
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

    if PlexService._checkUserHasActiveSessions() == True:
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
        
    if PlexService._checkUserHasActiveSessions() == True:
        viewOffset = session.viewOffset 
        duration = session.duration                 
        media_id = 235
        status = "CURRENT"

        if PlexService._percentajeComplete(viewOffset, duration):
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

    if PlexService._checkUserHasActiveSessions() == True: #Funcion publica de plex que llama anilist
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

# End point
   
def open_browser():
    webbrowser.open('http://localhost:5000')
    
if __name__ == '__main__':
    open_browser()
    app.run(debug=True)