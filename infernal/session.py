import os
import sys
import json
import logging
import functools
from enum import Enum

import requests

from infernal.static import RiotEndpoints
from infernal.exception import InfernalSessionException


""" Logging Setup """
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class InfernalHTTPAuth(requests.auth.AuthBase):
    
    @property
    def key(self):
        return self._key

    @property
    def token(self):
        return self._token


    def __init__(self, key):
        if not key or not isinstance(key, str):
            _msg = f'Invalid key {key}({type(key)})'
            logger.error(_msg)
            raise InfernalSessionException(_msg)

        self._key = key
        self._token = os.environ.get(key)

    def __call__(self, r):
        r.headers['X-Riot-Token'] = self.token
        return r


class InfernalHTTPSession(requests.Session):
    
    @property
    def region(self):
        return self._region.lower()

    @property
    def endpoint(self):
        try:
            return RiotEndpoints[self._region.upper()].value
        except KeyError as e:
            _msg = f'Unknown region {self._region}'
            logger.exception(_msg)
            raise InfernalSessionException(_msg)

    @property
    def base_url(self):
        return f'https://{self.endpoint}'


    def __init__(self, region='na1', auth_key='RIOT_TOKEN'):
        super().__init__()

        self._region = region.lower()

        self.auth = InfernalHTTPAuth(key=auth_key)

    
    def request(self, *args, **kwargs):
        return super().request(*args, **kwargs)


class InfernalHTTPRequest(requests.Request):
    pass