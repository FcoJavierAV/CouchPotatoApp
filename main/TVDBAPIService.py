import requests
import tvdb_v4_official
from datetime import datetime

APIKEY = "3f9cbd45-f38b-463c-8d97-89e9d6ed94ea"
tvdb = tvdb_v4_official.TVDB(APIKEY)

def _formatDate(date_str):
    try:
        date = datetime.fromisoformat(date_str)
        return date
    except ValueError:
        return None

def get_aired(episode):
    return _formatDate(episode['aired'])

def getSeasonsDates(animeTitle, animeYear):
    name = animeTitle + " " + animeYear
    search = tvdb.search(name)
    seasons = tvdb.get_series_extended(search[0]["id"][7:])["seasons"]
    seasonDates = []
    for season in seasons:
        if season['number'] not in [0, 1, len(season)-1]:
            dates = [get_aired(episode) for episode in tvdb.get_season_extended(season['id'])['episodes']]
            dates.sort()

            seasonDates.append({
                "Temporada": season,
                "StartDate": dates[0],
                "EndDate": dates[-1]
            })
    return seasonDates

def _getAnimeListAllEpisode(animeTitle, animeYear): # To do
    soup = BeautifulSoup(_getWebScrapingHTMLContent(animeTitle, animeYear), 'html.parser')
    seasonTable = soup.find('table', class_='table table-bordered table-hover table-colored')
    episodesForSeason = []
    for row in seasonTable.find_all('tr'):
        columns = row.find_all('td')
        if columns and len(columns) == 4:
            season = columns[0].text.strip()
            if season not in ["Specials", "All Seasons", "Unassigned Episodes"]:
                episodesNumber = int(columns[3].text.strip())
                episodesForSeason.append(episodesNumber)
    
    return episodesForSeason


def getSeasonsNumTVDB(animeTitle, animeYear):
    name = animeTitle + " " + animeYear
    search = tvdb.search(name)
    seasons = tvdb.get_series_extended(search[0]["id"][7:])["seasons"]
    seasonsNumberList = []
    for season in seasons:
        if seasons['number'] not in [0, len(season)-1]:
            seasonNumber = len(seasons)
            seasonsNumberList.append(seasonNumber)
    
    return seasonsNumberList