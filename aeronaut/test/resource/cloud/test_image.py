from aeronaut.resource.cloud.image import Image, ImageList


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
