from datetime import datetime, timedelta
import requests
import re
from bs4 import BeautifulSoup

def _getWebScrapingHTMLContent(animeTitle):
    animeName = _setFormatSlug(animeTitle)
    website = "https://www.thetvdb.com/series/"
    animeURL = website + animeName + '#seasons'
    response = requests.get(animeURL)
    content = response.text
    return content

def _setFormatSlug(text):
    text = re.sub(r'-1$', '', text)
    slugText = text.replace(" ", "-").lower()
    return slugText


def _formatDate(date_str):
    try:
        date = datetime.strptime(date_str, '%B %Y')
        return {"year": date.year, "month": date.month}
    except ValueError:
        return None

def _getSeasonDates(animeTitle):
    soup = BeautifulSoup(_getWebScrapingHTMLContent(animeTitle), 'html.parser')
    seasonTable = soup.find('table', class_='table table-bordered table-hover table-colored')
    seasonDates = []
    
    for fila in seasonTable.find_all('tr'):
        columns = fila.find_all('td')
        if columns and len(columns) == 4:
            season = columns[0].text.strip()
            if season not in ["Specials", "All Seasons", "Unassigned Episodes"]:
                startDate = columns[1].text.strip()
                endDate = columns[2].text.strip()
                formattedStartDate = _formatDate(startDate)
                formattedEndDate = _formatDate(endDate)
                seasonDates.append({
                    "Temporada": season,
                    "StartDate": formattedStartDate,
                    "EndDate": formattedEndDate
                })
    
    return seasonDates

def getAbsoluteEpisode(originalAnimeName, currentSeason, currentEpisode):
    allEpisodesList = getAnimeListAllEpisode(originalAnimeName)
    seasonsList = getSeasonNumTVDB(originalAnimeName)
 
    temporada_index = currentSeason - 1
    
    if temporada_index < 0 or temporada_index >= len(seasonsList):
        raise ValueError("Número de temporada no válido")
    
    if currentEpisode < 1 or currentEpisode > allEpisodesList[temporada_index]:
        raise ValueError("Número de episodio no válido en la temporada especificada")
    
    episodio_absoluto = sum(allEpisodesList[:temporada_index]) + currentEpisode
    return episodio_absoluto

def getAnimeListAllEpisode(animeTitle):
    soup = BeautifulSoup(_getWebScrapingHTMLContent(animeTitle), 'html.parser')
    seasonTable = soup.find('table', class_='table table-bordered table-hover table-colored')
    episodesForSeason = []
    for fila in seasonTable.find_all('tr'):
        columns = fila.find_all('td')
        if columns and len(columns) == 4:
            season = columns[0].text.strip()
            if season not in ["Specials", "All Seasons", "Unassigned Episodes"]:
                episodesNumber = int(columns[3].text.strip())
                episodesForSeason.append(episodesNumber)
    
    return episodesForSeason

def getSeasonNumTVDB(animeTitle):
    pattern = r"/official/[\w-]*"
    findSeasons = re.findall(pattern, str(_getWebScrapingHTMLContent(animeTitle)))
    seasonsNumberList = []
    for i in findSeasons:
        seasonNumber = i.replace("/official/", "")
        seasonsNumberList.append(seasonNumber)
    
    return seasonsNumberList

def getSeasonInfo(animeTitle, seasonNumber):
    allSeasonDates = _getSeasonDates(animeTitle)
    seasonName = f"Season {seasonNumber}"
    for season in allSeasonDates:
        if season["Temporada"] == seasonName:
            return season
    return None

def getNumberOfEpisodesInSeason(animeTitle, seasonNumber):
    allEpisodesList = getAnimeListAllEpisode(animeTitle)
    
    if seasonNumber < 1 or seasonNumber > len(allEpisodesList):
        raise ValueError("Número de temporada no válido")
    
    return allEpisodesList[seasonNumber - 1]

def getNextSeasonDate(animeTitle, start_year, end_year):
    temporadas = _getSeasonDates(animeTitle)
    for temporada in temporadas:
        if temporada['StartDate']['year'] > end_year:
            return temporada['StartDate']['year']
    
    return print("No se ha encontrado la fecha de después, parece que era el ultimo rango")


def getNextSeasonNum(animeTitle, start_year, end_year):
    temporadas = _getSeasonDates(animeTitle)
    last_season_number = None
    
    for index, temporada in enumerate(temporadas):
        if temporada['StartDate']['year'] <= end_year:
            last_season_number = index + 1 
        else:
            break
    
    if last_season_number is not None:
        return last_season_number
    else:
        return "No se encontró una temporada dentro del rango especificado"
