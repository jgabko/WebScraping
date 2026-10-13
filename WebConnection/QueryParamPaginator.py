from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from WebConnection.Abstracts.IPaginator import IPaginator


class QueryParamPaginator(IPaginator):
    """Pagina trocando um parâmetro da query string (ex.: ?o=2, ?page=3).

    `page_number` é o número da página que acabou de ser coletada (a primeira é 1,
    normalmente o link inicial sem o parâmetro). Devolve o link da página seguinte,
    ou None quando `page_number` já atingiu `max_pages`.
    """

    def __init__(self, max_pages: int, param: str = "page") -> None:
        if max_pages < 1:
            raise ValueError("max_pages deve ser >= 1")
        self.max_pages: int = max_pages
        self.param: str = param

    def next_link(self, page_number: int, current_link: str) -> str | None:
        if page_number >= self.max_pages:
            return None
        parts = urlparse(current_link)
        query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != self.param]
        query.append((self.param, str(page_number + 1)))
        return urlunparse(parts._replace(query=urlencode(query)))
