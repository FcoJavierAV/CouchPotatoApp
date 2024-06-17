import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import TVDBService, CouchPotatoApp, PlexService, AnilistService


#Test integración, pero poco
#1. Cargar datos (mock Plex y Anilist)
#2. Asertar que se realiza todo correctamente

class TestCouchPotatoApp(unittest.TestCase):

    def setUp(self):    
        self.plexOutputGenericAnime = {'originalTitle': "盾の勇者の成り上がり",
                                'season': 1,
                                'episode': 12,
                                'episodeYear': 2019,
                                'showYear': 2019,
                                'titleSlug': "the-rising-of-the-shield-hero"}
        
        self.anilistAnimeInfo = {"id": 99263,
                                 "episodes": 25,
                                 "format": "TV",
                                 "status": "FINISHED",
                                 "seasonYear": 2019,
                                 "startDate":{
                                    "year": 2019
                                    },
                                 "endDate":{
                                    "year": 2019
                                    } 
                                 }
        
    def test_seeEpisode(self):
        PlexService.getCompletedSessions = MagicMock(return_value=self.plexOutputGenericAnime)
        
        with patch.object(CouchPotatoApp, 'addEpisode') as mock_function_to_be_called:
            CouchPotatoApp.checkCompletedSessions(None)
            
            mock_function_to_be_called.assert_called()

    def test_alreadyJustSeenEpisode(self):
        PlexService.getCompletedSessions = MagicMock(return_value=self.plexOutputGenericAnime)

        with patch.object(CouchPotatoApp, 'addEpisode') as mock_function_to_be_called:
            CouchPotatoApp.checkCompletedSessions(self.plexOutputGenericAnime)

            mock_function_to_be_called.assert_not_called()


    def test_verifyAnimeAndToManageData(self):
        PlexService.getCompletedSessions = MagicMock(return_value=self.plexOutputGenericAnime)
        AnilistService.getAnimeInfo = MagicMock(side_effect=self.anilistServiceGetAnimeInfoMock)

        with    patch.object(CouchPotatoApp, 'setAnimeProgress') as mock_function_to_be_called1, \
                patch.object(AnilistService, 'getAnimeInfoDetail') as mock_function_to_be_called2:
            CouchPotatoApp.checkCompletedSessions(None)

            mock_function_to_be_called1.assert_called()
            mock_function_to_be_called2.assert_not_called()
        

    def anilistServiceGetAnimeInfoMock(self, *args, **kwargs):
        if args[0] == self.plexOutputGenericAnime['titleSlug']:
            return self.anilistAnimeInfo


    def test_getWebScrapingHTMLContent(self):
        TVDBService._getWebScrapingHTMLContent("Mushoku Tensei Jobless Reincarnation", 2021)

if __name__ == '__main__':
    unittest.main()

