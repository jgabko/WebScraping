from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IParse(ABC):
    @abstractmethod
    def parse(self, html: str) -> list[dict[str, Any]]:
        """Recebe o HTML de uma página de listagem e devolve os anúncios como dicts."""
