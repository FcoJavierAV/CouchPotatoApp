from datetime import datetime, timedelta
import requests
import re
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

options = webdriver.EdgeOptions()
options.add_argument("--headless=old")


def _getWebScrapingHTMLContent(animeTitle, animeYear):
    response = _getSeasonHTMLResponse(animeTitle)
    if response.status_code == 404:
        animeURL = _getAnimeURL(animeTitle, animeYear)
        return requests.get(animeURL).text
    else:
        return response.text


def _getSeasonHTMLResponse(animeTitle):
    animeName = _setFormatSlug(animeTitle)
    website = "https://www.thetvdb.com/series/"
    animeURL = website + animeName + '#seasons'
    return  requests.get(animeURL)
"""

def _getAnimeURL(animeTitle, year):    
    website = "https://www.thetvdb.com/search?query="
    animeURL = website + _setFormatSearch(animeTitle, year)
    edge = webdriver.Edge(options=options)
    edge.get(animeURL)
    animeEntries = edge.find_elements(By.CLASS_NAME, "ais-Hits-item")
    links = []
    for item in animeEntries:
        link = item.find_element(By.TAG_NAME, 'a')
        links.append(link.get_attribute('href'))
    edge.quit()
    return links[0]
"""
def _getAnimeURL(animeTitle, year):
    website = "https://www.thetvdb.com/search?query="
    animeURL = website + _setFormatSearch(animeTitle, year)
    response = requests.get(animeURL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        animeEntries = soup.find_all('div', class_="ais-Hits-item")
        links = []
        for item in animeEntries:
            link = item.find('a', href=True)
            if link:
                links.append(link['href'])
        if links:
            return links[0]
        else:
            return "No se encontraron resultados"
    else:
        return f"Error al acceder a la página. Código de estado: {response.status_code}"

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
    valid_seasons = [index + 1 for index, season in enumerate(seasons) if season['StartDate']['year'] <= endYear]
    
    return valid_seasons[-1] if valid_seasons else "No se encontró una temporada dentro del rango especificado"

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
