from __future__ import annotations

from typing import Any

from Processing.Abstract.ABSDataCollection import ABSDataCollection


class OlxListingDataCollector(ABSDataCollection):
    """Coletor de páginas de LISTAGEM da OLX.

    Ponto de extensão do site: se a OLX exigir algo a mais (esperar um seletor,
    rolar a página, fechar banner de cookies), customize aqui sem mexer na base.
    """

    async def collect(self, link: str) -> list[dict[str, Any]]:
        html = await self._fetch_html(link)
        return self.parser.parse(html)
