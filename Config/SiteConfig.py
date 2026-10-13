from __future__ import annotations

from dataclasses import dataclass

from Processing.Abstract.ABSDataCollection import ABSDataCollection
from Processing.Abstract.IParse import IParse
from WebConnection.Abstracts.IPaginator import IPaginator


@dataclass(frozen=True)
class SiteConfig:
    site_name: str
    collector_cls: type[ABSDataCollection]
    parser_cls: type[IParse]
    link_exp: str
    paginator: IPaginator
