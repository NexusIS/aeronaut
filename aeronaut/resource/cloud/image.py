from aeronaut.resource.cloud.resource import Resource, ResourceList


class AdditionalDisk(Resource):

    def _root_(self):
        return "additionalDisk"

    def _members_(self):
        return {
            "id": {
                "xpath": "./*[local-name()='id']"},

            "scsi_id": {
                "xpath": "./*[local-name()='scsiId']",
                "type": int},

            "size_gb": {
                "xpath": "./*[local-name()='diskSizeGb']",
                "type": int},

            "state": {
                "xpath": "./*[local-name()='state']"},
        }


class AdditionalDiskList(ResourceList):

    def _root_(self):
        return "ServerImageWithState"

    def _items_(self):
        return {
            "xpath": "./*[local-name()='additionalDisk']",
            "type": AdditionalDisk
        }


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
        return [
            "image",
            "ServerImageWithState"
        ]

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
                "xpath": "./@*[local-name()='type']"}
        }


class ImageSourceArtifact(Resource):

    def _root_(self):
        return "artifact"

    def _members_(self):
        return {
            "date": {
                "xpath": "./@*[local-name()='date']"},

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


class MachineStatus(Resource):

    def _root_(self):
        return "machineStatus"

    def _members_(self):
        return {
            "name": {
                "xpath": "./@*[local-name()='name']"},

            "value": {
                "xpath": "./*[local-name()='value']",
                "type": "auto"}
        }


class MachineStatusList(ResourceList):

    def _root_(self):
        return "ServerImageWithState"

    def _items_(self):
        return {
            "xpath": "./*[local-name()='machineStatus']",
            "type": MachineStatus
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


class ServerImage(Image):

    def _root_(self):
        return "ServerImageWithState"

    def _members_(self):
        base = super(ServerImage, self)._members_()

        override = {
            "deployed_time": {
                "xpath": "./*[local-name()='deployedTime']"},

            "disks": {
                "xpath": ".",
                "type": AdditionalDiskList},

            "id": {
                "xpath": "./*[local-name()='id']"},

            "location": {
                "xpath": "./*[local-name()='location']"},

            "os": {
                "xpath": "./*[local-name()='operatingSystem']",
                "type": ServerImageOperatingSystem},

            "os_storage_gb": {
                "xpath": "./*[local-name()='osStorageGb']",
                "type": int},

            "machine_status": {
                "xpath": ".",
                "type": MachineStatusList},

            "status": {
                "xpath": "./*[local-name()='status']",
                "type": ServerImageStatus}
        }

        # NOTE: The order of dictionaries below is important
        return dict(base.items() + override.items())


class ServerImageOperatingSystem(OperatingSystem):

    def _members_(self):
        return {
            "name": {
                "xpath": "./*[local-name()='displayName']"},

            "type": {
                "xpath": "./*[local-name()='type']"},
        }


class ServerImageStatus(Resource):

    def _root_(self):
        return "status"

    def _members_(self):
        return {
            "action": {
                "xpath": "./action"},

            "failure_reason": {
                "xpath": "./failureReason"},

            "request_time": {
                "xpath": "./requestTime"},

            "steps": {
                "xpath": ".",
                "type": ServerImageStatusStepsList},

            "update_time": {
                "xpath": "./updateTime"},

            "username": {
                "xpath": "./userName"}
        }


class ServerImageStatusStep(Resource):

    def _root_(self):
        return "step"

    def _members_(self):
        return {
            "name": {
                "xpath": "./name"},

            "number": {
                "xpath": "./number",
                "type": int},

            "percent_complete": {
                "xpath": "./percentComplete",
                "type": int}
        }


class ServerImageStatusStepsList(ResourceList):

    def _root_(self):
        return "status"

    def _items_(self):
        return {
            "xpath": "./*[local-name()='step']",
            "type": ServerImageStatusStep
        }


class SoftwareLabelList(ResourceList):

    def _root_(self):
        return [
            "image",
            "ServerImageWithState"
        ]

    def _items_(self):
        return {
            "xpath": "./*[local-name()='softwareLabel']"
        }
