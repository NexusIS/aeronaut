from aeronaut.request.cloud.v0_9.request import Request


class CleanFailedServerDeployment(Request):

    def params(self):
        return {
            'org_id': {
                'required': True
            },

            'server_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'get'

    def url(self):
        template = "{base_url}/{org_id}/server/{server_id}?clean"

        return template.format(base_url=self.base_url,
                               org_id=self.get_param('org_id'),
                               server_id=self.get_param('server_id'))
