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

def getAnimeListAllEpisode(animeTitle, animeYear):
    name = animeTitle + " " + str(animeYear)
    search = tvdb.search(name)
    seasons = tvdb.get_series_extended(search[0]["id"][7:])["seasons"]
    episodesForSeasons = []
    for season in seasons:
        seasons = tvdb.get_season_extended(seasons[season]["id"])['episodes']
        if season['number'] not in [len(season)-1]:
            episodesNumber = len(seasons)
            episodesForSeasons.append(episodesNumber)

    return episodesForSeasons


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