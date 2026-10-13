from __future__ import annotations

from Config.SiteConfig import SiteConfig
from Processing.OLXListingParse import OLXListingParse
from Processing.OlxListingDataCollector import OlxListingDataCollector
from WebConnection.QueryParamPaginator import QueryParamPaginator

SITE_CONFIGS: list[SiteConfig] = [
    SiteConfig(
        site_name="olx",
        collector_cls=OlxListingDataCollector,
        parser_cls=OLXListingParse,
        # TODO: troque pela URL da busca que você quer coletar.
        link_exp="https://www.olx.com.br/imoveis/venda/estado-pr",
        # TODO: confirme no navegador se a OLX pagina com "?o=2". Se não, ajuste o param.
        paginator=QueryParamPaginator(max_pages=5, param="o"),
    ),
    # Baggio e Zap entram aqui na Etapa 3.
]
