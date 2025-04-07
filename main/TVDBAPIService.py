import tvdb_v4_official
from datetime import datetime
from readWrite import LoadArchives

APIKEY = LoadArchives.getAccessToken()
tvdb = tvdb_v4_official.TVDB(APIKEY)

def _formatDate(date_str):
    try:
        date = datetime.fromisoformat(date_str)
        return date
    except ValueError:
        return None

def getAired(episode):
    return _formatDate(episode['aired'])

def getSeasonsDates(animeTitle, animeYear):
    try:
        search = tvdb.search(animeTitle)
        search = [s for s in search if s['type'] == "series" and 'year' in s.keys() and s['year'] == str(animeYear)]
        seasons = tvdb.get_series_extended(search[0]["tvdb_id"])["seasons"]
        seasonDates = []
        official_seasons = [season for season in seasons if season['type']['type'] == 'official' and season['number'] != 0]

        for season in official_seasons:
            dates = [getAired(episode) for episode in tvdb.get_season_extended(season['id'])['episodes']]
            dates.sort()
            seasonDates.append({
            "Temporada": season['number'],
            "StartDate": dates[0],
            "EndDate": dates[-1]
            })
        return seasonDates
    except Exception as e:
        return print("Error en la búsqueda")

def getAnimeListAllEpisodes(animeTitle, animeYear):
    seasons = tvdb.get_series_extended(animeSearched(animeTitle, animeYear)[0]["tvdb_id"])["seasons"]   
    episodesForSeasons = []
    for season in seasons:
        if season['type']['type'] == 'official':
            if season['number'] != 0:
                episodes =  len(tvdb.get_season_extended(season['id'])['episodes'])
                episodesForSeasons.append(episodes)
    
    return episodesForSeasons

def getSeasonsNumTVDB(animeTitle, animeYear):
    seasons = tvdb.get_series_extended(animeSearched(animeTitle, animeYear)[0]["tvdb_id"])["seasons"]
    seasonsNumberList = []

    for season in seasons:  
        if season['type']['type'] == 'official' and season['number'] != 0:
            seasonsNumberList.append(season['number'])  
        
    return seasonsNumberList

def animeSearched(animeTitle, animeYear):
    name = animeTitle + " " + str(animeYear)
    search = tvdb.search(name.lower())
    if not search:
        raise ValueError("No se encontraron resultados para la búsqueda.")
    return search
