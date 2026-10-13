from __future__ import annotations

from Processing.Abstract.ILinkQueue import ILinkQueue


class InMemoryFailedLinkQueue(ILinkQueue):
    """Fila de links que falharam, só na memória (vive enquanto o processo viver)."""

    def __init__(self) -> None:
        self._pending: dict[str, dict[str, str]] = {}

    def enqueue(self, link: str, source: str, error: str) -> None:
        # Se o mesmo link falhar de novo, mantém uma entrada só (com o erro mais recente).
        self._pending[link] = {"link": link, "source": source, "error": error}

    def dequeue_pending(self) -> list[dict[str, str]]:
        return [dict(item) for item in self._pending.values()]

    def mark_resolved(self, link: str) -> None:
        self._pending.pop(link, None)
