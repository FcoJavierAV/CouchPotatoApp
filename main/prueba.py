import re
from bs4 import BeautifulSoup
import requests

# Web Scarping
def animeListAllEpisode(animeTitle):
    soup = BeautifulSoup(getWebScrapingHTMLContent(animeTitle), 'html.parser')
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

def getAbsoluteEpisode(originalAnimeName, currentSeason, currentEpisode):
    allEpisodesList = animeListAllEpisode(originalAnimeName)
    seasonsList = seasonNumTVDB(originalAnimeName)
 
    temporada_index = currentSeason - 1
    
    if temporada_index < 0 or temporada_index >= len(seasonsList):
        raise ValueError("Número de temporada no válido")
    
    if currentEpisode < 1 or currentEpisode > allEpisodesList[temporada_index]:
        raise ValueError("Número de episodio no válido en la temporada especificada")
    
    episodio_absoluto = sum(allEpisodesList[:temporada_index]) + currentEpisode
    return episodio_absoluto

def setFormatSlug(text):
    text = re.sub(r'-1$', '', text)
    slugText = text.replace(" ", "-").lower()
    return slugText
