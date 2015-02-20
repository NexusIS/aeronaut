from aeronaut.resource.cloud.network import Network, NetworkList


class TestNetwork:

    # =======
    # HELPERS
    # =======

    @property
    def xmlstr(self):
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ns4:NetworkWithLocations
            xmlns:ns16="http://oec.api.opsource.net/schemas/support"
            xmlns="http://oec.api.opsource.net/schemas/server"
            xmlns:ns14="http://oec.api.opsource.net/schemas/manualimport"
            xmlns:ns15="http://oec.api.opsource.net/schemas/reset"
            xmlns:ns9="http://oec.api.opsource.net/schemas/admin"
            xmlns:ns5="http://oec.api.opsource.net/schemas/vip"
            xmlns:ns12="http://oec.api.opsource.net/schemas/datacenter"
            xmlns:ns13="http://oec.api.opsource.net/schemas/storage"
            xmlns:ns6="http://oec.api.opsource.net/schemas/general"
            xmlns:ns7="http://oec.api.opsource.net/schemas/backup"
            xmlns:ns10="http://oec.api.opsource.net/schemas/serverbootstrap"
            xmlns:ns8="http://oec.api.opsource.net/schemas/multigeo"
            xmlns:ns11="http://oec.api.opsource.net/schemas/whitelabel"
            xmlns:ns2="http://oec.api.opsource.net/schemas/directory"
            xmlns:ns4="http://oec.api.opsource.net/schemas/network"
            xmlns:ns3="http://oec.api.opsource.net/schemas/organization">
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

    # =====
    # TESTS
    # =====

    def test_network_attributes(self):
        net = NetworkList(self.xmlstr)[0]

        assert net.id == 'a4ffbcbc-670e-11e3-b29c-001517c4643e'
        assert net.name == 'Collab - Contact'
        assert net.description == 'the description'
        assert net.location == 'NA5'
        assert net.private_net == '10.193.122.0'
        assert net.is_multicast is False

    def test_network_list_items(self):
        nets = NetworkList(self.xmlstr)

        for net in nets:
            assert isinstance(net, Network)
