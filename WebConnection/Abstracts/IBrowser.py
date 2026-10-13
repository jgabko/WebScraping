from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IBrowser(ABC):
    @abstractmethod
    async def createBrowser(self) -> IBrowser:
        """Inicia o navegador e devolve a própria instância."""

    @abstractmethod
    async def new_page(self) -> Any:
        """Abre uma nova página (objeto específico do backend, ex.: playwright Page)."""

    @abstractmethod
    async def closeBrowser(self) -> None:
        """Fecha o navegador e libera os recursos."""
