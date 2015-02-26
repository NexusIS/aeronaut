from mock import call, MagicMock, Mock, patch
import pytest
import urllib
import uuid

from aeronaut.cloud import connect, UnauthorizedError
from aeronaut.request.cloud.v0_9.get_my_account import GetMyAccount
import aeronaut.resource


class TestCloudConnection:

    # =======
    # HELPERS
    # =======

    @property
    def endpoint(self):
        return 'api-na.dimensiondata.com'

    def mock_backend_authentication(self, mock_httplib, mock_open, mock_yaml):
        """
        Mocks all the objects involved in authenticating a connection. This
        also returns the list of mock return values to requests.Session.get so
        that other tests can add to that if needed.
        """
        # We expect the connection object to read the credentials from
        # ~/.aeronaut if these are not provided in the authenticate method.
        # This block mocks that file.
        mock_open.return_value = MagicMock(spec=file)
        mock_yaml.load.return_value = {
            self.endpoint: {
                'username': 'someuser',
                'password': 'somepassword'
            }
        }

        # Mock the response the the authentication request
        mock_get = mock_httplib.Session.return_value.get
        mock_auth_response = Mock()
        mock_auth_response.status_code = 200
        mock_auth_response.headers = {'content-type': 'text/xml'}
        mock_auth_response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ns2:Account xmlns:ns2="http://oec.api.opsource.net/schemas/directory">
            <ns2:userName>user1</ns2:userName>
            <ns2:fullName>Test</ns2:fullName>
            <ns2:firstName>User</ns2:firstName>
            <ns2:lastName>Uno</ns2:lastName>
            <ns2:emailAddress>user.uno@nowhere.com</ns2:emailAddress>
            <ns2:department>Engineering</ns2:department>
            <ns2:customDefined1>DevOps</ns2:customDefined1>
            <ns2:customDefined2/>
            <ns2:orgId>1234</ns2:orgId>
            <ns2:roles>
                <ns2:role>
                    <ns2:name>server</ns2:name>
                </ns2:role>
                <ns2:role>
                    <ns2:name>create image</ns2:name>
                </ns2:role>
                <ns2:role>
                    <ns2:name>storage</ns2:name>
                </ns2:role>
                <ns2:role>
                    <ns2:name>backup</ns2:name>
                </ns2:role>
            </ns2:roles>
        </ns2:Account>
        """
        mock_get_side_effect = [mock_auth_response]
        mock_get.side_effect = mock_get_side_effect
        return mock_get_side_effect

    # ============
    # authenticate
    # ============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_authenticate(self, mock_httplib, mock_open, mock_yaml):
        self.mock_backend_authentication(mock_httplib, mock_open, mock_yaml)

        # Exercise

        conn = connect(endpoint=self.endpoint)

        # Verify

        assert conn.is_authenticated

        # Verify that it made the correct request to the server
        mock_get = mock_httplib.Session.return_value.get
        req = GetMyAccount(base_url='https://{}'.format(self.endpoint))
        url = req.url()
        usr = mock_yaml.load.return_value[self.endpoint]['username']
        pwd = mock_yaml.load.return_value[self.endpoint]['password']
        assert mock_get.call_args_list == [call(url, auth=(usr, pwd))]

    # ==============================
    # clean_failed_server_deployment
    # ==============================

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_clean_failed_server_deployment(
            self, mock_httplib, mock_open, mock_yaml):
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to create_network
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas/organization">
                <ns6:operation>Clean Server</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>Successfully submitted clean failed server request for server id: {server-id}, private IP address {private-ip- address}</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
                </ns6:Status>
            """  # NOQA
        get_responses.append(response)

        server_id = "someserveridhere"

        # Exercise

        conn = connect(endpoint=self.endpoint)
        status = conn.clean_failed_server_deployment(server_id)

        # Verify

        assert isinstance(status, aeronaut.resource.cloud.resource.Status)

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/server/{server_id}?clean" \
              .format(endpoint=self.endpoint,
                      org_id=conn.my_account.org_id,
                      server_id=server_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # ===============
    # create_acl_rule
    # ===============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_create_acl_rule(self, mock_httplib, mock_open, mock_yaml):
        self.mock_backend_authentication(mock_httplib, mock_open, mock_yaml)

        # Mock the response to create_network
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns4:AclRule xmlns="http://oec.api.opsource.net/schemas/server"
                         xmlns:ns4="http://oec.api.opsource.net/schemas/network">
                <ns4:id>3271ca31-4ea1-4fc5-b7d8-3d11dcf3d1f2</ns4:id>
                <ns4:name>acl-test</ns4:name>
                <ns4:status>NORMAL</ns4:status>
                <ns4:position>150</ns4:position>
                <ns4:action>PERMIT</ns4:action>
                <ns4:protocol>TCP</ns4:protocol>
                <ns4:sourceIpRange>
                    <ns4:ipAddress>192.168.3.0</ns4:ipAddress>
                    <ns4:netmask>255.255.255.0</ns4:netmask>
                </ns4:sourceIpRange>
                <ns4:destinationIpRange>
                    <ns4:ipAddress>192.168.3.0</ns4:ipAddress>
                    <ns4:netmask>255.255.255.0</ns4:netmask>
                </ns4:destinationIpRange>
                <ns4:portRange>
                    <ns4:type>RANGE</ns4:type>
                    <ns4:port1>1</ns4:port1>
                    <ns4:port2>100</ns4:port2>
                </ns4:portRange>
                <ns4:type>OUTSIDE_ACL</ns4:type>
            </ns4:AclRule>
            """  # NOQA
        mock_httplib.Session.return_value.post.return_value = response

        # Exercise

        conn = connect(endpoint=self.endpoint)
        network_id = '12345'
        acl_name = 'acl-test'
        position = 150
        action = 'PERMIT'
        protocol = 'TCP'
        source_ip = '192.168.3.0'
        source_netmask = '255.255.255.0'
        dest_ip = '192.168.3.0'
        dest_netmask = '255.255.255.0'
        from_port = 1
        to_port = 100
        acl_type = 'OUTSIDE_ACL'
        status = conn.create_acl_rule(network_id=network_id,
                                      name=acl_name,
                                      position=position,
                                      action=action,
                                      protocol=protocol,
                                      source_ip=source_ip,
                                      source_netmask=source_netmask,
                                      dest_ip=dest_ip,
                                      dest_netmask=dest_netmask,
                                      from_port=from_port,
                                      to_port=to_port,
                                      type=acl_type)

        # Verify
        assert status.is_success

        # Check that it called the underlying REST API correctly

        url = "https://{endpoint}/oec/0.9/{org_id}/network/" \
              "{network_id}/aclrule".format(endpoint=self.endpoint,
                                            org_id=conn.my_account.org_id,
                                            network_id=network_id)

        template = """
            <AclRule xmlns="http://oec.api.opsource.net/schemas/network">
                <name>{name}</name>
                <position>{position}</position>
                <action>{action}</action>
                <protocol>{protocol}</protocol>

                <sourceIpRange>
                    <ipAddress>{source_ip}</ipAddress>
                    <netmask>{source_netmask}</netmask>
                </sourceIpRange>

                <destinationIpRange>
                    <ipAddress>{dest_ip}</ipAddress>
                    <netmask>{dest_netmask}</netmask>
                </destinationIpRange>

                <portRange>
                    <type>RANGE</type>
                    <port1>{from_port}</port1>
                    <port2>{to_port}</port2>
                </portRange>

                <type>{acl_type}</type>
            </AclRule>"""  # NOQA

        body = template.format(name=acl_name,
                               position=position,
                               action=action,
                               protocol=protocol,
                               source_ip=source_ip,
                               source_netmask=source_netmask,
                               dest_ip=dest_ip,
                               dest_netmask=dest_netmask,
                               from_port=from_port,
                               to_port=to_port,
                               acl_type=acl_type)

        assert mock_httplib.Session.return_value.post.call_args_list[0] == \
            call(url, data=body)

    # ==============
    # create_network
    # ==============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_create_network(self, mock_httplib, mock_open, mock_yaml):
        self.mock_backend_authentication(mock_httplib, mock_open, mock_yaml)

        # Mock the response to create_network
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas/general">
                <ns6:operation>Add Network</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>Network created successfully (Network ID: 4bc16e80-506f-11e3-b29c-001517c4643e)</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
            </ns6:Status>
            """  # NOQA
        mock_httplib.Session.return_value.post.return_value = response

        # Exercise

        network_name = "aeronaut-test-{}".format(uuid.uuid4())
        conn = connect(endpoint=self.endpoint)
        location = "NA3"
        desc = "Test network created by Aeronaut, a Python client library " \
            "for the DiData Cloud and CloudFiles API. This network is safe " \
            "to delete."
        result = conn.create_network(location=location,
                                     name=network_name,
                                     description=desc)

        # Verify

        assert result.is_success

        # Check that it called the underlying REST API correctly

        url = 'https://{endpoint}/oec/0.9/{org_id}/networkWithLocation' \
              .format(endpoint=self.endpoint, org_id=conn.my_account.org_id)
        body_template = """
        <NewNetworkWithLocation xmlns="http://oec.api.opsource.net/schemas/network">
            <name>{name}</name>
            <description>{description}</description>
            <location>{location}</location>
        </NewNetworkWithLocation>
        """  # NOQA
        body = body_template.format(
            location=location, name=network_name, description=desc)

        assert mock_httplib.Session.return_value.post.call_args_list[0] == \
            call(url, data=body)

    # ===============
    # delete_acl_rule
    # ===============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_delete_acl_rule(self, mock_httplib, mock_open, mock_yaml):
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # mock the response to get_my_account
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas/organization">
                <ns6:operation>Delete Acl Rule</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>ACL Rule deleted</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
            </ns6:Status>
        """  # NOQA
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        network_id = '1234'
        rule_id = '5678'
        status = conn.delete_acl_rule(network_id=network_id,
                                      rule_id=rule_id)

        # Verify

        assert status.is_success

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/network/" \
              "{network_id}/aclrule/{rule_id}?delete".format(
                  endpoint=self.endpoint,
                  org_id=conn.my_account.org_id,
                  network_id=network_id,
                  rule_id=rule_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # =============
    # delete_server
    # =============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_delete_server(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas">
                <ns6:operation>Delete Server</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>Server "Delete" issued</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
            </ns6:Status>
            """  # NOQA
        get_responses.append(response)

        server_id = "98b972ce-cc18-49a0-97c2-d87315e08bb1"

        # Exercise

        conn = connect(endpoint=self.endpoint)
        status = conn.delete_server(server_id=server_id)

        # Verify

        assert status.is_success

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/server/{server_id}" \
              "?delete".format(endpoint=self.endpoint,
                               org_id=conn.my_account.org_id,
                               server_id=server_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # =============
    # deploy_server
    # =============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_deploy_server(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        self.mock_backend_authentication(mock_httplib,
                                         mock_open,
                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas/organization">
                <ns6:operation>Deploy Server</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>Request "Deploy Server with Disk Speeds" successful</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
                <additionalInformation name="serverId">
                    <value>4b126b80-26f0-11e4-8e2e-552ad09887dc</value>
                </additionalInformation>
            </ns6:Status>
        """  # NOQA
        mock_httplib.Session.return_value.post.return_value = response

        image_id = '789'
        network_id = '101112'
        name = 'new server'
        description = 'my new server'
        image_id = image_id
        start = True
        admin_password = '123qwe456'
        network_id = network_id
        disks = [
            {'scsi_id': '0', 'speed': 'fast'},
            {'scsi_id': '1', 'speed': 'faster'},
            {'scsi_id': '2', 'speed': 'fasterer'},
        ]

        conn = connect(endpoint=self.endpoint)
        status = conn.deploy_server(name=name,
                                    description=description,
                                    image_id=image_id,
                                    start=start,
                                    admin_password=admin_password,
                                    network_id=network_id,
                                    disks=disks)

        assert status.is_success is True

        # Check that it called the underlying REST API correctly

        url = 'https://{endpoint}/oec/0.9/{org_id}/deployServer' \
              .format(endpoint=self.endpoint, org_id=conn.my_account.org_id)

        body = """
            <DeployServer xmlns="http://oec.api.opsource.net/schemas/server">
                <name>new server</name>
                <description>my new server</description>
                <imageId>789</imageId>
                <start>false</start>
                <administratorPassword>123qwe456</administratorPassword>
                <networkId>101112</networkId>
                <disk scsiId="0" speed="fast"/>
                <disk scsiId="1" speed="faster"/>
                <disk scsiId="2" speed="fasterer"/>
            </DeployServer>"""  # NOQA

        assert mock_httplib.Session.return_value.post.call_args_list[0] == \
            call(url, data=body)

    # =====================
    # does_image_name_exist
    # =====================

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_does_image_name_exists__true(
            self, mock_httplib, mock_open, mock_yaml):
        self.mock_backend_authentication(mock_httplib, mock_open, mock_yaml)

        # Mock the response to does_image_name_exist
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """
            <Exists xmlns="http://oec.api.opsource.net/schemas/general">true</Exists>
            """  # NOQA
        mock_httplib.Session.return_value.post.return_value = response

        image_name = "Whatever"
        location = "NA5"

        # Exercise

        conn = connect(endpoint=self.endpoint)
        result = conn.does_image_name_exist(image_name, location=location)

        # Verify

        assert result is True

        # Check that it called the underlying REST API correctly

        url = 'https://{endpoint}/oec/0.9/{org_id}/image/nameExists' \
              .format(endpoint=self.endpoint, org_id=conn.my_account.org_id)
        body_template = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ImageNameExists xmlns="http://oec.api.opsource.net/schemas/server">
                <location>{location}</location>
                <imageName>{image_name}</imageName>
            </ImageNameExists>
        """  # NOQA
        body = body_template.format(
            location=location, image_name=image_name)

        assert mock_httplib.Session.return_value.post.call_args_list[0] == \
            call(url, data=body)

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_does_image_name_exists__false(
            self, mock_httplib, mock_open, mock_yaml):
        self.mock_backend_authentication(mock_httplib, mock_open, mock_yaml)

        # Mock the response to does_image_name_exist
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """
            <Exists xmlns="http://oec.api.opsource.net/schemas/general">false</Exists>
            """  # NOQA
        mock_httplib.Session.return_value.post.return_value = response

        image_name = "Whatever"
        location = "NA5"

        # Exercise

        conn = connect(endpoint=self.endpoint)
        result = conn.does_image_name_exist(image_name, location=location)

        # Verify

        assert result is False

        # Check that it called the underlying REST API correctly

        url = 'https://{endpoint}/oec/0.9/{org_id}/image/nameExists' \
              .format(endpoint=self.endpoint, org_id=conn.my_account.org_id)
        body_template = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ImageNameExists xmlns="http://oec.api.opsource.net/schemas/server">
                <location>{location}</location>
                <imageName>{image_name}</imageName>
            </ImageNameExists>
        """  # NOQA
        body = body_template.format(
            location=location, image_name=image_name)

        assert mock_httplib.Session.return_value.post.call_args_list[0] == \
            call(url, data=body)

    # ==============
    # get_my_account
    # ==============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_get_my_account(self, mock_httplib, mock_open, mock_yaml):
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # mock the response to get_my_account
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """
            <Account>
                <fullName>Test</fullName>
            </Account>
        """
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        account = conn.my_account

        # Verify

        assert isinstance(account, aeronaut.resource.cloud.account.Account)
        assert account.full_name == 'Test'

    # ================
    # get_server_image
    # ================

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_get_server_image(self, mock_httplib, mock_open, mock_yaml):
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        image_id = '1234'

        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ServerImageWithState>
                <id>{image_id}</id>
                <location>NA1</location>
                <name>My New Customer Image</name>
                <description>Image for producing web servers.</description>
                <operatingSystem>
                    <type>WINDOWS</type>
                    <displayName>WIN2008E/64</displayName>
                </operatingSystem>
                <cpuCount>2</cpuCount>
                <memoryMb>4096</memoryMb>
                <osStorageGb>50</osStorageGb>
                <additionalDisk>
                    <id>ef49974c-87d0-400f-aa32-ee43559fdb1b</id>
                    <scsiId>1</scsiId>
                    <diskSizeGb>40</diskSizeGb>
                    <state>NORMAL</state>
                </additionalDisk>
                <softwareLabel>SAPACCEL</softwareLabel>
                <softwareLabel>MSSQL2008R2E</softwareLabel>
                <source type="IMPORT">
                    <artifact type="MF" value="MyCustomerImage.mf" date="2008-09- 29T02:49:45"/>
                    <artifact type="OVF" value="MyCustomerImage.ovf" date="2008-09- 29T02:49:45"/>
                    <artifact type="VMDK" value="MyCustomerImage-disk1.vmdk" date="2008- 09-29T02:49:45"/>
                    <artifact type="VMDK" value="MyCustomerImage-disk2.vmdk" date="2008- 09-29T02:49:45"/>
                </source>
                <state>FAILED_ADD</state>
                <deployedTime>2012-05-25T12:59:10.110Z</deployedTime>
                <machineStatus name="vmwareToolsApiVersion">
                    <value>8295</value>
                </machineStatus>
                <machineStatus name="vmwareToolsVersionStatus">
                    <value>CURRENT</value>
                </machineStatus>
                <machineStatus name="vmwareToolsRunningStatus">
                    <value>RUNNING</value>
                </machineStatus>
                <status>
                    <action>IMAGE_IMPORT</action>
                    <requestTime>2012-05-25T23:10:36.000Z</requestTime>
                    <userName>theUser</userName>
                    <numberOfSteps>3</numberOfSteps>
                    <updateTime>2012-05-25T23:11:32.000Z</updateTime>
                    <step>
                        <name>WAIT_FOR_OPERATION</name>
                        <number>3</number>
                        <percentComplete>50</percentComplete>
                    </step>
                <failureReason>Operation timed out.</failureReason>
                </status>
            </ServerImageWithState>
            """.format(image_id=image_id)  # NOQA
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        image = conn.get_server_image(image_id=image_id)

        # Verify

        assert isinstance(image, aeronaut.resource.cloud.image.Image)

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/image/{image_id}" \
              .format(endpoint=self.endpoint,
                      org_id=conn.my_account.org_id,
                      image_id=image_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # ==============
    # list_acl_rules
    # ==============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_acl_rules(self, mock_httplib, mock_open, mock_yaml):
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns4:AclRuleList xmlns:ns16="http://oec.api.opsource.net/schemas/support" xmlns="http://oec.api.opsource.net/schemas/server" xmlns:ns14="http://oec.api.opsource.net/schemas/manualimport" xmlns:ns15="http://oec.api.opsource.net/schemas/reset" xmlns:ns9="http://oec.api.opsource.net/schemas/admin" xmlns:ns5="http://oec.api.opsource.net/schemas/vip" xmlns:ns12="http://oec.api.opsource.net/schemas/datacenter" xmlns:ns13="http://oec.api.opsource.net/schemas/storage" xmlns:ns6="http://oec.api.opsource.net/schemas/general" xmlns:ns7="http://oec.api.opsource.net/schemas/backup" xmlns:ns10="http://oec.api.opsource.net/schemas/serverbootstrap" xmlns:ns8="http://oec.api.opsource.net/schemas/multigeo" xmlns:ns11="http://oec.api.opsource.net/schemas/whitelabel" xmlns:ns2="http://oec.api.opsource.net/schemas/directory" xmlns:ns4="http://oec.api.opsource.net/schemas/network" xmlns:ns3="http://oec.api.opsource.net/schemas/organization">
                <ns4:name>ALL_ACL</ns4:name>
                <ns4:AclRule>
                    <ns4:id>978d17e7-6b08-4035-aeda-b588837724eb</ns4:id>
                    <ns4:name>default-98</ns4:name>
                    <ns4:status>NORMAL</ns4:status>
                    <ns4:position>98</ns4:position>
                    <ns4:action>DENY</ns4:action>
                    <ns4:protocol>TCP</ns4:protocol>
                    <ns4:sourceIpRange>
                        <ns4:ipAddress>192.168.10.0</ns4:ipAddress>
                        <ns4:netmask>255.255.255.0</ns4:netmask>
                    </ns4:sourceIpRange>
                    <ns4:destinationIpRange>
                        <ns4:ipAddress>192.168.20.0</ns4:ipAddress>
                        <ns4:netmask>255.255.255.0</ns4:netmask>
                    </ns4:destinationIpRange>
                    <ns4:portRange>
                        <ns4:type>EQUAL_TO</ns4:type>
                        <ns4:port1>587</ns4:port1>
                    </ns4:portRange>
                    <ns4:type>INSIDE_ACL</ns4:type>
                </ns4:AclRule>
                <ns4:AclRule>
                    <ns4:id>46f4e08d-572b-476b-a0e6-004d909d4f12</ns4:id>
                    <ns4:name>default-99</ns4:name>
                    <ns4:status>NORMAL</ns4:status>
                    <ns4:position>99</ns4:position>
                    <ns4:action>DENY</ns4:action>
                    <ns4:protocol>TCP</ns4:protocol>
                    <ns4:sourceIpRange/>
                    <ns4:destinationIpRange/>
                    <ns4:portRange>
                        <ns4:type>EQUAL_TO</ns4:type>
                        <ns4:port1>25</ns4:port1>
                    </ns4:portRange>
                    <ns4:type>INSIDE_ACL</ns4:type>
                </ns4:AclRule>
            </ns4:AclRuleList>
            """  # NOQA
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        network_id = '4bc16e80-506f-11e3-b29c-001517c4643e'
        rules = conn.list_acl_rules(network_id)

        # Verify

        assert isinstance(rules, aeronaut.resource.cloud.acl.AclRuleList)

        for rule in rules:
            assert isinstance(rule, aeronaut.resource.cloud.acl.AclRule)

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/network/{network_id}" \
              "/aclrule".format(endpoint=self.endpoint,
                                org_id=conn.my_account.org_id,
                                network_id=network_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # ================
    # list_base_images
    # ================

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_base_images(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ImagesWithDiskSpeed pageNumber="1" pageCount="147" totalCount="147" pageSize="250">
                <image id="c379cf72-d724-11e2-b29c-001517c4643e" location="NA1">
                    <name>RedHat 6 64-bit 1 CPU</name>
                    <description>RedHat 6.4 Enterprise (Santiago) 64-bit</description>
                    <operatingSystem id="REDHAT664" displayName="REDHAT6/64" type="UNIX"/>
                    <cpuCount>1</cpuCount>
                    <memoryMb>2048</memoryMb>
                    <disk id="3de679b2-d762-11e2-b29c-001517c4643e" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                    <source type="BASE"/>
                    <created>2013-06-17T08:06:07.000Z</created>
                    <state>NORMAL</state>
                </image>
                <image id="26abd500-d729-11e2-b29c-001517c4643e" location="NA1">
                    <name>RedHat 6 64-bit 2 CPU</name>
                    <description>RedHat 6.4 Enterprise (Santiago) 64-bit</description>
                    <operatingSystem id="REDHAT664" displayName="REDHAT6/64" type="UNIX"/>
                    <cpuCount>2</cpuCount>
                    <memoryMb>4096</memoryMb>
                    <disk id="436948b0-d762-11e2-b29c-001517c4643e" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                    <source type="BASE"/>
                    <created>2013-06-17T08:37:31.000Z</created>
                    <state>NORMAL</state>
                </image>
                <image id="9831859e-d729-11e2-b29c-001517c4643e" location="NA1">
                    <name>RedHat 6 32-bit 1 CPU</name>
                    <description>RedHat 6.4 Enterprise (Santiago) 32-bit</description>
                    <operatingSystem id="REDHAT632" displayName="REDHAT6/32" type="UNIX"/>
                    <cpuCount>1</cpuCount>
                    <memoryMb>2048</memoryMb>
                    <disk id="436e8122-d762-11e2-b29c-001517c4643e" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                    <source type="BASE"/>
                    <created>2013-06-17T08:40:42.000Z</created>
                    <state>NORMAL</state>
                </image>
            </ImagesWithDiskSpeed>
            """  # NOQA
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        images = conn.list_base_images()

        # Verify

        assert isinstance(images, aeronaut.resource.cloud.image.ImageList)
        assert len(images) == 3

        for image in images:
            assert isinstance(image, aeronaut.resource.cloud.image.Image)

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/base/imageWithDiskSpeed?" \
              .format(endpoint=self.endpoint)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_base_images__paging(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ImagesWithDiskSpeed pageNumber="5" pageCount="2" totalCount="147" pageSize="2">
                <image id="c379cf72-d724-11e2-b29c-001517c4643e" location="NA1">
                    <name>RedHat 6 64-bit 1 CPU</name>
                    <description>RedHat 6.4 Enterprise (Santiago) 64-bit</description>
                    <operatingSystem id="REDHAT664" displayName="REDHAT6/64" type="UNIX"/>
                    <cpuCount>1</cpuCount>
                    <memoryMb>2048</memoryMb>
                    <disk id="3de679b2-d762-11e2-b29c-001517c4643e" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                    <source type="BASE"/>
                    <created>2013-06-17T08:06:07.000Z</created>
                    <state>NORMAL</state>
                </image>
                <image id="26abd500-d729-11e2-b29c-001517c4643e" location="NA1">
                    <name>RedHat 6 64-bit 2 CPU</name>
                    <description>RedHat 6.4 Enterprise (Santiago) 64-bit</description>
                    <operatingSystem id="REDHAT664" displayName="REDHAT6/64" type="UNIX"/>
                    <cpuCount>2</cpuCount>
                    <memoryMb>4096</memoryMb>
                    <disk id="436948b0-d762-11e2-b29c-001517c4643e" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                    <source type="BASE"/>
                    <created>2013-06-17T08:37:31.000Z</created>
                    <state>NORMAL</state>
                </image>
            </ImagesWithDiskSpeed>
            """  # NOQA
        get_responses.append(response)

        page_size = 2
        page_number = 5

        # Exercise

        conn = connect(endpoint=self.endpoint)
        images = conn.list_base_images(page_size=page_size,
                                       page_number=page_number)

        # Verify

        assert len(images) == 2
        assert images.page_number == 5

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/base/imageWithDiskSpeed?" \
              "pageNumber={page_number}&pageSize={page_size}"  \
              .format(endpoint=self.endpoint,
                      page_size=page_size,
                      page_number=page_number)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_base_images__filter_by_id(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ImagesWithDiskSpeed pageNumber="5" pageCount="2" totalCount="147" pageSize="2">
                <image id="c379cf72-d724-11e2-b29c-001517c4643e" location="NA5">
                    <name>RedHat 6 64-bit 1 CPU</name>
                    <description>RedHat 6.4 Enterprise (Santiago) 64-bit</description>
                    <operatingSystem id="REDHAT664" displayName="REDHAT6/64" type="UNIX"/>
                    <cpuCount>1</cpuCount>
                    <memoryMb>2048</memoryMb>
                    <disk id="3de679b2-d762-11e2-b29c-001517c4643e" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                    <source type="BASE"/>
                    <created>2016-06-17T08:06:07.000Z</created>
                    <state>NORMAL</state>
                </image>
            </ImagesWithDiskSpeed>
            """  # NOQA
        get_responses.append(response)

        filters = [
            ['location', 'equals', 'NA5'],
            ['created', 'greater_than', '2010-09-01T01:00:00Z'],
            ['os_id', 'like', 'RED*64']
        ]

        # Exercise

        conn = connect(endpoint=self.endpoint)
        images = conn.list_base_images(filters=filters)

        # Verify

        assert len(images) == 1

        # Check if the correct HTTP call was made
        query = "location=NA5&created.GREATER_THAN=20150201T00:00:00Z"

        query = "&".join([
            "location=NA5",
            "created.GREATER_THAN=2010-09-01T01:00:00Z",
            "operatingSystemId.LIKE=RED*64"
        ])

        url = "https://{endpoint}/oec/0.9/base/imageWithDiskSpeed?{query}" \
              .format(endpoint=self.endpoint, query=query)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # ====================
    # list_customer_images
    # ====================

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_customer_images(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ImagesWithDiskSpeed pageNumber="1" pageCount="2" totalCount="2" pageSize="250">
                <image id="482f12e4-d789-4173-9411-0b74677d7cfa" location="NA5">
                    <name>Image1</name>
                    <description></description>
                    <operatingSystem id="UBUNTU1264" displayName="UBUNTU12/64" type="UNIX"/>
                    <cpuCount>2</cpuCount>
                    <memoryMb>4096</memoryMb>
                    <disk id="16cfe4e9-17ee-4b8e-aa9b-e62d6f92e771" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                    <source type="CLONE">
                        <artifact type="SERVER_ID" value="b2395c7e-9a85-445d-8025-29ae6f982b8a"/>
                    </source>
                    <created>2014-07-30T00:42:45.000Z</created>
                    <state>NORMAL</state>
                </image>
                <image id="86d3256e-3112-4039-93ca-e44c1e806890" location="NA5">
                    <name>Image2</name>
                    <description></description>
                    <operatingSystem id="CENTOS664" displayName="CENTOS6/64" type="UNIX"/>
                    <cpuCount>1</cpuCount>
                    <memoryMb>2048</memoryMb>
                    <disk id="8e9159b6-6fc7-4d1f-a384-82b07af140a0" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                    <source type="CLONE">
                        <artifact type="SERVER_ID" value="0854be41-125d-4e70-b055-6a7f6d9600dd"/>
                    </source>
                    <created>2014-07-30T00:42:55.000Z</created>
                    <state>NORMAL</state>
                </image>
            </ImagesWithDiskSpeed>
            """  # NOQA
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        images = conn.list_customer_images()

        # Verify

        assert isinstance(images, aeronaut.resource.cloud.image.ImageList)
        assert len(images) == 2

        for image in images:
            assert isinstance(image, aeronaut.resource.cloud.image.Image)

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/imageWithDiskSpeed?" \
              .format(endpoint=self.endpoint,
                      org_id=conn.my_account.org_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_customer_images__paging(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ImagesWithDiskSpeed pageNumber="5" pageCount="2" totalCount="147" pageSize="2">
                <image id="c379cf72-d724-11e2-b29c-001517c4643e" location="NA1">
                    <name>RedHat 6 64-bit 1 CPU</name>
                    <description>RedHat 6.4 Enterprise (Santiago) 64-bit</description>
                    <operatingSystem id="REDHAT664" displayName="REDHAT6/64" type="UNIX"/>
                    <cpuCount>1</cpuCount>
                    <memoryMb>2048</memoryMb>
                    <disk id="3de679b2-d762-11e2-b29c-001517c4643e" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                    <source type="BASE"/>
                    <created>2013-06-17T08:06:07.000Z</created>
                    <state>NORMAL</state>
                </image>
                <image id="26abd500-d729-11e2-b29c-001517c4643e" location="NA1">
                    <name>RedHat 6 64-bit 2 CPU</name>
                    <description>RedHat 6.4 Enterprise (Santiago) 64-bit</description>
                    <operatingSystem id="REDHAT664" displayName="REDHAT6/64" type="UNIX"/>
                    <cpuCount>2</cpuCount>
                    <memoryMb>4096</memoryMb>
                    <disk id="436948b0-d762-11e2-b29c-001517c4643e" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                    <source type="BASE"/>
                    <created>2013-06-17T08:37:31.000Z</created>
                    <state>NORMAL</state>
                </image>
            </ImagesWithDiskSpeed>
            """  # NOQA
        get_responses.append(response)

        page_size = 2
        page_number = 5

        # Exercise

        conn = connect(endpoint=self.endpoint)
        images = conn.list_customer_images(page_size=page_size,
                                           page_number=page_number)

        # Verify

        assert len(images) == 2
        assert images.page_number == 5

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/imageWithDiskSpeed?" \
              "pageNumber={page_number}&pageSize={page_size}"  \
              .format(endpoint=self.endpoint,
                      org_id=conn.my_account.org_id,
                      page_size=page_size,
                      page_number=page_number)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # =================
    # list_data_centers
    # =================

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_data_centers(self, mock_httplib, mock_open, mock_yaml):
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <DatacentersWithMaintenanceStatus>
                <datacenter default="false" location="NA3">
                    <displayName>US - West</displayName>
                </datacenter>
                <datacenter default="false" location="NA1">
                    <displayName>US - East</displayName>
                </datacenter>
            </DatacentersWithMaintenanceStatus>
        """
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        dcs = conn.list_data_centers()

        # Verify

        assert isinstance(
            dcs, aeronaut.resource.cloud.data_center.DataCenterList)
        assert len(dcs) > 0

        dc = dcs[0]

        for dc in dcs:
            assert isinstance(
                dc, aeronaut.resource.cloud.data_center.DataCenter)

        assert dcs[0].display_name == 'US - West'

    # =============
    # list_networks
    # =============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_networks(self, mock_httplib, mock_open, mock_yaml):
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # mock the response to list_networks
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ns4:NetworkWithLocations xmlns:ns4="http://oec.api.opsource.net/schemas/network">
            <ns4:network>
                <ns4:id>a4ffbcbc-670e-11e3-b29c-001517c4643e</ns4:id>
                <ns4:name>Collab - Contact</ns4:name>
                <ns4:description>the description</ns4:description>
                <ns4:location>NA5</ns4:location>
                <ns4:privateNet>10.193.122.0</ns4:privateNet>
                <ns4:multicast>false</ns4:multicast>
            </ns4:network>
            <ns4:network>
                <ns4:id>da20c3a2-0f28-11e3-b29c-001517c4643e</ns4:id>
                <ns4:name>DevOps</ns4:name>
                <ns4:location>NA5</ns4:location>
                <ns4:privateNet>10.192.34.0</ns4:privateNet>
                <ns4:multicast>false</ns4:multicast>
            </ns4:network>
            <ns4:network>
                <ns4:id>4bb558f2-506f-11e3-b29c-001517c4643e</ns4:id>
                <ns4:name>Reporting - Practice</ns4:name>
                <ns4:description>Reporting Server(s) &amp; DB for Nexus practice BI</ns4:description>
                <ns4:location>NA5</ns4:location>
                <ns4:privateNet>10.192.158.0</ns4:privateNet>
                <ns4:multicast>false</ns4:multicast>
            </ns4:network>
        </ns4:NetworkWithLocations>
        """  # NOQA
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        nets = conn.list_networks()

        # Verify

        for net in nets:
            assert net.is_multicast is False

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_networks__auth_expired(
            self, mock_httplib, mock_open, mock_yaml):
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to the request below
        response = Mock()
        response.status_code = 401
        response.headers = {'Content-type': 'text/html;charset=utf-8'}
        response.content = """<html></html>
            """  # NOQA
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        with pytest.raises(UnauthorizedError):
            conn.list_networks()

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_networks__with_filter(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <DatacentersWithMaintenanceStatus>
                <datacenter default="true" location="NA3">
                    <displayName>US - West</displayName>
                </datacenter>
            </DatacentersWithMaintenanceStatus>
        """  # NOQA
        get_responses.append(response)

        # Mock the response to list_networks
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ns4:NetworkWithLocations xmlns:ns4="http://oec.api.opsource.net/schemas/network">
            <ns4:network>
                <ns4:id>a4ffbcbc-670e-11e3-b29c-001517c4643e</ns4:id>
                <ns4:name>Collab - Contact</ns4:name>
                <ns4:description>the description</ns4:description>
                <ns4:location>NA5</ns4:location>
                <ns4:privateNet>10.193.122.0</ns4:privateNet>
                <ns4:multicast>false</ns4:multicast>
            </ns4:network>
            <ns4:network>
                <ns4:id>da20c3a2-0f28-11e3-b29c-001517c4643e</ns4:id>
                <ns4:name>DevOps</ns4:name>
                <ns4:location>NA5</ns4:location>
                <ns4:privateNet>10.192.34.0</ns4:privateNet>
                <ns4:multicast>false</ns4:multicast>
            </ns4:network>
            <ns4:network>
                <ns4:id>4bb558f2-506f-11e3-b29c-001517c4643e</ns4:id>
                <ns4:name>Reporting - Practice</ns4:name>
                <ns4:description>Reporting Server(s) &amp; DB for Nexus practice BI</ns4:description>
                <ns4:location>NA5</ns4:location>
                <ns4:privateNet>10.192.158.0</ns4:privateNet>
                <ns4:multicast>false</ns4:multicast>
            </ns4:network>
        </ns4:NetworkWithLocations>
        """  # NOQA
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        dcs = [dc for dc in conn.list_data_centers() if dc.is_default]
        dc = dcs[0]
        nets = conn.list_networks(location=dc.location)

        # Verify

        assert isinstance(nets, aeronaut.resource.cloud.network.NetworkList)

        for net in nets:
            assert isinstance(net, aeronaut.resource.cloud.network.Network)

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/networkWithLocation/" \
              "{location}".format(endpoint=self.endpoint,
                                  org_id=conn.my_account.org_id,
                                  location=dc.location)

        assert mock_httplib.Session.return_value.get.call_args_list[2] == \
            call(url)

    # ============
    # list_servers
    # ============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_servers(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ServersWithBackup pageNumber="1" pageCount="5" totalCount="5" pageSize="250" xmlns:ns16="http://oec.api.opsource.net/schemas/support" xmlns="http://oec.api.opsource.net/schemas/server" xmlns:ns14="http://oec.api.opsource.net/schemas/manualimport" xmlns:ns15="http://oec.api.opsource.net/schemas/reset" xmlns:ns9="http://oec.api.opsource.net/schemas/admin" xmlns:ns5="http://oec.api.opsource.net/schemas/vip" xmlns:ns12="http://oec.api.opsource.net/schemas/datacenter" xmlns:ns13="http://oec.api.opsource.net/schemas/storage" xmlns:ns6="http://oec.api.opsource.net/schemas/general" xmlns:ns7="http://oec.api.opsource.net/schemas/backup" xmlns:ns10="http://oec.api.opsource.net/schemas/serverbootstrap" xmlns:ns8="http://oec.api.opsource.net/schemas/multigeo" xmlns:ns11="http://oec.api.opsource.net/schemas/whitelabel" xmlns:ns2="http://oec.api.opsource.net/schemas/directory" xmlns:ns4="http://oec.api.opsource.net/schemas/network" xmlns:ns3="http://oec.api.opsource.net/schemas/organization">
                <server id="63e5a7ab-a3ae-4ce3-82d5-c77685290976" location="NA5">
                    <name>Tableau Reporting Server</name>
                    <description>Hosts Tableau Software Reporting Server Engine</description>
                    <operatingSystem id="WIN2012S64" displayName="WIN2012S/64" type="WINDOWS"/>
                    <cpuCount>4</cpuCount>
                </server>
                <server id="2a80508b-aeec-46e2-a0a1-13d0ceee7eef" location="NA5">
                    <name>MySQL Reporting Engine</name>
                    <description>MySQL Database that Holds NITRO Extract for Reporting</description>
                    <operatingSystem id="UBUNTU1264" displayName="UBUNTU12/64" type="UNIX"/>
                    <cpuCount>2</cpuCount>
                    <memoryMb>4096</memoryMb>
                    <machineStatus name="vmwareToolsVersionStatus">
                        <value>NEED_UPGRADE</value>
                    </machineStatus>
                </server>
            </ServersWithBackup>
            """  # NOQA
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        servers = conn.list_servers()

        # Verify

        assert len(servers) == 2
        assert isinstance(servers, aeronaut.resource.cloud.server.ServerList)

        for server in servers:
            assert isinstance(server, aeronaut.resource.cloud.server.Server)

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/serverWithBackup?" \
              .format(endpoint=self.endpoint,
                      org_id=conn.my_account.org_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_servers__paging(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ServersWithBackup pageNumber="2" pageCount="5" totalCount="5" pageSize="2" xmlns:ns16="http://oec.api.opsource.net/schemas/support" xmlns="http://oec.api.opsource.net/schemas/server" xmlns:ns14="http://oec.api.opsource.net/schemas/manualimport" xmlns:ns15="http://oec.api.opsource.net/schemas/reset" xmlns:ns9="http://oec.api.opsource.net/schemas/admin" xmlns:ns5="http://oec.api.opsource.net/schemas/vip" xmlns:ns12="http://oec.api.opsource.net/schemas/datacenter" xmlns:ns13="http://oec.api.opsource.net/schemas/storage" xmlns:ns6="http://oec.api.opsource.net/schemas/general" xmlns:ns7="http://oec.api.opsource.net/schemas/backup" xmlns:ns10="http://oec.api.opsource.net/schemas/serverbootstrap" xmlns:ns8="http://oec.api.opsource.net/schemas/multigeo" xmlns:ns11="http://oec.api.opsource.net/schemas/whitelabel" xmlns:ns2="http://oec.api.opsource.net/schemas/directory" xmlns:ns4="http://oec.api.opsource.net/schemas/network" xmlns:ns3="http://oec.api.opsource.net/schemas/organization">
                <server id="63e5a7ab-a3ae-4ce3-82d5-c77685290976" location="NA5">
                    <name>Tableau Reporting Server</name>
                    <description>Hosts Tableau Software Reporting Server Engine</description>
                    <operatingSystem id="WIN2012S64" displayName="WIN2012S/64" type="WINDOWS"/>
                    <cpuCount>4</cpuCount>
                </server>
                <server id="2a80508b-aeec-46e2-a0a1-13d0ceee7eef" location="NA5">
                    <name>MySQL Reporting Engine</name>
                    <description>MySQL Database that Holds NITRO Extract for Reporting</description>
                    <operatingSystem id="UBUNTU1264" displayName="UBUNTU12/64" type="UNIX"/>
                    <cpuCount>2</cpuCount>
                    <memoryMb>4096</memoryMb>
                    <machineStatus name="vmwareToolsVersionStatus">
                        <value>NEED_UPGRADE</value>
                    </machineStatus>
                </server>
            </ServersWithBackup>
            """  # NOQA
        get_responses.append(response)

        page_size = 2
        page_number = 2

        # Exercise

        conn = connect(endpoint=self.endpoint)
        images = conn.list_servers(page_size=page_size,
                                   page_number=page_number)

        # Verify

        assert len(images) == page_size
        assert images.page_number == page_number

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/serverWithBackup?" \
              "pageNumber={page_number}&pageSize={page_size}"  \
              .format(endpoint=self.endpoint,
                      org_id=conn.my_account.org_id,
                      page_size=page_size,
                      page_number=page_number)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_list_servers__filter(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ServersWithBackup pageNumber="2" pageCount="5" totalCount="5" pageSize="2" xmlns:ns16="http://oec.api.opsource.net/schemas/support" xmlns="http://oec.api.opsource.net/schemas/server" xmlns:ns14="http://oec.api.opsource.net/schemas/manualimport" xmlns:ns15="http://oec.api.opsource.net/schemas/reset" xmlns:ns9="http://oec.api.opsource.net/schemas/admin" xmlns:ns5="http://oec.api.opsource.net/schemas/vip" xmlns:ns12="http://oec.api.opsource.net/schemas/datacenter" xmlns:ns13="http://oec.api.opsource.net/schemas/storage" xmlns:ns6="http://oec.api.opsource.net/schemas/general" xmlns:ns7="http://oec.api.opsource.net/schemas/backup" xmlns:ns10="http://oec.api.opsource.net/schemas/serverbootstrap" xmlns:ns8="http://oec.api.opsource.net/schemas/multigeo" xmlns:ns11="http://oec.api.opsource.net/schemas/whitelabel" xmlns:ns2="http://oec.api.opsource.net/schemas/directory" xmlns:ns4="http://oec.api.opsource.net/schemas/network" xmlns:ns3="http://oec.api.opsource.net/schemas/organization">
                <server id="63e5a7ab-a3ae-4ce3-82d5-c77685290976" location="NA5">
                    <name>Tableau Reporting Server</name>
                    <description>Hosts Tableau Software Reporting Server Engine</description>
                    <operatingSystem id="WIN2012S64" displayName="WIN2012S/64" type="WINDOWS"/>
                    <cpuCount>4</cpuCount>
                </server>
                <server id="2a80508b-aeec-46e2-a0a1-13d0ceee7eef" location="NA5">
                    <name>MySQL Reporting Engine</name>
                    <description>MySQL Database that Holds NITRO Extract for Reporting</description>
                    <operatingSystem id="UBUNTU1264" displayName="UBUNTU12/64" type="UNIX"/>
                    <cpuCount>2</cpuCount>
                    <memoryMb>4096</memoryMb>
                    <machineStatus name="vmwareToolsVersionStatus">
                        <value>NEED_UPGRADE</value>
                    </machineStatus>
                </server>
            </ServersWithBackup>
            """  # NOQA
        get_responses.append(response)

        # Exercise

        conn = connect(endpoint=self.endpoint)
        conn.list_servers(filters=["machine_name", "==", "something"])

        # Verify

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/serverWithBackup?" \
              "machineName=something"  \
              .format(endpoint=self.endpoint,
                      org_id=conn.my_account.org_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # =============
    # modify_server
    # =============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_modify_server(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        self.mock_backend_authentication(mock_httplib,
                                         mock_open,
                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas/support">
                <ns6:operation>Edit Server</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>Server edited</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
            </ns6:Status>
        """  # NOQA
        mock_httplib.Session.return_value.post.return_value = response

        server_id = "98b972ce-cc18-49a0-97c2-d87315e08bb1"
        name = "newname"
        description = "new description"
        cpu_count = 2
        memory = 2048

        # Exercise

        conn = connect(endpoint=self.endpoint)
        status = conn.modify_server(server_id=server_id,
                                    name=name,
                                    description=description,
                                    cpu_count=cpu_count,
                                    memory=memory)

        # Verify

        assert status.is_success

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/server/{server_id}" \
              .format(endpoint=self.endpoint,
                      org_id=conn.my_account.org_id,
                      server_id=server_id)

        headers = {
            'Content-type': 'application/x-www-form-urlencoded'
        }

        payload = {}
        for param in ['description', 'memory', 'name']:
            payload[param] = eval(param)
        payload['cpuCount'] = eval('cpu_count')
        body = urllib.urlencode(payload)

        assert mock_httplib.Session.return_value.post.call_args_list[0] == \
            call(url, data=body, headers=headers)

    # ===============
    # poweroff_server
    # ===============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_poweroff_server(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas/organization">
                <ns6:operation>Power Off Server</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>Server "Power Off" issued</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
            </ns6:Status>"""  # NOQA
        get_responses.append(response)

        server_id = "98b972ce-cc18-49a0-97c2-d87315e08bb1"

        # Exercise

        conn = connect(endpoint=self.endpoint)
        status = conn.poweroff_server(server_id=server_id)

        # Verify

        assert status.is_success

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/server/{server_id}" \
              "?poweroff".format(endpoint=self.endpoint,
                                 org_id=conn.my_account.org_id,
                                 server_id=server_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # =============
    # reboot_server
    # =============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_reboot_server(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas">
                <ns6:operation>Reboot Server</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>Server "Reboot" issued</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
            </ns6:Status>
            """  # NOQA
        get_responses.append(response)

        server_id = "98b972ce-cc18-49a0-97c2-d87315e08bb1"

        # Exercise

        conn = connect(endpoint=self.endpoint)
        status = conn.reboot_server(server_id=server_id)

        # Verify

        assert status.is_success

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/server/{server_id}" \
              "?reboot".format(endpoint=self.endpoint,
                               org_id=conn.my_account.org_id,
                               server_id=server_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # ============
    # reset_server
    # ============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_reset_server(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas/organization">
                <ns6:operation>Reset Server</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>Server "Reset" issued</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
            </ns6:Status>"""  # NOQA
        get_responses.append(response)

        server_id = "98b972ce-cc18-49a0-97c2-d87315e08bb1"

        # Exercise

        conn = connect(endpoint=self.endpoint)
        status = conn.reset_server(server_id=server_id)

        # Verify

        assert status.is_success

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/server/{server_id}" \
              "?reset".format(endpoint=self.endpoint,
                              org_id=conn.my_account.org_id,
                              server_id=server_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # ===============
    # shutdown_server
    # ===============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_shutdown_server(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas/organization">
                <ns6:operation>Graceful Shutdown Server</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>Server "Graceful Shutdown" issued</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
            </ns6:Status>
            """  # NOQA
        get_responses.append(response)

        server_id = "98b972ce-cc18-49a0-97c2-d87315e08bb1"

        # Exercise

        conn = connect(endpoint=self.endpoint)
        status = conn.shutdown_server(server_id=server_id)

        # Verify

        assert status.is_success

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/server/{server_id}" \
              "?shutdown".format(endpoint=self.endpoint,
                                 org_id=conn.my_account.org_id,
                                 server_id=server_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)

    # ============
    # start_server
    # ============

    @patch('aeronaut.cloud.yaml', autospec=True)
    @patch('aeronaut.cloud.open', create=True)
    @patch('aeronaut.cloud.requests', autospec=True)
    def test_start_server(
            self, mock_httplib, mock_open, mock_yaml):
        # Mocked responses to HTTP get
        get_responses = self.mock_backend_authentication(mock_httplib,
                                                         mock_open,
                                                         mock_yaml)

        # Mock the response to list_data_centers
        response = Mock()
        response.headers = {'content-type': 'text/xml'}
        response.content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas/organization">
                <ns6:operation>Start Server</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>Server "Start" issued</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
            </ns6:Status>
            """  # NOQA
        get_responses.append(response)

        server_id = "98b972ce-cc18-49a0-97c2-d87315e08bb1"

        # Exercise

        conn = connect(endpoint=self.endpoint)
        status = conn.start_server(server_id=server_id)

        # Verify

        assert status.is_success

        # Check if the correct HTTP call was made
        url = "https://{endpoint}/oec/0.9/{org_id}/server/{server_id}" \
              "?start".format(endpoint=self.endpoint,
                              org_id=conn.my_account.org_id,
                              server_id=server_id)

        assert mock_httplib.Session.return_value.get.call_args_list[1] == \
            call(url)
