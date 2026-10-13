from __future__ import annotations

from playwright.async_api import Browser, Page, Playwright, async_playwright

from WebConnection.Abstracts.IBrowser import IBrowser


class PWBrowser(IBrowser):
    def __init__(self, headless: bool = True) -> None:
        self._headless: bool = headless
        self._pw: Playwright | None = None
        self.browser: Browser | None = None

    async def createBrowser(self) -> PWBrowser:
        if self.browser is not None:
            return self
        self._pw = await async_playwright().start()
        self.browser = await self._pw.chromium.launch(headless=self._headless)
        return self

    async def new_page(self) -> Page:
        if self.browser is None:
            raise RuntimeError("Navegador não iniciado. Chame createBrowser() antes.")
        return await self.browser.new_page()

    async def closeBrowser(self) -> None:
        if self.browser is not None:
            await self.browser.close()
            self.browser = None
        if self._pw is not None:
            await self._pw.stop()
            self._pw = None
