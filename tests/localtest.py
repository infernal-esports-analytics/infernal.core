import context

import os
import re
import sys
import json
import logging
import functools

from infernal import common as c
from infernal.service import create_service


""" Logging Setup """
logger = logging.getLogger('local')
logger.setLevel(logging.INFO)

summoner = create_service('summoner')
match = create_service('match')

shparki = summoner.get_summoner_by_name('Shparki')
c.jprint(shparki)

matchlist = match.get_matches(shparki['accountId'])
c.jprint(matchlist)