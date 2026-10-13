from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from Processing.Abstract.IParse import IParse
from WebConnection.Abstracts.ABSFactoryPage import ABSFactoryPage
from WebConnection.Abstracts.IBrowser import IBrowser
from WebConnection.Abstracts.IPaginator import IPaginator


class ABSDataCollection(ABC):
    def __init__(
        self,
        browser: IBrowser,
        pagefactory: ABSFactoryPage,
        parser: IParse,
        linkexp: str,
        paginator: IPaginator,
    ) -> None:
        self.browser: IBrowser = browser
        self.pagefactory: ABSFactoryPage = pagefactory
        self.parser: IParse = parser
        self.linkexp: str = linkexp
        self.paginator: IPaginator = paginator

    @abstractmethod
    async def collectdata(self) -> list[dict[str, Any]]:
        """Percorre as páginas a partir de linkexp e devolve todos os anúncios."""
