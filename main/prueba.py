import requests
import re

# URL y headers para AniList API
url = "https://graphql.anilist.co"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def _getWebScrapingHTMLContent(animeTitle):
    animeName = _setFormatSlug(animeTitle)
    website = "https://www.thetvdb.com/series/"
    animeURL = website + animeName + '#seasons'
    response = requests.get(animeURL)
    
    if response.status_code == 404:
        print(f"404 error for {animeURL}. Searching for synonyms on AniList...")
        synonym = _getFirstSynonymFromAniList(animeTitle)
        if synonym:
            formattedSynonym = _setFormatSlug(synonym)
            animeURL = website + formattedSynonym + '#seasons'
            response = requests.get(animeURL)
    
    if response.status_code == 200:
        content = response.text
        return content
    else:
        print(f"Error en la solicitud: {response.status_code} for {animeURL}")
        return None

def _setFormatSlug(text):
    text = re.sub(r'-1$', '', text)
    text = text.replace(":", "").replace(" ", "-").lower()
    return text

def _getFirstSynonymFromAniList(animeTitle):
    query = '''
    query ($search: String) {
        Media(search: $search, type: ANIME) {
            synonyms
        }
    }
    '''
    variables = {"search": animeTitle}
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'Media' in data['data']:
            synonyms = data['data']['Media'].get('synonyms', [])
            if synonyms:
                return synonyms[0]
            else:
                print('No synonyms found')
                return None
        else:
            print('Synonyms not found in AniList')
            return None
    else:
        print(f"Error en la solicitud a AniList: {response.status_code}")
        return None

# Ejemplo de uso
animeTitle = "Cowboy Bebop: Tengoku no Tobira"
htmlContent = _getWebScrapingHTMLContent(animeTitle)
if htmlContent:
    print("HTML content fetched successfully.")
else:
    print("Failed to fetch HTML content.")
