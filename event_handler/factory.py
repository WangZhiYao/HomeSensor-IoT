import logging
from typing import Dict, Type

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from event_handler.event_handler import EventHandler
from event_handler.sunrise_sunset_handler import SunriseSunsetHandler
from model.event import EventType, Event


class EventHandlerFactory:
    """
    A factory class for managing and dispatching event handlers.
    """

    event_handlers: Dict[EventType, Type[EventHandler]] = {}

    @staticmethod
    def register_event_handler(event_type: EventType, handler: Type[EventHandler]):
        """
        Registers an event handler class for a specific event type.

        Args:
            :param event_type: The type of event to handle.
            :param handler: The event handler class.
        """
        EventHandlerFactory.event_handlers[event_type] = handler

    @staticmethod
    async def handle_event(scheduler: AsyncIOScheduler, event: Event):
        """
        Handles an event by finding and invoking the appropriate registered handler.

        Args:
            :param event:
            :param scheduler:
        """
        logging.info(f"Handling event: {event}")
        handler_class = EventHandlerFactory.event_handlers.get(event.type)
        if handler_class:
            handler = handler_class(scheduler)
            await handler.handle_event(event)
        else:
            logging.warning(f"No handler registered for event type: {event.type}")


EventHandlerFactory.register_event_handler(EventType.SUNRISE, SunriseSunsetHandler)
EventHandlerFactory.register_event_handler(EventType.SUNSET, SunriseSunsetHandler)
