import threading
import time
from flask import Flask, jsonify, redirect, request, url_for, render_template
import psutil
import webbrowser
import PlexService
import AnilistService
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

plex_credentials = PlexService.getCredentials()
PlexService.connectServer(PlexService, plex_credentials)
anilist_credentials = AnilistService.init(AnilistService)
userId = AnilistService.getUserId()

def completeSessionTask():
    lastPlexEpisodeViewed = None
    while True:
        plexEpisodeViewed = PlexService.getCompletedSessions()
        if plexEpisodeViewed != None and lastPlexEpisodeViewed != plexEpisodeViewed:
            print("Episodio completado")
            if (addEpisode(plexEpisodeViewed)):
                lastPlexEpisodeViewed = plexEpisodeViewed
                plexEpisodeViewed = None
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
    
#Función prueba    
def toStringAnimeInfo():
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


def setAnimeUserProgress():
    if PlexService._checkUserHasActiveSessions() == True:
        animeId = AnilistService.getAnimeId()
        episode_num = PlexService.getSessionDetails()
        episode = episode_num['index']

        AnilistService.setAnimeUserProgress(animeId, episode)

def setAnimeComplete(media_id):
    status = "COMPLETED"
    AnilistService.setAnimeUserStatus(media_id, status)

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

def addEpisode(plexEpisodeViewed):
       
    if plexEpisodeViewed != None:
        season = plexEpisodeViewed['season']
        episode = plexEpisodeViewed['episode']
        animeName = plexEpisodeViewed['originalTitle']
        if season not in [0, 1]:
            str(season)
            animeFull = f"{animeName} {season}"
        else:
            animeFull = animeName
        # Fallo crítico   SEASONSYEAR devuelve o buscas por la fecha
        animeInfo = AnilistService.getAnimeInfo(animeFull)
        # dos posibilidades
        # 1. Primera temporada del anime (nº capitulos pequeño)
        # 2. Todo el anime (sin tener en cuenta arcos, muchos episodios)
        # Muchos episodios significa más episodios que los de la temporada 1

        
        animeId = animeInfo['id']
        animeUser = AnilistService.getAnimeUser(userId, animeId)
        if animeUser == None:
            AnilistService.updateAnimeAndAddCurrent(animeId)
            animeUser = AnilistService.getAnimeUser(userId, animeId)
        if animeInfo['episodes'] == episode and animeUser['status'] == 'CURRENT':
                  return AnilistService.setAnimeUserStatus(animeUser['id'], 'COMPLETED', episode)
        if animeUser['progress'] < episode:
                if animeUser['status'] == 'CURRENT' or  animeUser['status'] == 'PAUSED' or  animeUser['status'] == 'PLANNING':
                    return AnilistService.setAnimeUserStatus(animeUser['id'], 'CURRENT', episode)
                elif animeUser['status'] == 'DROPPED':
                    print("Has abandonado el anime y no se puede añadir")
                elif animeUser['status'] == 'REPEATING' or  animeUser['status'] == 'COMPLETED':
                    return AnilistService.setAnimeUserStatus(animeUser['id'], 'REPEATING', episode)
        
    else:
        print(f"No se encuentra el nombre de {plexEpisodeViewed['originalTitle']}")

def getAbsoluteEpisode(currentSeason, currentEpisode, animeName): 
    return sum(animeListAllEpisode(animeName)[:currentSeason - 1]) + currentEpisode

def animeListAllEpisode(animeTitle):
    soup = BeautifulSoup(getWebScrapingHTMLContent(animeTitle), 'html.parser')
    seasonTable = soup.find('table', class_='table table-bordered table-hover table-colored')
    episodesForSeason = []
    for fila in seasonTable.find_all('tr'):
        columns = fila.find_all('td')
        if columns and len(columns) == 4:
            season = columns[0].text.strip()
            if season not in ["Specials", "All Seasons", "Unassigned Episodes"]:
                episodesNumber = columns[3].text.strip()
                episodesForSeason.append(episodesNumber)
    
    return episodesForSeason

def seasonNumTVDB(animeTitle):
    pattern = r"/official/[\w-]*"
    findSeasons = re.findall(pattern, str(getWebScrapingHTMLContent(animeTitle)))
    seasonsNumberList = []
    for i in findSeasons:
        seasonNumber = i.replace("/official/", "")
        seasonsNumberList.append(seasonNumber)
    
    return seasonsNumberList

def getWebScrapingHTMLContent(animeTitle):
    animeName = animeTitle
    website = "https://www.thetvdb.com/series/"
    animeURL = website + animeName + '#seasons'
    response = requests.get(animeURL)
    content = response.text
    return content

# End point
def isPortInUse(port):
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