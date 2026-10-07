from WebConnection.Abstracts import ABSFactoryPage
from WebConnection.PWPage import PWPage
from WEBConnection.PWBrowser import PWBrowser


class PWPageFactory(ABSFactoryPage):

    def __innt__(self, browser):
        self.browser = browser

    def get_browser(self):
        return self.browser

    def set_browser(self, browser):
        self.browser = browser

    async def create_page(self) -> IPage:
        return PWPage(browser)