import re
from bs4 import BeautifulSoup
import requests

# CONSTANTS
API_KEY = 'd0217915-ed05-4e19-8467-35dd4640bdac'
API_URL = 'https://api.thetvdb.com'
URLSeries = f"{API_URL}/search/series" 

# VARIABLES
headers = None
token = None
seriesId = None

def init(self):
    self.token =  getToken()
    if token == None:
        print('Error: Token not defined')
    setHeader(self)    
    return None

def getToken(api_key):
    url = f"{API_URL}/login"
    headers = {'Content-Type': 'application/json'}
    data = {
        'apikey': api_key
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['token']
    else:
        raise Exception("Error al obtener el token de autenticación")

def setHeader(self):
    self.headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }

def getURLEpisodesSummary(seriesId):
    return f"{API_URL}/series/{seriesId}/episodes/summary"

def getAnimeInfo(showOriginalTitle): 
    params = {'name': showOriginalTitle}
    response = requests.get(URLSeries, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Error al buscar la serie")

def getSeasonEpisodes(seriesId, season_number):
    response = requests.get(getURLEpisodesSummary(seriesId), headers=headers)
    if response.status_code == 200:
        seasons = response.json()['data']['airedSeasons']
        if str(season_number) in seasons:
            season_info = response.json()['data']['airedEpisodesBySeason'][str(season_number)]
            return len(season_info)
        else:
            raise Exception(f"Temporada {season_number} no encontrada para la serie con ID {seriesId}")
    else:
        raise Exception("Error al obtener las temporadas de la serie")

def getSeasonDates(seriesId):
    response = requests.get(getURLEpisodesSummary(seriesId), headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        season_dates = {}
        for season, episodes in data['airedEpisodesBySeason'].items():
            first_episode_date = episodes[0]['firstAired'] if episodes else None
            last_episode_date = episodes[-1]['firstAired'] if episodes else None
            season_dates[season] = {
                'firstAired': first_episode_date,
                'lastAired': last_episode_date
            }
        return season_dates
    else:
        raise Exception("Error al obtener las temporadas de la serie")

def getEpisodesPerSeason(seriesId):
    response = requests.get(getURLEpisodesSummary(seriesId), headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        episodesForSeason = {}
        for season, episodes in data['airedEpisodesBySeason'].items():
            if season not in ["0"]:  # Excluyendo "Specials" (season 0)
                episodesForSeason[season] = len(episodes)
        return episodesForSeason
    else:
        raise Exception("Error al obtener las temporadas de la serie")


# Old using Web Scarping

def getAbsoluteEpisode(currentSeason, currentEpisode, animeTitle): 
    return sum(animeListAllEpisode(animeTitle)[:currentSeason - 1]) + currentEpisode

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
 
