from os.path import expanduser, exists, join
import re
import requests
import yaml

from aeronaut.resource.cloud.resource import RootElementNotFoundError
from aircraft.response import Response


# ==========
# EXCEPTIONS
# ==========

class AuthenticationError(Exception):

    def __init__(self, response):
        message = 'Can\'t authenticate against {remote}. ' \
                  'Server returned HTTP status {code}'.format(
                      remote=response.url, code=response.status_code)
        super(AuthenticationError, self).__init__(message)

        self.response = response


class UnauthorizedError(Exception):

    def __init__(self):
        message = "Unable to complete the request due to authorization " \
                  "error. The session has likely expired. Please check " \
                  "and re-authenticate as needed."
        super(UnauthorizedError, self).__init__(message)


# ================
# CONNECTION CLASS
# ================

class CloudConnection(object):

    def __init__(self, endpoint, api_version='v0.9'):
        """Initializes a DiData CloudConnection object without authenticating.

        Args:
            endpoint (str): Then endpoing to connect to.
                For example, 'api-na.dimensiondata.com') Do not prepend
                'https://' to the endpoint!

            api_version (str): The API version to use throughout the connection
                object's lifetime. Defaults to 'v0.9' when not provided.
        """
        self._endpoint = endpoint
        self._api_version = api_version
        self._my_account = None

    # =================
    # PUBLIC PROPERTIES
    # =================

    @property
    def api_version(self):
        return self._api_version

    @property
    def base_url(self):
        return 'https://{}'.format(self.endpoint)

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def is_authenticated(self):
        return self.my_account is not None

    @property
    def my_account(self):
        return self._my_account

    # ==================
    # PRIVATE PROPERTIES
    # ==================

    @property
    def _dotfile_credentials(self):
        """
        Gets the applicable credentials from ~/.aeronaut when available. If
        not available, None will be returned.
        """
        path = join(expanduser('~'), '.aeronaut')

        if not exists(path):
            return None

        if not hasattr(self, '__dotfile_credentials__'):
            with open(path, 'r') as dotfile:
                d = yaml.load(dotfile)
                if self.endpoint not in d:
                    return None
                self.__dotfile_credentials__ = d[self.endpoint]

        return self.__dotfile_credentials__

    @property
    def _http_session(self):
        if not hasattr(self, '__http_session__'):
            self.__http_session__ = requests.Session()

        return self.__http_session__

    # ==============
    # PUBLIC METHODS
    # ==============

    def authenticate(self):
        """Authenticates against the endpoint provided during initialization
        """
        kwargs = {}

        if self._dotfile_credentials is not None:
            credentials = self._dotfile_credentials
            username = credentials['username']
            password = credentials['password']
            kwargs['auth'] = (username, password)

        # The server does pre-emptive basic authentication and self.request()
        # Provides basic auth data when available. So calling any method will
        # automatically authenticate us. We just happen to choose the
        # 'get_my_account' request for this process so that we will have a copy
        # of the account in memory.
        response = self.request('get_my_account', **kwargs)

        if response.status_code in [200, 201]:
            self._my_account = self._deserialize('my_account.MyAccount',
                                                 response.body)
        else:
            raise AuthenticationError(response)

    def create_acl_rule(self, network_id, name, position, action, protocol,
                        type, source_ip=None, source_netmask=None,
                        dest_ip=None, dest_netmask=None, from_port=None,
                        to_port=None, org_id=None):
        """Creates an ACL Rule

        Returns:
            :mod:`aeronaut.resource.cloud.acl.CreateAclRuleStatus`
        """
        if org_id is None:
            org_id = self.my_account.org_id

        params = {
            'type': type,
            'action': action,
            'dest_ip': dest_ip,
            'dest_netmask': dest_netmask,
            'from_port': from_port,
            'name': name,
            'network_id': network_id,
            'org_id': org_id,
            'position': position,
            'protocol': protocol,
            'source_ip': source_ip,
            'source_netmask': source_netmask,
            'to_port': to_port
        }

        response = self.request('create_acl_rule', params=params)
        self._raise_if_unauthorized(response)

        # The underlying REST API is inconsistent. When succesful, it returns
        # an AclRule element, otherwise it returns a Status element. This is an
        # attempt to make our own return value consistent.
        try:
            return self._deserialize('acl.CreateAclRuleStatus', response.body)
        except RootElementNotFoundError:
            xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas/general">
                <ns6:operation>Add ACL Rule</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>ACL Rule created succesfully</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
            </ns6:Status>
            """  # NOQA
            return self._deserialize('acl.CreateAclRuleStatus', xml)

    def create_network(self, location, name, org_id=None, description=None):
        """Creates a network with the given name in the given location

        Args:
            location (str): The data center where the network is to be created.

            name (str): The name of the network

            org_id (str): The ID of the organization who will own this network.
                If not provided, the ``org_id`` member of the authenticated
                user's account will be used.

        Returns:
            :mod:`aeronaut.resource.cloud.network.CreateNetworkStatus
        """
        if org_id is None:
            org_id = self.my_account.org_id

        params = {
            'org_id': org_id,
            'location': location,
            'name': name
        }

        if description:
            params['description'] = description

        response = self.request('create_network', params=params)
        self._raise_if_unauthorized(response)

        return self._deserialize('network.CreateNetworkStatus', response.body)

    def delete_acl_rule(self, network_id, rule_id, org_id=None):
        """Deletes the given rule from the given network

        Returns:
            :mod:`aeronaut.resource.cloud.acl.DeleteAclRuleStatus
        """
        if org_id is None:
            org_id = self.my_account.org_id

        params = {
            'org_id': org_id,
            'network_id': network_id,
            'rule_id': rule_id
        }

        response = self.request('delete_acl_rule', params=params)
        self._raise_if_unauthorized(response)

        return self._deserialize('acl.DeleteAclRuleStatus', response.body)

    def does_image_name_exist(self, image_name, location, org_id=None):
        """Returns True if the given image name exists in the data center

        Returns:
            bool
        """
        if org_id is None:
            org_id = self.my_account.org_id

        params = {
            'org_id': org_id,
            'image_name': image_name,
            'location': location
        }

        response = self.request('does_image_name_exist', params=params)
        self._raise_if_unauthorized(response)
        exists = self._deserialize('image.ImageNameExists', response.body)

        return exists.is_true

    def list_acl_rules(self, network_id, org_id=None):
        """Returns a list of ACL rules

        Returns:
            :mod:`aeronaut.resource.cloud.acl.AclRuleList`
        """
        if not org_id:
            org_id = self.my_account.org_id

        params = {
            'network_id': network_id,
            'org_id': org_id
        }

        response = self.request('list_acl_rules', params=params)
        self._raise_if_unauthorized(response)

        return self._deserialize('acl.AclRuleList', response.body)

    def list_base_images(self, **kwargs):
        """Returns a list of base images

        Returns:
            :mod:`aeronaut.resource.cloud.image.ImageList`
        """
        return self.list_images('base', **kwargs)

    def list_customer_images(self, org_id=None, **kwargs):
        """Returns a list of customer images

        Returns:
            :mod:`aeronaut.resource.cloud.image.ImageList`
        """
        if not org_id:
            org_id = self.my_account.org_id

        return self.list_images(org_id, **kwargs)

    def list_data_centers(self):
        """Returns a list of data centers

        Returns:
            :mod:`aeronaut.resource.cloud.data_center.DataCenterList`
        """
        org_id = self.my_account.org_id
        response = self.request('list_data_centers', params={'org_id': org_id})
        self._raise_if_unauthorized(response)

        return self._deserialize('data_center.DataCenterList', response.body)

    def list_images(self, base_or_org_id, **kwargs):
        """Returns a list of base or customer images

        Returns:
            :mod:`aeronaut.resource.cloud.image.ImageList`
        """
        kwargs['base_or_org_id'] = base_or_org_id

        response = self.request('list_images', params=kwargs)
        self._raise_if_unauthorized(response)
        images = self._deserialize('image.ImageList', response.body)

        return images

    def list_networks(self, org_id=None, location=None):
        """Returns a list of networks

        Args:
            org_id (str): The ID of the organization whose networks you want
                listed. If not provided, the ``org_id`` member of the
                authenticated user's account will be used.

            location (str): Optional. Provide this argument to limit the result
                to the networks in a specific data center. You can get this
                from the ``location`` attribute of a
                :mod:`aeronaut.resource.cloud.data_center.DataCenter` instance.
        """
        if org_id is None:
            org_id = self.my_account.org_id

        params = {'org_id': org_id}

        if isinstance(location, str):
            params['location'] = location

        response = self.request('list_networks', params=params)
        self._raise_if_unauthorized(response)

        return self._deserialize('network.NetworkList', response.body)

    def request(self, req_name, api_version=None, params={}, auth=None):
        """Sends a request to the provider.

        Args:
            req_name (str): The name of the request. For a list of available
                requests, see :mod:`aeronaut.request.cloud`

            api_version (str): The API version to use.

            params (dict): Parameters to be supplied to the request. This can
                vary between requests.

            auth (tuple): A tuple of two strings, username and password, to use
                should the server require authentication.
        """
        if api_version is None:
            api_version = self.api_version

        request = self._build_request(req_name, api_version, params)
        kwargs = {}

        if auth is not None:
            kwargs['auth'] = auth

        if request.http_method() in ['post', 'put'] \
                and request.body() is not None:
            kwargs['data'] = request.body()

        http_method = getattr(self._http_session, request.http_method())
        return Response(http_method(request.url(), **kwargs), request)

    def update_admin_account(self, account):
        """Updates an admin account.

        WARNING: NOT FULLY IMPLEMENTED. NOT TESTED.
        """
        params = account.to_dict(only_dirty=True)
        params['org_id'] = account.org_id
        params['username'] = account.username
        response = self.request('update_admin_account', params=params)
        self._raise_if_unauthorized(response)

        return self._deserialize('request_status.RequestStatus', response.body)

    # ===============
    # PRIVATE METHODS
    # ===============

    def _build_request(self, req_name, api_version, params):
        classname = ''.join([s.capitalize() for s in req_name.split('_')])
        api_version = re.sub('\.', '_', api_version)
        modname = 'aeronaut.request.cloud.{api_version}.{req_name}' \
                  .format(api_version=api_version,
                          req_name=req_name)

        mod = __import__(modname, fromlist=[classname])
        klass = getattr(mod, classname)
        return klass(base_url=self.base_url, params=params)

    def _deserialize(self, classname, xml):
        modname, classname = classname.split('.')
        modname = 'aeronaut.resource.cloud.{}'.format(modname)
        mod = __import__(modname, fromlist=[classname])
        klass = getattr(mod, classname)
        return klass(xml=xml)

    def _raise_if_unauthorized(self, response):
        if response.status_code == 401:
            raise UnauthorizedError()


def connect(endpoint):
    """Creates a new connection to a DiData cloud provider

    Args:
        endpoint (str): Then endpoing to connect to.
            For example, 'api-na.dimensiondata.com') Do not prepend 'https://'
            to the endpoint!

    The module will look for the username and password to use against the given
    endpoint in ``~/.aeronaut``. The file must be YAML formatted and must have
    the following structure::

        api-na.dimensiondata.com:
            username: myuser
            password: mypassword

        another.endpoint.com:
            username: myotheruser
            password: mypasswordtoo!
    """
    conn = CloudConnection(endpoint=endpoint)
    conn.authenticate()
    return conn