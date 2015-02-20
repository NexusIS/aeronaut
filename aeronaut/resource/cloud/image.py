from aeronaut.resource.cloud.resource import Resource, ResourceList


class Disk(Resource):

    def _root_(self):
        return "disk"

    def _members_(self):
        return {
            "id": {
                "xpath": "./@*[local-name()='id']"},

            "scsi_id": {
                "xpath": "./@*[local-name()='scsiId']",
                "type": int},

            "size_gb": {
                "xpath": "./@*[local-name()='sizeGb']",
                "type": int},

            "speed": {
                "xpath": "./@*[local-name()='speed']"},

            "state": {
                "xpath": "./@*[local-name()='state']"},
        }


class DiskList(ResourceList):

    def _root_(self):
        return 'image'

    def _items_(self):
        return {
            "xpath": "./*[local-name()='disk']",
            "type": Disk
        }


class Image(Resource):

    def _root_(self):
        return "image"

    def _members_(self):
        return {
            "cpu_count": {
                "xpath": "./*[local-name()='cpuCount']",
                "type": int},

            "created": {
                "xpath": "./*[local-name()='created']"},

            "description": {
                "xpath": "./*[local-name()='description']"},

            "disks": {
                "xpath": ".",
                "type": DiskList},

            "id": {
                "xpath": "./@*[local-name()='id']"},

            "location": {
                "xpath": "./@*[local-name()='location']"},

            "memory_mb": {
                "xpath": "./*[local-name()='memoryMb']",
                "type": int},

            "name": {
                "xpath": "./*[local-name()='name']"},

            "os": {
                "xpath": "./*[local-name()='operatingSystem']",
                "type": OperatingSystem},

            "software_labels": {
                "xpath": ".",
                "type": SoftwareLabelList},

            "source": {
                "xpath": "./*[local-name()='source']",
                "type": ImageSource},

            "state": {
                "xpath": "./*[local-name()='state']"}
        }


class ImageList(ResourceList):

    def _root_(self):
        return 'ImagesWithDiskSpeed'

    def _items_(self):
        return {
            "xpath": "./*[local-name()='image']",
            "type": Image
        }


class ImageNameExists(Resource):

    def _root_(self):
        return "Exists"

    def _members_(self):
        return {
            "is_true": {
                "xpath": ".",
                "type": bool}
        }


class ImageSource(Resource):

    def _root_(self):
        return "source"

    def _members_(self):
        return {
            "artifacts": {
                "xpath": ".",
                "type": ImageSourceArtifactList},

            "type": {
                "xpath": "./@*[local-name()='type']"},
        }


class ImageSourceArtifact(Resource):

    def _root_(self):
        return "artifact"

    def _members_(self):
        return {
            "type": {
                "xpath": "./@*[local-name()='type']"},

            "value": {
                "xpath": "./@*[local-name()='value']"}
        }


class ImageSourceArtifactList(ResourceList):

    def _root_(self):
        return 'source'

    def _items_(self):
        return {
            "xpath": "./*[local-name()='artifact']",
            "type": ImageSourceArtifact
        }


class OperatingSystem(Resource):

    def _root_(self):
        return "operatingSystem"

    def _members_(self):
        return {
            "id": {
                "xpath": "./@*[local-name()='id']"},

            "name": {
                "xpath": "./@*[local-name()='displayName']"},

            "type": {
                "xpath": "./@*[local-name()='type']"},
        }


class SoftwareLabelList(ResourceList):

    def _root_(self):
        return 'image'

    def _items_(self):
        return {
            "xpath": "./*[local-name()='softwareLabel']"
        }
