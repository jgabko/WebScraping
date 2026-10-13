from abc import ABC,abstractmethod

class IBrowser(ABC):
    @abstractmethod
    async def createBrowser(self):pass

    @abstractmethod
    async def closeBrowser(self): pass