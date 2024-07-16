from enum import StrEnum
from typing import List

from beanie import Document, Indexed

from model.location import Location


class SensorType(StrEnum):
    THP = "thp"
    ILLUMINANCE = "illuminance"


class Sensor(Document):
    sensor_id: Indexed(str, unique=True)
    location: Location
    type: List[SensorType]

    class Settings:
        name = "sensor"
