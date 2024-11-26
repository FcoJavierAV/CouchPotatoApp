import TVDBAPIService

def getNumberOfEpisodesInSeason(animeTitle, seasonNumber, animeYear): 
    allEpisodesList = TVDBAPIService.getAnimeListAllEpisode(animeTitle, animeYear)
    
    if seasonNumber < 1 or seasonNumber > len(allEpisodesList):
        raise ValueError("Número de temporada no válido")
    
    return allEpisodesList[seasonNumber - 1]

def getSeasonFromEpisodeYear(animeTitle, episodeYear, animeYear):
    seasons = TVDBAPIService.getSeasonDates(animeTitle, animeYear)
    for season in seasons:
        if season['EndDate']['year'] >= episodeYear:
            return season['StartDate']['year']
    
    return print("No se ha encontrado la fecha de después, parece que era el ultimo rango")

def getNextSeasonNum(animeTitle, endYear, animeYear):
    seasons = TVDBAPIService.getSeasonDates(animeTitle, animeYear)
    valid_seasons = [index + 1 for index, season in enumerate(seasons) if season['StartDate']['year'] <= endYear]
    
    return valid_seasons[-1] if valid_seasons else "No se encontró una temporada dentro del rango especificado"

def getAbsoluteEpisode(originalAnimeName, currentSeason, currentEpisode, animeYear): 
    allEpisodesList = TVDBAPIService.getAnimeListAllEpisode(originalAnimeName, animeYear)
    seasonsList = TVDBAPIService.getSeasonNumTVDB(originalAnimeName, animeYear)
 
    temporada_index = currentSeason - 1
    
    if temporada_index < 0 or temporada_index >= len(seasonsList):
        raise ValueError("Número de temporada no válido")
    
    if currentEpisode < 1 or currentEpisode > allEpisodesList[temporada_index]:
        raise ValueError("Número de episodio no válido en la temporada especificada")
    
    episodio_absoluto = sum(allEpisodesList[:temporada_index]) + currentEpisode
    return episodio_absoluto
