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
r = summoner.get_summoner_by_id('6ui6PSeq6TL6qS_CJfeTkMSaYh4pKllD4sSQZdQUvhEw4Sw')
c.jprint(r)