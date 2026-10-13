from __future__ import annotations

from abc import ABC, abstractmethod


class IPage(ABC):
    @abstractmethod
    async def create_page(self) -> None:
        """Abre a página no navegador."""

    @abstractmethod
    async def goto(self, link: str) -> IPage:
        """Navega até o link e devolve a própria página."""

    @abstractmethod
    async def content(self) -> str:
        """Devolve o HTML atual da página."""

    @abstractmethod
    async def closepage(self) -> None:
        """Fecha a página."""
