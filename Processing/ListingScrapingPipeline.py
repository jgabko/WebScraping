from __future__ import annotations

import asyncio
import logging
from typing import Any

from Persistence.Abstract.ISave import ISave
from Processing.Abstract.ABSDataCollection import ABSDataCollection
from Processing.Abstract.ILinkQueue import ILinkQueue
from Processing.Abstract.IScrapingPipeline import IScrapingPipeline
from WebConnection.Abstracts.IPaginator import IPaginator

logger = logging.getLogger(__name__)


class ListingScrapingPipeline(IScrapingPipeline):
    """Percorre as páginas de listagem de um site, salva os anúncios e guarda as falhas.

    Fluxo: coleta a página -> remove repetidos -> salva -> pede o próximo link ao paginator.
    Para quando: o paginator devolve None, uma página vem sem anúncios, ou acontecem
    `max_consecutive_failures` falhas seguidas (evita insistir num site que bloqueou).
    """

    def __init__(
        self,
        collector: ABSDataCollection,
        saver: ISave,
        failed_queue: ILinkQueue,
        paginator: IPaginator,
        source: str,
        delay_seconds: float = 1.0,
        max_consecutive_failures: int = 3,
        dedupe_key: str | None = "url",
    ) -> None:
        self.collector: ABSDataCollection = collector
        self.saver: ISave = saver
        self.failed_queue: ILinkQueue = failed_queue
        self.paginator: IPaginator = paginator
        self.source: str = source
        self.delay_seconds: float = delay_seconds
        self.max_consecutive_failures: int = max_consecutive_failures
        self.dedupe_key: str | None = dedupe_key

    def _only_new(self, items: list[dict[str, Any]], seen: set[str]) -> list[dict[str, Any]]:
        if self.dedupe_key is None:
            return items
        fresh: list[dict[str, Any]] = []
        for item in items:
            key = item.get(self.dedupe_key)
            if not key:  # sem chave não dá para deduplicar: mantém
                fresh.append(item)
                continue
            if key in seen:
                continue
            seen.add(str(key))
            fresh.append(item)
        return fresh

    async def run(self) -> None:
        link: str | None = self.collector.linkexp
        page_number = 1
        failures = 0
        total_saved = 0
        seen: set[str] = set()

        while link is not None:
            try:
                items = await self.collector.collect(link)
            except Exception as exc:
                failures += 1
                self.failed_queue.enqueue(link, self.source, f"{type(exc).__name__}: {exc}")
                logger.warning("[%s] página %d falhou (%s): %s", self.source, page_number, link, exc)
                if failures >= self.max_consecutive_failures:
                    logger.error("[%s] %d falhas seguidas; encerrando.", self.source, failures)
                    break
            else:
                failures = 0
                if not items:
                    logger.info("[%s] página %d sem anúncios; fim da listagem.", self.source, page_number)
                    break
                new_items = self._only_new(items, seen)
                if new_items:
                    await self.saver.save(new_items)
                    total_saved += len(new_items)
                logger.info(
                    "[%s] página %d: %d anúncios (%d novos)",
                    self.source, page_number, len(items), len(new_items),
                )

            link = self.paginator.next_link(page_number, link)
            page_number += 1
            if link is not None and self.delay_seconds > 0:
                await asyncio.sleep(self.delay_seconds)

        logger.info("[%s] concluído: %d anúncios salvos.", self.source, total_saved)
