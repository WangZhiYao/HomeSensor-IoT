import logging
from datetime import datetime, timedelta

from database import find_sensor_by_id, find_devices_by_location
from device.factory import PlugFactory
from event_handler.event_handler import EventHandler
from model.device import DeviceType, Device
from model.event import EventType, Event
from setting import settings


class SunriseSunsetHandler(EventHandler):
    """Handles sunrise and sunset events to control devices based on location."""

    async def handle_event(self, event: Event):
        """Handles sunrise and sunset events.

        Args:
            event (Event): The sunrise or sunset event to handle.
        """
        if event.type == EventType.SUNRISE:
            await self._handle_sunrise_sunset(event, switch_on=True)
        elif event.type == EventType.SUNSET:
            await self._handle_sunrise_sunset(event, switch_on=False)
        else:
            logging.warning(f"Unknown event type: {event.type}")

    async def _handle_sunrise_sunset(self, event: Event, switch_on: bool):
        """Handles sunrise and sunset events and processes devices accordingly.

        Args:
            event (Event): The sunrise or sunset event to handle.
            switch_on (bool): True to switch devices on, False to switch off.
        """
        sensor = await find_sensor_by_id(event.sensor_id)
        if not sensor:
            logging.warning(f"Sensor not found for event: {event}")
            return

        devices = await find_devices_by_location(sensor.location)
        logging.info(f"Found {len(devices)} devices for location: {sensor.location}")

        for device in devices:
            if switch_on:
                switch_on_delay = 0
                if settings.switch_on_delay and settings.switch_on_delay > 0:
                    switch_on_delay = settings.switch_on_delay
                self.scheduler.add_job(
                    self._process_device,
                    trigger="date",
                    kwargs={"device": device, "switch_on": switch_on},
                    id=f"sunrise_{device.id}",
                    run_date=datetime.fromtimestamp(event.timestamp) + timedelta(seconds=switch_on_delay)
                )
            else:
                switch_off_delay = 0
                if settings.switch_off_delay and settings.switch_off_delay > 0:
                    switch_off_delay = settings.switch_off_delay
                if switch_off_delay > 0:
                    self.scheduler.add_job(
                        self._process_device,
                        trigger="date",
                        kwargs={"device": device, "switch_on": switch_on},
                        id=f"sunset_{device.id}",
                        run_date=datetime.fromtimestamp(event.timestamp) + timedelta(seconds=switch_off_delay)
                    )
                else:
                    await self._process_device(device, switch_on)

    async def _process_device(self, device: Device, switch_on: bool):
        """Processes a device by switching it on or off.

        Args:
            device (Device): The device to process.
            switch_on (bool): True to switch the device on, False to switch off.
        """
        logging.info(f"Processing device: {device}")
        if device.type == DeviceType.PLUG:
            success = await self._process_plug(device, switch_on)
            logging.info(f"Process device: {device} success: {success}")
        else:
            logging.warning(f"Unsupported device type: {device.type}")

    async def _process_plug(self, device: Device, switch_on: bool) -> bool:
        """Processes a plug device.

        Args:
            device (Device): The plug device to process.
            switch_on (bool): True to switch the plug on, False to switch off.
        """
        try:
            plug = PlugFactory.generate_plug(device)
        except Exception as e:
            logging.error(f"Error on generate plug: {e}")
            return False

        logging.info(f"Generated plug: {plug}")
        if switch_on:
            if plug.is_switch_on():
                logging.info(f"Plug: {plug} already switched on")
            plug.toggle(True)
            logging.info(f"Send switch on plug: {plug.device.device_id} command")
            return True
        else:
            if not plug.is_switch_on():
                logging.info(f"Plug: {plug} already switched off")
            plug.toggle(False)
            logging.info(f"Send switch off plug: {plug.device.device_id} command")
            return True
