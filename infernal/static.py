import os
import sys
import json
from enum import Enum, unique



@unique
class RiotProducts(Enum):
    # League of Legends (LoL)
    LOL =               'lol'

    # Legends of Runterra (LoR)
    LOR =               'lor'

    # Teamfight Tacticts (TFT)
    TFT =               'ltr'



@unique
class RiotEndpoints(Enum):
    BR1 =               'br1.api.riotgames.com'
    EUN1 =              'eun1.api.riotgames.com'
    EUW1 =              'euw1.api.riotgames.com'
    JP1 =               'jp1.api.riotgames.com'
    KR =                'kr.api.riotgames.com'
    LA1 =               'la1.api.riotgames.com'
    LA2 =               'la2.api.riotgames.com'
    NA1 =               'na1.api.riotgames.com'
    OC1 =               'oc1.api.riotgames.com'
    TR1 =               'tr1.api.riotgames.com'
    RU =                'ru.api.riotgames.com'

    AMERICAS =          'americas.api.riotgames.com'
    ASIA =              'asia.api.riotgames.com'
    EUROPE =            'europe.api.riotgames.com'


DataDragonBase = 'https://static.developer.riotgames.come/docs/'
class DataDragon(Enum):
    SEASONS =           'seasons.json'
    QUEUES =            'queues.json'
    MAPS =              'maps.json'
    GAME_MODES =        'gameModes.json'
    GAME_TYPES =        'gameTypes.json'

def get_static_data(dtype, product='lol'):
    pass


class RiotQueuesUnranked(Enum):
    RANKED_SOLO =       'RANKED_SOLO_5x5'
    RANKED_TEAM =       'RANKED_TEAM_5x5'