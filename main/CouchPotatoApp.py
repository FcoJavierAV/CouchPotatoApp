import threading
import time
from flask import Flask, jsonify, redirect, request, url_for, render_template
import psutil
import webbrowser
import PlexService
import AnilistService
import TVDBService

app = Flask(__name__)

plexCredentials = PlexService.getCredentials()
PlexService.connectServer(PlexService, plexCredentials)
anilistCredentials = AnilistService.init(AnilistService)
userId = AnilistService.getUserId()
TVDBCredentials = TVDBService.init(TVDBService)

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
    authorization_url = f"https://anilist.co/api/v2/oauth/authorize?client_id={anilistCredentials['CLIENT_ID']}&redirect_uri={anilistCredentials['REDIRECT_URI']}&response_type=code"
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400
    AnilistService.getToken(AnilistService, anilistCredentials, code)   

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
        
        # Fallo crítico   SEASONSYEAR devuelve o buscas por la fecha
        animeInfo = AnilistService.getAnimeInfo(animeName)
        episodesInSeasons = getCountAnimeEpisodesForSeason(animeName, season)

        if animeInfo['episodes'] == episodesInSeasons:
            if season not in [0, 1]:
                str(season)
                animeFull = f"{animeName} {season}"
            else:
                animeFull = animeName
            animeInfo = AnilistService.getAnimeInfo(animeFull)

        else:
            pass           
        # dos posibilidades
        # 1. Primera temporada del anime (nº capitulos pequeño)
        # 2. Todo el anime (sin tener en cuenta arcos, muchos episodios)
        # Muchos episodios significa más episodios que los de la temporada 1
        #animeInfoDetail = AnilistService.getAnimeInfoDetail(animeFull)

        if plexEpisodeViewed['year'] >= animeInfo['startDate']['year'] and plexEpisodeViewed['year'] <= animeInfo['endDate']['year']:
            print("Estas dentro de la temporada")  
        else:
            print("Estas fuera de esta temporada")   

        setAnimeProgress(animeInfo, episode)
        
    else:
        print(f"No se encuentra el objeto {plexEpisodeViewed}")

def getCountAnimeEpisodesForSeason(showOriginalTitle, season):   
    TVDBAnimeId = TVDBService.getAnimeInfo(showOriginalTitle)
    allEpisodesForSeason = TVDBService.getSeasonEpisodes(TVDBAnimeId, season)

    return allEpisodesForSeason

def isAnimeGeneric(animeName, season):
    episodesInSeasons = getCountAnimeEpisodesForSeason(animeName, season)

    return False


def setAnimeProgress(animeInfo, episode):
    animeId = animeInfo['id']
    animeUser = AnilistService.getAnimeUser(userId, animeId)
    if animeUser == None:
        AnilistService.updateAnimeAndAddCurrent(animeId)
        animeUser = AnilistService.getAnimeUser(userId, animeId)
    if animeInfo['episodes'] == episode and animeUser['status'] == 'CURRENT':
                return AnilistService.setAnimeUserStatus(animeUser['id'], 'COMPLETED', episode)
    elif animeUser['progress'] < episode:
            if animeUser['status'] == 'CURRENT' or  animeUser['status'] == 'PAUSED' or  animeUser['status'] == 'PLANNING':
                return AnilistService.setAnimeUserStatus(animeUser['id'], 'CURRENT', episode)
            elif animeUser['status'] == 'DROPPED':
                print("Has abandonado el anime y no se puede añadir")
            elif animeUser['status'] == 'REPEATING' or  animeUser['status'] == 'COMPLETED':
                return AnilistService.setAnimeUserStatus(animeUser['id'], 'REPEATING', episode)
        
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