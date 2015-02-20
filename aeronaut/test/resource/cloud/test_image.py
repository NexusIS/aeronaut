from aeronaut.resource.cloud.image import Image, ImageList, ServerImage


class TestImage:

    # =======
    # HELPERS
    # =======

    @property
    def xmlstr(self):
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <image id="482f12e4-d789-4173-9411-0b74677d7cfa" location="NA5">
                <name>Image1</name>
                <description>something</description>
                <operatingSystem id="UBUNTU1264" displayName="UBUNTU12/64" type="UNIX"/>
                <cpuCount>2</cpuCount>
                <memoryMb>4096</memoryMb>
                <disk id="16cfe4e9-17ee-4b8e-aa9b-e62d6f92e771" scsiId="0" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                <disk id="b7ca7478-b8cf-11e3-b29c-001517c4643e" scsiId="1" sizeGb="300" speed="STANDARD" state="NORMAL"/>
                <disk id="fb9daec2-b8cf-11e3-b29c-001517c4643e" scsiId="2" sizeGb="10" speed="STANDARD" state="NORMAL"/>
                <softwareLabel>SAPACCEL</softwareLabel>
                <softwareLabel>MSSQL2012R2E</softwareLabel>
                <source type="CLONE">
                    <artifact type="SERVER_ID" value="b2395c7e-9a85-445d-8025"/>
                </source>
                <created>2014-07-30T00:42:45.000Z</created>
                <state>NORMAL</state>
            </image>
            """  # NOQA

    # =====
    # TESTS
    # =====

    def test_attributes(self):
        image = Image(self.xmlstr)

        assert image.id == "482f12e4-d789-4173-9411-0b74677d7cfa"
        assert image.location == "NA5"
        assert image.name == "Image1"
        assert image.description == "something"
        assert image.os.id == "UBUNTU1264"
        assert image.os.name == "UBUNTU12/64"
        assert image.os.type == "UNIX"
        assert image.cpu_count == 2
        assert image.memory_mb == 4096
        assert len(image.disks) == 3
        assert image.disks[0].id == "16cfe4e9-17ee-4b8e-aa9b-e62d6f92e771"
        assert image.disks[0].scsi_id == 0
        assert image.disks[0].size_gb == 10
        assert image.disks[0].speed == "STANDARD"
        assert image.disks[0].state == "NORMAL"
        assert image.disks.total_pages is None
        assert len(image.software_labels) == 2
        assert image.software_labels[0] == "SAPACCEL"
        assert image.software_labels[1] == "MSSQL2012R2E"
        assert image.source.type == "CLONE"
        assert len(image.source.artifacts) == 1
        assert image.source.artifacts[0].type == "SERVER_ID"
        assert image.source.artifacts[0].value == "b2395c7e-9a85-445d-8025"
        assert image.created == "2014-07-30T00:42:45.000Z"
        assert image.state == "NORMAL"


class TestImageList:

    # =======
    # HELPERS
    # =======

    @property
    def xmlstr(self):
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ImagesWithDiskSpeed pageNumber="1" pageCount="2" totalCount="5" pageSize="2">
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

    # =====
    # TESTS
    # =====

    def test_items(self):
        images = ImageList(self.xmlstr)

        assert len(images) == 2
        assert images.page_number == 1
        assert images.total_pages == 3
        assert images.page_size == 2
        assert images.total_count == 5

        for image in images:
            assert isinstance(image, Image)


class TestServerImage:

    # =======
    # HELPERS
    # =======

    @property
    def xmlstr(self):
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ServerImageWithState>
                <id>c325fe04-7711-4968-962e-c88784eb2xyz</id>
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
            """  # NOQA

    # =====
    # TESTS
    # =====

    def test_attributes(self):
        image = ServerImage(self.xmlstr)

        assert image.id == "c325fe04-7711-4968-962e-c88784eb2xyz"
        assert image.location == "NA1"
        assert image.name == "My New Customer Image"
        assert image.description == "Image for producing web servers."
        assert image.os.type == "WINDOWS"
        assert image.os.name == "WIN2008E/64"
        assert image.os_storage_gb == 50
        assert image.cpu_count == 2
        assert image.memory_mb == 4096
        assert len(image.disks) == 1
        assert image.disks[0].id == "ef49974c-87d0-400f-aa32-ee43559fdb1b"
        assert image.disks[0].scsi_id == 1
        assert image.disks[0].size_gb == 40
        assert image.disks[0].state == "NORMAL"
        assert image.disks.total_pages is None
        assert len(image.software_labels) == 2
        assert image.software_labels[0] == "SAPACCEL"
        assert image.software_labels[1] == "MSSQL2008R2E"
        assert image.source.type == "IMPORT"
        assert len(image.source.artifacts) == 4
        assert image.source.artifacts[0].type == "MF"
        assert image.source.artifacts[0].value == "MyCustomerImage.mf"
        assert image.source.artifacts[0].date == "2008-09- 29T02:49:45"
        assert image.state == "FAILED_ADD"
        assert image.deployed_time == "2012-05-25T12:59:10.110Z"
        assert len(image.machine_status) == 3
        assert image.machine_status[0].name == "vmwareToolsApiVersion"
        assert image.machine_status[0].value == 8295
        assert image.status.action == "IMAGE_IMPORT"
        assert image.status.request_time == "2012-05-25T23:10:36.000Z"
        assert image.status.username == "theUser"
        assert image.status.update_time == "2012-05-25T23:11:32.000Z"
        assert len(image.status.steps) == 1
        assert image.status.steps[0].name == "WAIT_FOR_OPERATION"
        assert image.status.steps[0].number == 3
        assert image.status.steps[0].percent_complete == 50
        assert image.status.failure_reason == "Operation timed out."
