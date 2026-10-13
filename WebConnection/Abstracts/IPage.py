from abc import ABC,abstractmethod


class IPage(ABC):
    @abstractmethod
    async def create_page(self):
        pass

    @abstractmethod
    async def goto(self, link):
        pass

    @abstractmethod
    async def content(self):
        pass


    @abstractmethod
    async def closepage(self):
        pass