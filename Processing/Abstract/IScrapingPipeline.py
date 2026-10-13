from __future__ import annotations

from abc import ABC, abstractmethod


class IScrapingPipeline(ABC):
    @abstractmethod
    async def run(self) -> None:
        """Executa o pipeline do início ao fim."""
