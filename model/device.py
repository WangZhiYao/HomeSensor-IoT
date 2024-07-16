from enum import StrEnum
from typing import Dict, Any

from beanie import Document, Indexed

from model.location import Location


class DeviceType(StrEnum):
    PLUG = 'plug'


class Device(Document):
    type: DeviceType
    model: str
    host: str
    token: str
    did: Indexed(str, unique=True)
    location: Location
    config: Dict[str, Any]

    class Settings:
        name = "device"
