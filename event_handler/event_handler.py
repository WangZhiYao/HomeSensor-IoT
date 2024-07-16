from abc import ABC, abstractmethod

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class EventHandler(ABC):

    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    @abstractmethod
    async def handle_event(self, event):
        pass
