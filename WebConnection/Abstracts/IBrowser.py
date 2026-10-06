from abc import ABC,abstractmethod

class IBrowser(ABC):
    @abstractmethod
    async def createBrowser()->IBrowser:pass

    @abstractmethod
    async def closeBrowser(): pass