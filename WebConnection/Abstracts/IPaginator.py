from __future__ import annotations

from abc import ABC, abstractmethod


class IPaginator(ABC):
    @abstractmethod
    def next_link(self, page_number: int, current_link: str) -> str | None:
        """Devolve o link da próxima página, ou None quando acabarem as páginas."""
