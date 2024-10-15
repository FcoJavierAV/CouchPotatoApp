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
        animeInfo = AnilistService.getAnimeInfo(plexEpisodeViewed['titleSlug'])
        return animeChecker(animeInfo, plexEpisodeViewed)

    else:
        print(f"No se encuentra el objeto {plexEpisodeViewed}")

def animeChecker(animeInfo, plexEpisodeViewed):
    episodeYear = plexEpisodeViewed['episodeYear']
    anilistStartDate = animeInfo["startDate"]["year"]
    anilistEndDate = animeInfo["endDate"]["year"]

    if episodeYear >= anilistStartDate and episodeYear <= anilistEndDate:
        return anilistReference(plexEpisodeViewed, animeInfo)

    elif episodeYear > anilistEndDate:
        return anilistWithoutRefence(plexEpisodeViewed)

def anilistWithoutRefence(plexEpisodeViewed):
    season = plexEpisodeViewed['season']
    episode = plexEpisodeViewed['episode']
    animeName = plexEpisodeViewed['titleSlug']
    episodeYear = plexEpisodeViewed['episodeYear']
    animeYear = plexEpisodeViewed['showYear']
    tvdbYear = TVDBService.getSeasonFromEpisodeYear(animeName, episodeYear, animeYear)
    animeInfoNew = AnilistService.getAnimeInfoDetail(animeName, tvdbYear)
    tvdbNumEpisodes = TVDBService.getNumberOfEpisodesInSeason(animeName, season, animeYear)
    anilistEndDateNew = animeInfoNew["endDate"]["year"]
    anilistTotalEpisodes = animeInfoNew["episodes"]

    if anilistTotalEpisodes > tvdbNumEpisodes:
        seasonNum = TVDBService.getNextSeasonNum(animeName, anilistEndDateNew, animeYear)
        modifySeason = season - seasonNum
        return setUpdateAnime(animeInfoNew, animeName, modifySeason, season, animeYear)
    elif anilistTotalEpisodes < tvdbNumEpisodes:
        modifyEpisode = setCorrectEpisode(episode, anilistTotalEpisodes)
        return setAnimeProgress(animeInfoNew, modifyEpisode)
    else:
        return setAnimeProgress(animeInfoNew, episode)

def anilistReference(plexEpisodeViewed, animeInfo):
    season = plexEpisodeViewed['season']
    episode = plexEpisodeViewed['episode']
    animeName = plexEpisodeViewed['titleSlug']
    animeYear = plexEpisodeViewed['showYear']
    anilistAllEpisodes = animeInfo["episodes"]
    tvdbNumEpisodes = TVDBService.getNumberOfEpisodesInSeason(animeName, season, animeYear)
    if anilistAllEpisodes != tvdbNumEpisodes:
        return setUpdateAnime(animeInfo, animeName, season, episode)
    else:
        return setAnimeProgress(animeInfo, episode)

def setCorrectEpisode(currentEpisode, totalExpected):
    return currentEpisode - totalExpected

def setUpdateAnime(animeInfo, animeName, season, episode, animeYear): 
    if season > 1:
        absoluteEpisode = TVDBService.getAbsoluteEpisode(animeName, season, episode, animeYear)
        return setAnimeProgress(animeInfo, absoluteEpisode)
    else:
        return setAnimeProgress(animeInfo, episode)

def setAnimeProgress(animeInfo, episode):
    animeId = animeInfo['id']
    animeUser = AnilistService.getAnimeUser(CouchPotatoApp.userId, animeId)
    if animeUser == None:
        AnilistService.updateAnimeAndAddCurrent(animeId)
        animeUser = AnilistService.getAnimeUser(CouchPotatoApp.userId, animeId)
    if animeInfo['episodes'] == episode and animeUser['status'] in ['CURRENT', 'REPEATING']:
        return AnilistService.setAnimeUserStatus(animeUser['id'], 'COMPLETED', episode)
    elif animeUser['progress'] < episode:
        if animeUser['status'] in ['CURRENT', 'PAUSED', 'PLANNING']:
            return AnilistService.setAnimeUserStatus(animeUser['id'], 'CURRENT', episode)
        elif animeUser['status'] == 'DROPPED':
            print("Has abandonado el anime y no se puede añadir")
        elif animeUser['status'] in ['REPEATING', 'COMPLETED']:
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