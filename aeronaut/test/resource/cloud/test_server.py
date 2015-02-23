from aeronaut.resource.cloud.server import Server, ServerList

XMLSTR = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ServersWithBackup pageNumber="1" pageCount="5" totalCount="5" pageSize="250" xmlns:ns16="http://oec.api.opsource.net/schemas/support" xmlns="http://oec.api.opsource.net/schemas/server" xmlns:ns14="http://oec.api.opsource.net/schemas/manualimport" xmlns:ns15="http://oec.api.opsource.net/schemas/reset" xmlns:ns9="http://oec.api.opsource.net/schemas/admin" xmlns:ns5="http://oec.api.opsource.net/schemas/vip" xmlns:ns12="http://oec.api.opsource.net/schemas/datacenter" xmlns:ns13="http://oec.api.opsource.net/schemas/storage" xmlns:ns6="http://oec.api.opsource.net/schemas/general" xmlns:ns7="http://oec.api.opsource.net/schemas/backup" xmlns:ns10="http://oec.api.opsource.net/schemas/serverbootstrap" xmlns:ns8="http://oec.api.opsource.net/schemas/multigeo" xmlns:ns11="http://oec.api.opsource.net/schemas/whitelabel" xmlns:ns2="http://oec.api.opsource.net/schemas/directory" xmlns:ns4="http://oec.api.opsource.net/schemas/network" xmlns:ns3="http://oec.api.opsource.net/schemas/organization">
    <server id="63e5a7ab-a3ae-4ce3-82d5-c77685290976" location="NA5">
        <name>Reporting Server</name>
        <description>Software Reporting Server Engine</description>
        <operatingSystem id="WIN2012S64" displayName="WIN2012S/64" type="WINDOWS"/>
        <cpuCount>4</cpuCount>
        <memoryMb>8192</memoryMb>
        <disk id="cc77c436-314a-4c06-9a5d-e2aa4391fb8a" scsiId="0" sizeGb="50" speed="STANDARD" state="NORMAL"/>
        <sourceImageId>4787337e-0f31-11e3-b29c-001517c4643e</sourceImageId>
        <networkId>4bb558f2-506f-11e3-b29c-001517c4643e</networkId>
        <machineName>10-192-158-11</machineName>
        <privateIp>10.192.158.11</privateIp>
        <publicIp>162.216.171.60</publicIp>
        <created>2014-07-11T03:48:17.000Z</created>
        <isDeployed>true</isDeployed>
        <isStarted>true</isStarted>
        <state>NORMAL</state>
        <machineStatus name="vmwareToolsVersionStatus">
            <value>NEED_UPGRADE</value>
        </machineStatus>
        <machineStatus name="vmwareToolsRunningStatus">
            <value>RUNNING</value>
        </machineStatus>
        <machineStatus name="vmwareToolsApiVersion">
            <value>9221</value>
        </machineStatus>
        <status>
            <action>START_SERVER</action>
            <requestTime>2012-09-26T08:36:28</requestTime>
            <userName>btaylor</userName>
            <numberOfSteps>3</numberOfSteps>
            <updateTime>2012-09-26T08:37:28</updateTime>
            <step>
                <name>Waiting for operation</name>
                <number>3</number>
                <percentComplete>3</percentComplete>
            </step>
            <failureReason>Message Value</failureReason>
        </status>
        <backup assetId="5c1956d9-4e30-4b74-9fa1-10a0f272f08e" state="NORMAL" servicePlan="Advanced"/>
    </server>
    <server id="2a80508b-aeec-46e2-a0a1-13d0ceee7eef" location="NA5">
        <name>MySQL Reporting Engine</name>
        <description>MySQL Database</description>
        <operatingSystem id="UBUNTU1264" displayName="UBUNTU12/64" type="UNIX"/>
        <cpuCount>2</cpuCount>
        <memoryMb>4096</memoryMb>
        <disk id="a3d1358f-725d-4387-8563-bc1dcd6a4b4e" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
        <disk id="32143502-b23f-4693-aa3c-73ef88d89811" scsiId="1" sizeGb="10" speed="HIGHPERFORMANCE" state="NORMAL"/>
        <sourceImageId>47866124-0f31-11e3-b29c-001517c4643e</sourceImageId>
        <networkId>4bb558f2-506f-11e3-b29c-001517c4643e</networkId>
        <machineName>10-192-158-12</machineName>
        <privateIp>10.192.158.12</privateIp>
        <publicIp>162.216.171.61</publicIp>
        <created>2014-07-11T03:59:29.000Z</created>
        <isDeployed>true</isDeployed>
        <isStarted>true</isStarted>
        <softwareLabel>REDHAT5ES64</softwareLabel>
        <state>NORMAL</state>
        <machineStatus name="vmwareToolsVersionStatus">
            <value>NEED_UPGRADE</value>
        </machineStatus>
        <machineStatus name="vmwareToolsRunningStatus">
            <value>RUNNING</value>
        </machineStatus>
        <machineStatus name="vmwareToolsApiVersion">
            <value>9221</value>
        </machineStatus>
    </server>
</ServersWithBackup>
"""  # NOQA


class TestServer:

    def test_members(self):
        servers = ServerList(xml=XMLSTR)
        server = servers[0]

        assert isinstance(server, Server)
        assert server.id == "63e5a7ab-a3ae-4ce3-82d5-c77685290976"
        assert server.location == "NA5"
        assert server.name == "Reporting Server"
        assert server.description == "Software Reporting Server Engine"
        assert server.os.id == "WIN2012S64"
        assert server.os.display_name == "WIN2012S/64"
        assert server.os.type == "WINDOWS"
        assert server.cpu_count == 4
        assert server.memory_mb == 8192
        assert len(server.disks) == 1
        assert server.disks[0].id == "cc77c436-314a-4c06-9a5d-e2aa4391fb8a"
        assert server.disks[0].scsi_id == 0
        assert server.disks[0].size_gb == 50
        assert server.disks[0].speed == "STANDARD"
        assert server.disks[0].state == "NORMAL"
        assert len(server.software_labels) == 0
        assert server.source_image_id == "4787337e-0f31-11e3-b29c-001517c4643e"
        assert server.network_id == "4bb558f2-506f-11e3-b29c-001517c4643e"
        assert server.machine_name == "10-192-158-11"
        assert server.private_ip == "10.192.158.11"
        assert server.public_ip == "162.216.171.60"
        assert server.created == "2014-07-11T03:48:17.000Z"
        assert server.is_deployed is True
        assert server.is_started is True
        assert server.state == "NORMAL"
        assert len(server.machine_status) == 3
        assert server.machine_status[0].name == "vmwareToolsVersionStatus"
        assert server.machine_status[0].value == "NEED_UPGRADE"
        assert server.backup.asset_id == "5c1956d9-4e30-4b74-9fa1-10a0f272f08e"
        assert server.backup.state == "NORMAL"
        assert server.backup.service_plan == "Advanced"
        assert server.status.action == "START_SERVER"

        assert servers[1].backup.asset_id is None
        assert servers[1].software_labels[0] == "REDHAT5ES64"


class TestServerList:

    def test_items(self):
        servers = ServerList(xml=XMLSTR)

        assert isinstance(servers, ServerList)
        assert len(servers) == 2

        for server in servers:
            assert isinstance(server, Server)
