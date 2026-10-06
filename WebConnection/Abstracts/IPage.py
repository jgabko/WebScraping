from abc import ABC,abstractmethod

class IPage(ABC):
    @abstractmethod
    async def goto(link:str)->IPage:pass

    @abstractmethod
    async def content(): pass

    @abstractmethod
    async def closepage(): pass