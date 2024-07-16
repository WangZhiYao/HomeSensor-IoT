from enum import StrEnum

from pydantic import BaseModel


class EventType(StrEnum):
    SUNRISE = 'sunrise'
    SUNSET = 'sunset'


class Event(BaseModel):
    type: EventType
    sensor_id: str
    timestamp: int
