from datetime import datetime, timedelta
import requests
import re
from bs4 import BeautifulSoup


def _getWebScrapingHTMLContent(animeTitle, animeYear):
    response = _getSeasonHTMLContent(animeTitle)
    if response.status_code == 404:
        response = _getSearchPageHTMLContent(animeTitle, animeYear)
        animeURL = _getFirstSearchedElement(response.content)
        return requests.get("https://www.thetvdb.com" + animeURL).content
    else:
        return response.content


def _getSeasonHTMLContent(animeTitle):
    animeName = _setFormatSlug(animeTitle)
    website = "https://www.thetvdb.com/series/"
    animeURL = website + animeName + '#seasons'
    return  requests.get(animeURL)

def _getSearchPageHTMLContent(animeTitle, year):
    website = "https://www.thetvdb.com/search?query="
    animeURL = website + _setFormatSearch(animeTitle, year)
    return  requests.get(animeURL)

def _setFormatSlug(text):
    text = re.sub(r'-1$', '', text)
    slugText = text.replace(" ", "-").lower()
    return slugText

def _setFormatSearch(text, animeYear):
    formatedText = re.sub(r'-1$', '', text)
    formatedText = text.replace(" ", "%20").lower()
    formatedText += "&menu%5Btype%5D=series&menu%5Byear%5D=" + str(animeYear)
    return formatedText

def _formatDate(date_str):
    try:
        date = datetime.strptime(date_str, '%B %Y')
        return {"year": date.year, "month": date.month}
    except ValueError:
        return None

def _getFirstSearchedElement(htmlContent):
    soup = BeautifulSoup(htmlContent, 'html.parser')
    list = soup.find('div', id='hits')
    firstElement = list.find_all('li')[0]
    return firstElement.find('a')['href']


def _getSeasonDates(animeTitle, animeYear):
    soup = BeautifulSoup(_getWebScrapingHTMLContent(animeTitle, animeYear), 'html.parser')
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

def getAbsoluteEpisode(originalAnimeName, currentSeason, currentEpisode, animeYear):
    allEpisodesList = _getAnimeListAllEpisode(originalAnimeName, animeYear)
    seasonsList = _getSeasonNumTVDB(originalAnimeName, animeYear)
 
    temporada_index = currentSeason - 1
    
    if temporada_index < 0 or temporada_index >= len(seasonsList):
        raise ValueError("Número de temporada no válido")
    
    if currentEpisode < 1 or currentEpisode > allEpisodesList[temporada_index]:
        raise ValueError("Número de episodio no válido en la temporada especificada")
    
    episodio_absoluto = sum(allEpisodesList[:temporada_index]) + currentEpisode
    return episodio_absoluto

def _getAnimeListAllEpisode(animeTitle, animeYear):
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

def _getSeasonNumTVDB(animeTitle,animeYear):
    pattern = r"/official/[\w-]*"
    findSeasons = re.findall(pattern, str(_getWebScrapingHTMLContent(animeTitle, animeYear)))
    seasonsNumberList = []
    for i in findSeasons:
        seasonNumber = i.replace("/official/", "")
        seasonsNumberList.append(seasonNumber)
    
    return seasonsNumberList

def getNumberOfEpisodesInSeason(animeTitle, seasonNumber, animeYear):
    allEpisodesList = _getAnimeListAllEpisode(animeTitle, animeYear)
    
    if seasonNumber < 1 or seasonNumber > len(allEpisodesList):
        raise ValueError("Número de temporada no válido")
    
    return allEpisodesList[seasonNumber - 1]

def getSeasonFromEpisodeYear(animeTitle, episodeYear, animeYear):
    seasons = _getSeasonDates(animeTitle, animeYear)
    for season in seasons:
        if season['EndDate']['year'] >= episodeYear:
            return season['StartDate']['year']
    
    return print("No se ha encontrado la fecha de después, parece que era el ultimo rango")

def getNextSeasonNum(animeTitle, endYear, animeYear):
    seasons = _getSeasonDates(animeTitle, animeYear)
    last_season_number = None
    
    for index, season in enumerate(seasons):
        if season['StartDate']['year'] <= endYear:
            last_season_number = index + 1 
        else:
            break
    
    if last_season_number is not None:
        return last_season_number
    else:
        return "No se encontró una temporada dentro del rango especificado"
