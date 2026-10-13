from __future__ import annotations

from playwright.async_api import Page

from WebConnection.Abstracts.IBrowser import IBrowser
from WebConnection.Abstracts.IPage import IPage


class PWPage(IPage):
    def __init__(self, browser: IBrowser) -> None:
        self._browser: IBrowser = browser
        self._page: Page | None = None

    def _require_page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Página não criada. Chame create_page() antes.")
        return self._page

    async def create_page(self) -> None:
        self._page = await self._browser.new_page()

    async def goto(self, link: str) -> PWPage:
        await self._require_page().goto(link)
        return self

    async def content(self) -> str:
        return await self._require_page().content()

    async def closepage(self) -> None:
        if self._page is not None:
            await self._page.close()
            self._page = None
