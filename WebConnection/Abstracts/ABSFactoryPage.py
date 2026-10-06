from abc import ABC,abstractmethod
from WebConnection.Abstracts.IPage import IPage 

class ABSFactoryPage(ABC):
    @abstractmethod
    async def create_page()->IPage:pass