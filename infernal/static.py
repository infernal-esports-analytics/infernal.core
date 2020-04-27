import os
import sys
import json
from enum import Enum, unique


# from infernal import common as common


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

class DataDragon(Enum):
    BASE =              'https://static.devele'
