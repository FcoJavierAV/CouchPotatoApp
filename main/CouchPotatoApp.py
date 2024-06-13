import threading
import time
from flask import Flask, jsonify, redirect, request, url_for, render_template
import psutil
import webbrowser
import PlexService
import AnilistService
import TVDBService
import CouchPotatoApp

app = Flask(__name__)
anilistCredentials = None
userId = None

def startCouchPotatoApp(self):
    plexCredentials = PlexService.getCredentials()
    PlexService.connectServer(PlexService, plexCredentials)
    self.anilistCredentials = AnilistService.init(AnilistService)
    self.userId = AnilistService.getUserId()
    mainThread = threading.Thread(target=completeSessionTask)
    mainThread.start()

def completeSessionTask():#TODO: Think if it is convenient to change this to a file
    while True:
        checkCompletedSessions(None)
        time.sleep(5)

def checkCompletedSessions(lastPlexEpisodeViewed):
    plexEpisodeViewed = PlexService.getCompletedSessions()
    if plexEpisodeViewed != None and lastPlexEpisodeViewed != plexEpisodeViewed:
        print("Episodio completado")
        if (addEpisode(plexEpisodeViewed)):
            lastPlexEpisodeViewed = plexEpisodeViewed
            plexEpisodeViewed = None
    else:
        print("No esta terminando")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    authorization_url = f"https://anilist.co/api/v2/oauth/authorize?client_id={CouchPotatoApp.anilistCredentials['CLIENT_ID']}&redirect_uri={CouchPotatoApp.anilistCredentials['REDIRECT_URI']}&response_type=code"
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400
    AnilistService.getToken(AnilistService, CouchPotatoApp.anilistCredentials, code)   

def addEpisode(plexEpisodeViewed):     
    if plexEpisodeViewed != None:
        season = plexEpisodeViewed['season']
        episode = plexEpisodeViewed['episode']
        animeName = plexEpisodeViewed['titleSlug']
        animeYearEpisode = plexEpisodeViewed['year']
        animeInfo = AnilistService.getAnimeInfo(animeName)

        return animeChecker(animeName, animeYearEpisode, animeInfo, season, episode)

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
            return setUpdateAnime(animeInfo, animeName, season, episode)
        else:
            return setAnimeProgress(animeInfo, episode)

    elif episodeYear > endDate:
        year = TVDBService.getSeasonFromEpisodeYear(animeName, episodeYear)
        animeInfoNew = AnilistService.getAnimeInfoDetail(animeName, year)
        episodes = TVDBService.getNumberOfEpisodesInSeason(animeName, season)
        endDateNew = animeInfoNew["endDate"]["year"]
        totalEpisodes = animeInfoNew["episodes"]

        if totalEpisodes > episodes:
            seasonNum = TVDBService.getNextSeasonNum(animeName, endDateNew)
            modifySeason = season - seasonNum
            return setUpdateAnime(animeInfoNew, animeName, modifySeason, episode)
        elif totalEpisodes < episodes:
            pass
        else:
            return setAnimeProgress(animeInfoNew, episode)
    '''
    Comparar que los datos de TVDB coincidan con los de anilist
    Se pretende buscar la primera vez con el nombre del show genérico y ya con el año de ese cap trabajamos
    A partir de ahora no tomaremos el numero de la season para hacer la busqueda ya que es muy subjetivo
    Asique usaremos el año de ese episodio y lo formateamos si es necesario
    '''
def setUpdateAnime(animeInfo, animeName, season, episode): 
    if season > 1:
        absoluteEpisode = TVDBService.getAbsoluteEpisode(animeName, season, episode)
        return setAnimeProgress(animeInfo, absoluteEpisode)
    else:
        return setAnimeProgress(animeInfo, episode)

def setAnimeProgress(animeInfo, episode):
    animeId = animeInfo['id']
    animeUser = AnilistService.getAnimeUser(CouchPotatoApp.userId, animeId)
    if animeUser == None:
        AnilistService.updateAnimeAndAddCurrent(animeId)
        animeUser = AnilistService.getAnimeUser(CouchPotatoApp.userId, animeId)
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
    startCouchPotatoApp(CouchPotatoApp)
    openBrowser()
    app.run(debug=True)