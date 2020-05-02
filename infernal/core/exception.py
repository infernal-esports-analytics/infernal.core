from requests import RequestException


""" Exception Bases """
class InfernalException(Exception):
    """ Core Infernal Exception """





""" Service Exceptions """
class InfernalServiceException(InfernalException):
    """ Infernal Service Exception """



""" Session Exceptions """
class InfernalSessionException(InfernalException):
    """ Infernal Session Exception """


class InfernalHTTPException(InfernalException, RequestException):

    def __init__(self, response=None, request=None, *args, **kwargs):
        super().__init__(response=response, request=request, *args, **kwargs)