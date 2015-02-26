from aeronaut.request.cloud.v0_9.request import Request


class ListServers(Request):

    def with_paging(self):
        return True

    def fields(self):
        return {
            'created': {
                'filter': True
            },

            'deployed': {
                'filter': True
            },

            'location': {
                'filter': True
            },

            'machine_name': {
                'filter': True
            },

            'name': {
                'filter': True
            },

            'network_id': {
                'filter': True
            },

            'private_ip': {
                'filter': True
            },

            'server_id': {
                'filter': True,
                'query_key': 'id'
            },

            'source_image_id': {
                'filter': True
            }
        }

    def params(self):
        return {
            'org_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'get'

    def url(self):
        t = '{base_url}/{org_id}/serverWithBackup?'

        return t.format(base_url=self.base_url,
                        org_id=self.get_param('org_id'))
