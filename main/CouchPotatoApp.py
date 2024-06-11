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
        animeName = plexEpisodeViewed['titleSlug']
        animeYearEpisode = plexEpisodeViewed['year']
        animeInfo = AnilistService.getAnimeInfo(animeName)

        animeChecker(animeName, animeYearEpisode, animeInfo, season, episode)

    else:
        print(f"No se encuentra el objeto {plexEpisodeViewed}")

def isAnimeGeneric(animeName, yearAnimeChapter, episode):
    animeInfo = AnilistService.getAnimeInfo(animeName)
    startDate = animeInfo['startDate']['year']
    endDate = animeInfo["endDate"]["year"]
    totalEpisodes = animeInfo['episodes']

    return yearAnimeChapter >= startDate and yearAnimeChapter <= endDate and episode <= totalEpisodes

def animeChecker(animeName, episodeYear, animeInfo, season, episode):
    startDate = animeInfo["startDate"]["year"]
    endDate = animeInfo["endDate"]["year"]
    allEpisodes = animeInfo["episodes"]

    if episodeYear >= startDate and episodeYear <= endDate:
        episodes = TVDBService.getNumberOfEpisodesInSeason(animeName, season)
        if allEpisodes != episodes:
            setUpdateAnime(animeInfo, animeName, season, episode)
        else:
            setAnimeProgress(animeName, episode)

    elif episodeYear > endDate:
        year = TVDBService.getNextSeasonDate(animeName, startDate, endDate)
        animeInfoNew = AnilistService.getAnimeInfoDetail(animeName, year)
        episodes = TVDBService.getNumberOfEpisodesInSeason(animeName, season)
        startDateNew = animeInfoNew["startDate"]["year"]
        endDateNew = animeInfoNew["endDate"]["year"]
        totalEpisodes = animeInfoNew["episodes"]
        animeNameNew = animeInfoNew["title"]["native"]

        if totalEpisodes != episodes:
            seasonNum = TVDBService.getNextSeasonNum(animeName, startDateNew, endDateNew)
            modifySeason = season - seasonNum
            setUpdateAnime(animeInfoNew, animeNameNew, modifySeason, episode)
        else:
            setAnimeProgress(animeNameNew, episode)
    '''
    Comprar que los datos de TVDB coincidan con los de anilist
    Se pretende buscar la primera vez con el nombre del show genérico y ya con el año de ese cap trabajamos
    A partir de ahora no tomaremos el numero de la season para hacer la busqueda ya que es muy subjetivo
    Asique usaremos el año de ese episodio y lo formateamos si es necesario
    '''
def setUpdateAnime(animeInfo, animeName, season, episode): 
    if season > 1:
        absoluteEpisode = TVDBService.getAbsoluteEpisode(animeName, season, episode)
        setAnimeProgress(animeInfo, absoluteEpisode)
    else:
        setAnimeProgress(animeInfo, episode)

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