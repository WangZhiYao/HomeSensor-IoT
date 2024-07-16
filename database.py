import logging

from beanie import init_beanie
from beanie.operators import Eq
from motor.motor_asyncio import AsyncIOMotorClient

from model.device import Device
from model.sensor import Sensor
from setting import settings

mongo_client = AsyncIOMotorClient(settings.mongo_url)


async def init_database():
    logging.info("Initializing Database")
    await init_beanie(
        database=mongo_client.get_default_database(),
        document_models=[Device, Sensor]
    )
    logging.info("Database initialized successfully.")


async def find_sensor_by_id(sensor_id):
    logging.info(f"Finding sensor by id: {sensor_id}")
    sensor = await Sensor.find_one(Eq(Sensor.sensor_id, sensor_id))
    return sensor


async def find_devices_by_location(location):
    logging.info(f"Finding device by location: {location}")
    devices = await Device.find(Eq(Device.location, location)).to_list()
    return devices
