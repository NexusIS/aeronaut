from aeronaut.request.cloud.v0_9.request import Request


class ListImages(Request):

    def params(self):
        return {
            'base_or_org_id': {
                'required': True
            },

            'created': {
                'required': False,
                'default': None
            },

            'image_id': {
                'required': False,
                'default': None
            },

            'location': {
                'required': False,
                'default': None
            },

            'name': {
                'required': False,
                'default': None
            },

            'page_number': {
                'required': False,
                'default': None
            },

            'page_size': {
                'required': False,
                'default': None
            },

            'os_family': {
                'required': False,
                'default': None
            },

            'os_id': {
                'required': False,
                'default': None
            },

            'state': {
                'required': False,
                'default': None
            }
        }

    def http_method(self):
        return 'get'

    def url(self):
        t = '{base_url}/{base_or_org_id}/imageWithDiskSpeed?'

        query_str = []

        if self.has_param('page_number'):
            query_str.append('pageNumber={page_number}')

        if self.has_param('page_size'):
            query_str.append('pageSize={page_size}')

        if self.has_param('image_id'):
            query_str.append('id={image_id}')

        if self.has_param('location'):
            query_str.append('location={location}')

        if self.has_param('name'):
            query_str.append('name={name}')

        if self.has_param('created'):
            query_str.append('created={created}')

        if self.has_param('state'):
            query_str.append('state={state}')

        if self.has_param('os_id'):
            query_str.append('os_id={os_id}')

        if self.has_param('os_family'):
            query_str.append('os_family={os_family}')

        if query_str:
            t += '&'.join(query_str)

        return t.format(base_url=self.base_url,
                        base_or_org_id=self.get_param('base_or_org_id'),
                        image_id=self.get_param('image_id'),
                        page_number=self.get_param('page_number'),
                        page_size=self.get_param('page_size'),
                        location=self.get_param('location'),
                        name=self.get_param('name'),
                        created=self.get_param('created'),
                        state=self.get_param('state'),
                        os_id=self.get_param('os_id'),
                        os_family=self.get_param('os_family'))
