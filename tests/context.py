import os
import sys
import logging


""" Logging Setup """
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.INFO, filename='output.log', filemode='w')


""" Environment Setup """
with open('dev.env') as env:
    for line in env.readlines():
        key,val = [k.strip() for k in line.split('=')]
        os.environ[key]=val

os.environ['local_catalog_dir'] =       'services'
os.environ['base_url'] =                'test'


""" Pathing Setup """
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..'
)))