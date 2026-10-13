from __future__ import annotations

from abc import ABC, abstractmethod


class IRun_scraping(ABC):
    @abstractmethod
    async def run(self, only_sites: list[str] | None = None) -> None:
        """Roda o scraping de todos os sites configurados, ou só dos nomes em only_sites."""
