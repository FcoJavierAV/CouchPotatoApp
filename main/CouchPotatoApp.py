import threading
import time
from flask import Flask, jsonify, redirect, request, url_for, render_template
import psutil
import webbrowser
import PlexService
import AnilistService

app = Flask(__name__)

plex_credentials = PlexService.getCredentials()
PlexService.connectServer(PlexService, plex_credentials)
anilist_credentials = AnilistService.init(AnilistService)


def completeSessionTask():
    while True:
        show_original_title = PlexService.getCompletedSessions()
        if show_original_title != None:
            print("Episodio completado")
            addEpisode()
            show_original_title = None
        else:
            print("No esta terminando")
        time.sleep(5)


mainThread = threading.Thread(target=completeSessionTask)
mainThread.start()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    authorization_url = f"https://anilist.co/api/v2/oauth/authorize?client_id={anilist_credentials['CLIENT_ID']}&redirect_uri={anilist_credentials['REDIRECT_URI']}&response_type=code"
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400
    AnilistService.getToken(AnilistService, anilist_credentials, code)
    
    
def get_anime_info():
    anime_name = PlexService.getCompletedSessions()
    anime_info = AnilistService.getAnimeInfo(anime_name)
    if anime_info:
        print(f"Información del anime {anime_name}:")
        print(f"ID: {anime_info['id']}")
        print(f"Título (inglés): {anime_info['title']['english']}")
        print(f"Título (romaji): {anime_info['title']['romaji']}")
        print(f"Título (nativo): {anime_info['title']['native']}")
        print(f"Episodios: {anime_info['episodes']}")
        print(f"Formato: {anime_info['format']}")
        print(f"Estado: {anime_info['status']}")
    else:
        print(f"No se encontró información para el anime {anime_name}")




    '''if PlexService._checkUserHasActiveSessions() == True:
        session = PlexService.getCompletedSessions()
        anime_name = session['show']
        season = 1                     # Important change ¿De donde saco el numero de season (no funciona el session.index )?
        if season not in [0, 1]:
            str(season)
            anime_full = f"{anime_name} {season}"
        else:
            anime_full = anime_name

        if not anime_full:
            return jsonify({'error': 'Anime name is required'}), 400
    
        response = AnilistService.get_anime_info(anime_full)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch user info', 'status_code': response.status_code, 'response': response.text}), response.status_code
'''

def set_anime_user_progress():
    if PlexService._checkUserHasActiveSessions() == True:
        animeId = getAnimeInfo()
        progress = PlexService.getCompletedSessions()['episode']

        AnilistService.setAnimeUserProgress(animeId, progress)


def setAnimeComplete(media_id):
    status = "COMPLETED"
    response = AnilistService.setStatusAnime(media_id, status)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch user info', 'status_code': response.status_code, 'response': response.text}), response.status_code


def getAnimeInfo():
    if PlexService._checkUserHasActiveSessions() == True: 
        plex_viewed_episode = PlexService.getCompletedSessions()
        season_num = PlexService.getSessionDetails()
        season = season_num['parentIndex']
        anime_name = plex_viewed_episode
        if season not in [0, 1]:
            str(season)
            anime_full = f"{anime_name} {season}"
        else:
            anime_full = anime_name

        if not anime_full:
            return jsonify({'error': 'Anime name is required'}), 400

        return AnilistService.getAnimeInfo(anime_full)

    return None

def addEpisode():
    show_original_title = PlexService.getCompletedSessions()
    episode_num = PlexService.getSessionDetails()
    episode = episode_num['index']
    if show_original_title != None:
        userId = AnilistService.get_user_id()
        animeId = AnilistService.getAnimeInfo(show_original_title)
        AnilistService.getMediaUserStatus(userId , animeId) 
        AnilistService.setStatusAnime(animeId, 'CURRENT')
        AnilistService.setAnimeUserProgress(animeId, episode)
    else:
        print("No se ha podido añadir el episodio")

# End point
def isPortInUse(port):
    """Check if a port is in use on the local machine."""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return True
    return False   


def openBrowser():
    url = 'http://localhost:5000'
    if not isPortInUse(5000):
        webbrowser.open(url)
    else:
        print(f"Port 5000 is already in use. Please check if the server is already running.")

if __name__ == '__main__':
    openBrowser()
    app.run(debug=True)