from abc import ABC,abstractmethod
from WebConnection.Abstracts.IPage import IPage 

class ABSFactoryPage(ABC):


    @abstractmethod
    def __innt__(self,browser):
        self.browser = browser

    @abstractmethod
    def get_browser(self):
        return self.browser

    @abstractmethod
    def set_browser(self, browser):
        self.browser = browser

    @abstractmethod
    async def create_page(self)->IPage:pass