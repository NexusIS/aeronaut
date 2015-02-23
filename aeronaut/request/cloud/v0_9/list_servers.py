from aeronaut.request.cloud.v0_9.request import Request


class ListServers(Request):

    def params(self):
        return {
            'page_number': {
                'required': False,
                'default': None
            },

            'page_size': {
                'required': False,
                'default': None
            },


            'org_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'get'

    def url(self):
        t = '{base_url}/{org_id}/serverWithBackup?'

        query_str = []

        if self.has_param('page_number'):
            query_str.append('pageNumber={page_number}')

        if self.has_param('page_size'):
            query_str.append('pageSize={page_size}')

        if query_str:
            t += '&'.join(query_str)

        return t.format(base_url=self.base_url,
                        org_id=self.get_param('org_id'),
                        page_number=self.get_param('page_number'),
                        page_size=self.get_param('page_size'))
