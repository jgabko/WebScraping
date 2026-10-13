from __future__ import annotations

from abc import ABC, abstractmethod

from WebConnection.Abstracts.IBrowser import IBrowser
from WebConnection.Abstracts.IPage import IPage


class ABSFactoryPage(ABC):
    def __init__(self, browser: IBrowser) -> None:
        self.browser: IBrowser = browser

    def get_browser(self) -> IBrowser:
        return self.browser

    def set_browser(self, browser: IBrowser) -> None:
        self.browser = browser

    @abstractmethod
    async def create_page(self) -> IPage:
        """Cria uma página pronta para uso (já aberta no navegador)."""
