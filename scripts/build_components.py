import os
import sys
import json
import time
import logging
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from selenium import webdriver


""" Logging Setup """
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.INFO, filename='output.log', filemode='w')
logger = logging.getLogger('BuildComponents')
logger.setLevel(logging.INFO)

""" Global Variables """
URL = 'https://developer.riotgames.com/apis'
DRIVER = os.path.join(os.path.dirname(__file__), 'chromedriver')
SITE_FOLDER = 'developer.riotgames.com'

""" Utility Methods """
def jprint(data, load=False, marshall=True, indent=2):
    def _stringify_val(data):
        if isinstance(data, dict):
            return {k:_stringify_val(v) for k,v in data.items()}
        elif isinstance(data, list):
            return [_stringify_val(v) for v in data]
        elif isinstance(data, (str, int, float)):
            return data
        return str(data)
    _data = _stringify_val(data) if marshall else data
    try:
        _d = (
            json.dumps(json.loads(_data), indent=indent) if load else
            json.dumps(_data, indent=indent)
        )
    except:
        _d = _data
    print(_d)


def parse_api_content(api_name):
    tables = {}

    driver = webdriver.Chrome(executable_path=DRIVER)
    driver.get(f'{URL}#{api_name}')
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elements = soup.body.find_all('div', {'api-name': api_name})
    for el in elements:
        ops = el.find_all('li', {'class': 'get operation'})
        defs = {}
        for op in ops:
            logger.info(f'Found element {api_name}.{op["id"]}')

            header = op.find('div', {'class': 'heading'})
            _method = (
                header.find('span', {'class': 'http_method'}).a.text
            )
            _endpoint = (
                header.find('span', {'class': 'path'}).a.text
            )
            _options = [
                li.a.text for li in header.find(
                    'ul', {'class': 'options'}
                ).find_all('li')
            ]
            data = {
                'method': _method,
                'endpoint': _endpoint,
                'options': _options
            }

            Path(f'{SITE_FOLDER}/{api_name}').mkdir(parents=True, exist_ok=True)
            with open(f'{SITE_FOLDER}/{api_name}/{op["id"]}.html', 'w') as f:
                f.write(str(header.prettify()))

            defs[op['id']] = data
        tables.update(defs)

    return tables


page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
_apis = [k for k in soup.body.find_all('div') if k.has_attr('api-name')]
apis = {
    k['api-name']: parse_api_content(k['api-name']) for k in _apis[:]
}

jprint(apis)
