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
    seasons = tvdb.get_series_extended(animeSearched(animeTitle, animeYear)[0]["id"][7:])["seasons"]
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

def getAnimeListAllEpisodes(animeTitle, animeYear):
    seasons = tvdb.get_series_extended(animeSearched(animeTitle, animeYear)[0]["id"][7:])["seasons"]   
    episodesForSeasons = []
    for season in seasons:
        if season['type']['name'] == 'Aired Order':
            if season['number'] not in [0, len(season)-1]:
                episodes =  len(tvdb.get_season_extended(season['id'])['episodes'])
                episodesForSeasons.append(episodes)
    
    return episodesForSeasons

def getSeasonsNumTVDB(animeTitle, animeYear):
    series_id = tvdb.get_series_extended(animeSearched(animeTitle, animeYear)[0]["id"][7:])["seasons"]
    seasonsNumberList = []

    for season in series_id:  
        if season.get('type', {}).get('name', '').lower() == 'aired order' and season['number'] not in [0, len(series_id) - 1]:
            seasonsNumberList.append(season['number'])  
        
    return seasonsNumberList

def animeSearched(animeTitle, animeYear):
    name = animeTitle + " " + str(animeYear)
    search = tvdb.search(name.lower())
    return search