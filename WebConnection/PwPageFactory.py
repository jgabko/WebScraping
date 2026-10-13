from __future__ import annotations

from WebConnection.Abstracts.ABSFactoryPage import ABSFactoryPage
from WebConnection.Abstracts.IPage import IPage
from WebConnection.PWPage import PWPage


class PWPageFactory(ABSFactoryPage):
    async def create_page(self) -> IPage:
        page = PWPage(self.browser)
        await page.create_page()
        return page
