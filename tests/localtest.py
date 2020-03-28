import conftest

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..'
)))


from infernal import common as c
from infernal.service import ServiceCatalog


catalog = ServiceCatalog()
c.jprint(catalog._services)