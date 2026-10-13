from WebConnection.Abstracts.IBrowser import IBrowser
import asyncio
from playwright.async_api import Browser, Playwright,async_playwright

class PWBrowser(IBrowser):

    def __init__(self, headless: bool = True):
        self._pw: Playwright | None = None
        self.browser: Browser | None = None
        self._headless = headless

    
    async def createBrowser(self):
       self._pw = await async_playwright().start()
       self.browser = await self._pw.chromium.launch(headless=self._headless)
       return self.browser
    
        
    async def closeBrowser(self):
        if self.browser:                 
            await self.browser.close()   

        if self._playwright:             
            await self._pw.stop()