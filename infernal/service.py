import os
import sys
import json
import logging

from infernal import common as c


""" Exceptions """





""" logging config """
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class ServiceCatalog:

    def __init__(self, local_catalog_dir=None):
        _catalog_dir = (
            local_catalog_dir or os.environ.get('local_catalog_dir')
        )
        if not _catalog_dir:
            _catalog_dir = 'services'
            logger.warning(
                'Local service catalog not set through "local_catalog_dir"'
            )

        self._local_catalog_dir = c.get_project_root_dir(_catalog_dir)
        if not os.path.exists(self._local_catalog_dir):
            raise Exception(f'Path {self._local_catalog_dir} does not exist')

        logger.info(
            f'Local catalog directory set to {self._local_catalog_dir}'
        )

        _found_services = [
            os.path.join(self._local_catalog_dir, p)
            for p in os.listdir(self._local_catalog_dir)
            if not str(p).startswith('__')
        ]

        self._services = []
        for service in _found_services:
            if service and self._validate_service(service):
                try:
                    service_obj = Service.service_factory(service)
                    self._services.append(service_obj)
                except Exception as e:
                    logger.warning(
                        f'Could not load {service} due to {e}'
                    )

    
    def __repr__(self):
        pass

    def __str__(self):
        pass


    def _validate_service(self, path):
        if not os.path.exists(path):
            logger.error(f'Service with path {path} does not exist.')
            return None

        _all_children = [p for c in os.walk(path) for p in c[2]]
        
        return 'service.json' in _all_children


class Service:

    BASE_URL = os.environ.get('base_url')
    if not Service.BASE_URL:
        raise Exception('Environment variable "base_url" not set.')


    @classmethod
    def service_factory(cls, service_dir):
        # load in service.json
        _service_def_path = os.path.join(service_dir, 'service.json')
        try:
            with open(_service_def_path) as f:
                service_def = json.load(f)
        except Exception as e:
            logger.error(f'Could not load {_service_def_path} due to {e}')

        return service_def



    @property
    def key(self):
        return self._key
    @property
    def ednpoint(self):
        return self._endpoint
    @property
    def




    def __init__(self, key, endpoint, version, requests={}, models={}):
        self._key = key
        self._endpoint = endpoint
        self._version = version
        self._requests = requests
        self._models = models
