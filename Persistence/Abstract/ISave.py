from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ISave(ABC):
    @abstractmethod
    async def save(self, data: list[dict[str, Any]]) -> None:
        """Persiste uma lista de anúncios já parseados."""
