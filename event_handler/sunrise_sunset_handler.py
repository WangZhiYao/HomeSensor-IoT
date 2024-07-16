import logging
from datetime import datetime, timedelta

from database import find_sensor_by_id, find_devices_by_location
from device.factory import PlugFactory
from event_handler.event_handler import EventHandler
from model.device import DeviceType, Device
from model.event import EventType, Event


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
            logging.warning(f"Sensor not found for event {event}")
            return

        devices = await find_devices_by_location(sensor.location)
        logging.info(f"Found {len(devices)} devices for location {sensor.location}")

        for device in devices:
            if switch_on:
                self._schedule_device_action(device, event.timestamp, switch_on)
            else:
                await self._process_device(device, switch_on)

    def _schedule_device_action(self, device: Device, timestamp: int, switch_on: bool):
        """Schedules a device action with a delay.

        Args:
            device (Device): The device to schedule the action for.
            timestamp (int): The event timestamp.
            switch_on (bool): True to switch the device on, False to switch off.
        """
        self.scheduler.add_job(
            self._process_device,
            trigger="date",
            kwargs={"device": device, "switch_on": switch_on},
            id=f"sunrise_{device.id}",
            run_date=datetime.fromtimestamp(timestamp) + timedelta(minutes=30, hours=2)
        )

    async def _process_device(self, device: Device, switch_on: bool):
        """Processes a device by switching it on or off.

        Args:
            device (Device): The device to process.
            switch_on (bool): True to switch the device on, False to switch off.
        """
        logging.info(f"Processing device {device}")
        if device.type == DeviceType.PLUG:
            await self._process_plug(device, switch_on)
        else:
            logging.warning(f"Unsupported device type: {device.type}")

    async def _process_plug(self, device: Device, switch_on: bool):
        """Processes a plug device.

        Args:
            device (Device): The plug device to process.
            switch_on (bool): True to switch the plug on, False to switch off.
        """
        plug = PlugFactory.generate_plug(device)
        logging.info(f"Generated plug {plug}")
        if switch_on:
            if plug.is_switch_on():
                logging.info(f"Plug {plug} already switched on")
                return
            plug.toggle(True)
        else:
            if not plug.is_switch_on():
                logging.info(f"Plug {plug} already switched off")
                return
            plug.toggle(False)
