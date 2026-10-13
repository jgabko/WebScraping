from WebConnection.Abstracts.IPage import IPage
from WebConnection.Abstracts.IBrowser import IBrowser
from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Playwright,
)

class PWPage(IPage):
    def __init__(self,browser:IBrowser):
        self._browser=browser
        self.page=None

    async def create_page(self):
        page = await self._browser.new_page()
        self.page=page


    async def goto(self,link):
        await self.page.goto(link)

    
    async def content(self):
        return await self.page.content()

    
    async def closepage(self):
        await self.page.close()