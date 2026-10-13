from __future__ import annotations

from abc import ABC, abstractmethod


class ILinkQueue(ABC):
    @abstractmethod
    def enqueue(self, link: str, source: str, error: str) -> None:
        """Registra um link que falhou, com o site de origem e o erro."""

    @abstractmethod
    def dequeue_pending(self) -> list[dict[str, str]]:
        """Devolve os links pendentes: [{"link": ..., "source": ..., "error": ...}]."""

    @abstractmethod
    def mark_resolved(self, link: str) -> None:
        """Marca o link como resolvido (sai da fila de pendentes)."""
