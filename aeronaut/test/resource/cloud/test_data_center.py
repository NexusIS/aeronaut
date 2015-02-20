from aeronaut.resource.cloud.data_center \
    import Backup, DataCenter, DataCenterList, DiskSpeed, DiskSpeedList, \
    Hypervisor, Networking


class TestDataCenter:

    # =======
    # HELPERS
    # =======

    @property
    def xmlstr(self):
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ns12:DatacentersWithMaintenanceStatus
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
            <ns12:datacenter ns12:default="false" ns12:location="NA3">
                <ns12:displayName>US - West</ns12:displayName>
                <ns12:city>Santa Clara</ns12:city>
                <ns12:state>California</ns12:state>
                <ns12:country>US</ns12:country>
                <ns12:vpnUrl>https://na3.cloud-vpn.net</ns12:vpnUrl>
                <ns12:networking ns12:type="1" ns12:maintenanceStatus="NORMAL">
                    <ns12:property name="MAX_SERVER_TO_VIP_CONNECTIONS" value="20"/>
                </ns12:networking>
                <ns12:hypervisor ns12:type="VMWARE" ns12:maintenanceStatus="NORMAL">
                    <ns12:diskSpeed ns12:id="STANDARD" ns12:default="true" ns12:available="true">
                        <ns12:displayName>Standard</ns12:displayName>
                        <ns12:abbreviation>STD</ns12:abbreviation>
                        <ns12:description>Standard Disk Speed</ns12:description>
                    </ns12:diskSpeed>
                    <ns12:diskSpeed ns12:id="HIGHPERFORMANCE" ns12:default="false" ns12:available="true">
                        <ns12:displayName>High Performance</ns12:displayName>
                        <ns12:abbreviation>HPF</ns12:abbreviation>
                        <ns12:description>Faster than Standard. Uses 15000 RPM disk with Fast Cache.</ns12:description>
                    </ns12:diskSpeed>
                    <ns12:diskSpeed ns12:id="ECONOMY" ns12:default="false" ns12:available="true">
                        <ns12:displayName>Economy</ns12:displayName>
                        <ns12:abbreviation>ECN</ns12:abbreviation>
                        <ns12:description>Slower than Standard. Uses 7200 RPM disk without Fast Cache.</ns12:description>
                    </ns12:diskSpeed>
                    <ns12:property name="MIN_DISK_SIZE_GB" value="10"/>
                    <ns12:property name="MAX_DISK_SIZE_GB" value="1000"/>
                    <ns12:property name="MAX_TOTAL_ADDITIONAL_STORAGE_GB" value="10000"/>
                    <ns12:property name="MAX_TOTAL_IMAGE_STORAGE_GB" value="2600"/>
                    <ns12:property name="MAX_CPU_COUNT" value="16"/>
                    <ns12:property name="MIN_MEMORY_MB" value="1024"/>
                    <ns12:property name="MAX_MEMORY_MB" value="131072"/>
                </ns12:hypervisor>
                <ns12:backup ns12:type="COMMVAULT" ns12:maintenanceStatus="NORMAL"/>
            </ns12:datacenter>
            <ns12:datacenter ns12:default="false" ns12:location="NA1">
                <ns12:displayName>US - East</ns12:displayName>
                <ns12:city>Ashburn</ns12:city>
                <ns12:state>Virginia</ns12:state>
                <ns12:country>US</ns12:country>
                <ns12:vpnUrl>https://na1.cloud-vpn.net</ns12:vpnUrl>
                <ns12:networking ns12:type="1" ns12:maintenanceStatus="NORMAL">
                    <ns12:property name="MAX_SERVER_TO_VIP_CONNECTIONS" value="20"/>
                </ns12:networking>
                <ns12:hypervisor ns12:type="VMWARE" ns12:maintenanceStatus="NORMAL">
                    <ns12:diskSpeed ns12:id="STANDARD" ns12:default="true" ns12:available="true">
                        <ns12:displayName>Standard</ns12:displayName>
                        <ns12:abbreviation>STD</ns12:abbreviation>
                        <ns12:description>Standard Disk Speed</ns12:description>
                    </ns12:diskSpeed>
                    <ns12:property name="MIN_DISK_SIZE_GB" value="10"/>
                    <ns12:property name="MAX_DISK_SIZE_GB" value="1000"/>
                    <ns12:property name="MAX_TOTAL_ADDITIONAL_STORAGE_GB" value="10000"/>
                    <ns12:property name="MAX_TOTAL_IMAGE_STORAGE_GB" value="2600"/>
                    <ns12:property name="MAX_CPU_COUNT" value="8"/>
                    <ns12:property name="MIN_MEMORY_MB" value="1024"/>
                    <ns12:property name="MAX_MEMORY_MB" value="65536"/>
                </ns12:hypervisor>
                <ns12:backup ns12:type="COMMVAULT" ns12:maintenanceStatus="NORMAL"/>
            </ns12:datacenter>
            <ns12:datacenter ns12:default="true" ns12:location="NA5">
                <ns12:displayName>US - East 2</ns12:displayName>
                <ns12:city>Ashburn</ns12:city>
                <ns12:state>Virginia</ns12:state>
                <ns12:country>US</ns12:country>
                <ns12:vpnUrl>https://na5.cloud-vpn.net</ns12:vpnUrl>
                <ns12:networking ns12:type="1" ns12:maintenanceStatus="NORMAL">
                    <ns12:property name="MAX_SERVER_TO_VIP_CONNECTIONS" value="20"/>
                </ns12:networking>
                <ns12:hypervisor ns12:type="VMWARE" ns12:maintenanceStatus="NORMAL">
                    <ns12:diskSpeed ns12:id="STANDARD" ns12:default="true" ns12:available="true">
                        <ns12:displayName>Standard</ns12:displayName>
                        <ns12:abbreviation>STD</ns12:abbreviation>
                        <ns12:description>Standard Disk Speed</ns12:description>
                    </ns12:diskSpeed>
                    <ns12:diskSpeed ns12:id="HIGHPERFORMANCE" ns12:default="false" ns12:available="true">
                        <ns12:displayName>High Performance</ns12:displayName>
                        <ns12:abbreviation>HPF</ns12:abbreviation>
                        <ns12:description>Faster than Standard. Uses 15000 RPM disk with Fast Cache.</ns12:description>
                    </ns12:diskSpeed>
                    <ns12:diskSpeed ns12:id="ECONOMY" ns12:default="false" ns12:available="true">
                        <ns12:displayName>Economy</ns12:displayName>
                        <ns12:abbreviation>ECN</ns12:abbreviation>
                        <ns12:description>Slower than Standard. Uses 7200 RPM disk without Fast Cache.</ns12:description>
                    </ns12:diskSpeed>
                    <ns12:property name="MIN_DISK_SIZE_GB" value="10"/>
                    <ns12:property name="MAX_DISK_SIZE_GB" value="1000"/>
                    <ns12:property name="MAX_TOTAL_ADDITIONAL_STORAGE_GB" value="10000"/>
                    <ns12:property name="MAX_TOTAL_IMAGE_STORAGE_GB" value="2600"/>
                    <ns12:property name="MAX_CPU_COUNT" value="16"/>
                    <ns12:property name="MIN_MEMORY_MB" value="1024"/>
                    <ns12:property name="MAX_MEMORY_MB" value="131072"/>
                </ns12:hypervisor>
                <ns12:backup ns12:type="COMMVAULT" ns12:maintenanceStatus="NORMAL"/>
            </ns12:datacenter>
        </ns12:DatacentersWithMaintenanceStatus>
        """  # NOQA

    # =====
    # TESTS
    # =====

    def test_data_center_list_items(self):
        dcs = DataCenterList(self.xmlstr)

        for dc in dcs:
            assert isinstance(dc, DataCenter)

    def test_data_center_attributes(self):
        dc = DataCenterList(self.xmlstr)[0]

        assert dc.is_default is False
        assert dc.location == 'NA3'
        assert dc.display_name == 'US - West'
        assert dc.city == 'Santa Clara'
        assert dc.state == 'California'
        assert dc.country == 'US'
        assert dc.vpn_url == 'https://na3.cloud-vpn.net'

        assert isinstance(dc.networking, Networking)
        assert dc.networking.type == 1
        assert dc.networking.maintenance_status == 'NORMAL'
        assert dc.networking.max_server_to_vip_connections == 20
        assert dc.networking['MAX_SERVER_TO_VIP_CONNECTIONS'] == 20

        assert isinstance(dc.hypervisor, Hypervisor)
        assert dc.hypervisor.type == 'VMWARE'
        assert dc.hypervisor.maintenance_status == 'NORMAL'
        assert dc.hypervisor.min_disk_size_gb == 10
        assert dc.hypervisor['MIN_DISK_SIZE_GB'] == 10

        assert isinstance(dc.hypervisor.disk_speeds, DiskSpeedList)

        for speed in dc.hypervisor.disk_speeds:
            assert isinstance(speed, DiskSpeed)

        speed = dc.hypervisor.disk_speeds[0]
        assert speed.id == 'STANDARD'
        assert speed.is_default is True
        assert speed.is_available is True
        assert speed.display_name == 'Standard'
        assert speed.abbreviation == 'STD'
        assert speed.description == 'Standard Disk Speed'

        assert isinstance(dc.backup, Backup)
        assert dc.backup.type == 'COMMVAULT'
        assert dc.backup.maintenance_status == 'NORMAL'
