from aircraft.params import Params


class Request(object):

    def __init__(self, auth_data=None, base_url=None, params={}):
        self._auth_data = auth_data
        self._base_url = base_url

        params_def = self._build_params_def()

        if params_def:
            self.__params__ = Params(params_def, params)

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

    def build_url(self):
        url = self.url()

        if self.with_paging():
            query = []
            page_number = self.get_param('page_number')
            page_size = self.get_param('page_size')

            if page_number:
                query.append("pageNumber={}".format(page_number))

            if page_size:
                query.append("pageSize={}".format(page_size))

            if '?' not in url and query:
                url += "?"

            if query:
                url += "&".join(query)

        return url

    def get_param(self, name):
        if self.has_param(name):
            return getattr(self.__params__, name)
        else:
            return None

    def has_param(self, name):
        return hasattr(self, '__params__') and \
            hasattr(self.__params__, name) and \
            getattr(self.__params__, name) is not None

    def headers(self):
        return {}

    def http_method(self):
        return None

    def url(self):
        return None

    def with_paging(self):
        return False

    # ===============
    # PRIVATE METHODS
    # ===============

    def _build_params_def(self):
        if hasattr(self, 'params'):
            params_def = self.params()
        else:
            params_def = {}

        if self.with_paging():
            for param in ['page_number', 'page_size']:
                params_def[param] = {
                    'required': False,
                    'default': None
                }

        return params_def
