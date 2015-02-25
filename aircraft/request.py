from aircraft.params import Params


class Request(object):

    def __init__(self, auth_data=None, base_url=None, params={}):
        self._auth_data = auth_data
        self._base_url = base_url

        if hasattr(self, 'params'):
            self.__params__ = Params(self.params(), params)

    # =================
    # PUBLIC PROPERTIES
    # =================

    @property
    def base_url(self):
        return self._base_url

    # ==============
    # PUBLIC METHODS
    # ==============

    def basic_auth(self):
        return None

    def body(self):
        return None

    def get_param(self, name):
        if hasattr(self.__params__, name):
            return getattr(self.__params__, name)
        else:
            return None

    def has_param(self, name):
        return self.get_param(name) is not None

    def headers(self):
        return {}

    def http_method(self):
        return None

    def url(self):
        return None
