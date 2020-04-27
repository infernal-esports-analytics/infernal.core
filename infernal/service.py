import os
import re
import sys
import json
import logging

from infernal import common as c
from infernal.session import InfernalHTTPSession
from infernal.exception import InfernalServiceException



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

        self._services = {}
        for service in _found_services:
            if service and self._validate_service(service):
                try:
                    with open(f'{service}/service.json') as f:
                        service_obj = json.load(f)
                    key = service_obj.get('__metadata__',{}).get('service_key')
                    if key:
                        self._services[key] = service

                except Exception as e:
                    logger.warning(
                        f'Could not load {service} due to {e}'
                    )

    def __repr__(self):
        pass

    def __str__(self):
        pass


    def get_service(self, service_key):
        if not service_key in self._services:
            _msg = f'Unknown service "{service_key}"'
            logger.exception(_msg)
            raise InfernalServiceException(_msg)

        with open(f'{self._services[service_key]}/service.json') as f:
            service_doc = json.load(f)

        return service_doc
        


    def _validate_service(self, path):
        if not os.path.exists(path):
            logger.error(f'Service with path {path} does not exist.')
            return None

        _all_children = [p for c in os.walk(path) for p in c[2]]
        
        return 'service.json' in _all_children


class ServiceBase:
    PAT = re.compile(r"\${(?P<arg>\w+)}")


    @property
    def __metadata__(self):
        return dict(self.__service__.get('__metadata__',{}))

    @property
    def requests(self):
        _service_def = dict(self.__service__.get('requests',{}))
        return {k: self._build_url(v.get('url')) for k,v in _service_def.items()}

    @property
    def models(self):
        return dict(self.__service__.get('models',{}))



    def __init__(self, service_data={}, session=None):
        self.session = session or InfernalHTTPSession()
        self.__service__ = service_data

    def __getattr__(self, key):
        def _null_request(*args, **kwargs):
            return None

        if not key in self.requests:
            return self._null_request
        return self._build_method(self.requests[key])


    def meta(self, key, default=None):
        return self.__metadata__.get(key, default)


    def _build_url(self, url):
        return '/'.join([
            self.session.base_url,
            self.meta('service_product'),
            self.meta('service_endpoint'),
            self.meta('service_version'),
            url
        ])

    def _build_method(self, url):
        _args = self.PAT.findall(url)

        def method(*args, **kwargs):
            if len(args) > len(_args):
                _msg = f'Too many arguments provided. Expected {len(_args)}'
                logger.exception(_msg)
                raise InfernalServiceException(_msg)

            params = dict(zip(_args, args))

            for k,v in kwargs.items():
                if not k in _args:
                    _msg = f'Unrecognized argument "{k}"'
                    logger.exception(_msg)
                    raise InfernalServiceException(_msg)
                elif k in params:
                    _msg = f'Argument "{k}" provided more than once'
                    logger.exception(_msg)
                    raise InfernalServiceException(_msg)
                else:
                    params[k] = v

            if not all(a in params for a in _args):
                _misargs = ', '.join([
                    a for a in _args if not a in params
                ])
                _msg = f'Missing required arguments: {_misargs}'
                logger.exception(_msg)
                raise InfernalServiceException(_msg)

            nonlocal url
            for k,v in params.items():
                url = url.replace(f'${{{k}}}', v)

            print(url)
            response = self.session.get(url)
            return json.loads(response.text)

        return method


def create_service(service_key, session=None):
    catalog = ServiceCatalog()
    _service_obj = type(service_key.title(), (ServiceBase,), {})
    return _service_obj(
        service_data=catalog.get_service(service_key),
        session=session
    )

