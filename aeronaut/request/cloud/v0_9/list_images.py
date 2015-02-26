from aeronaut.request.cloud.v0_9.request import Request


class ListImages(Request):

    def with_paging(self):
        return True

    def fields(self):
        return {
            'created': {
                'filter': True
            },

            'image_id': {
                'filter': True,
                'query_key': 'id'
            },

            'location': {
                'filter': True
            },

            'name': {
                'filter': True
            },

            'os_family': {
                'filter': True,
                'query_key': 'operatingSystemFamily'
            },

            'os_id': {
                'filter': True,
                'query_key': 'operatingSystemId'
            },

            'state': {
                'filter': True
            }
        }

    def params(self):
        return {
            'base_or_org_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'get'

    def url(self):
        t = '{base_url}/{base_or_org_id}/imageWithDiskSpeed?'

        return t.format(base_url=self.base_url,
                        base_or_org_id=self.get_param('base_or_org_id'))
