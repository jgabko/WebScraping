from __future__ import annotations

import json
import re
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from Processing.Abstract.IParse import IParse


@dataclass
class Anuncio:
    list_id: str
    url: str
    titulo: str = ""
    categoria: str = ""
    tipo: str = ""
    preco: str = ""
    preco_antigo: str = ""
    municipio: str = ""
    bairro: str = ""
    area_m2: str = ""
    quartos: str = ""
    banheiros: str = ""
    vagas: str = ""
    condominio: str = ""
    iptu: str = ""
    imagem: str = ""
    profissional: bool | None = None
    anunciante: str = ""
    publicado_em: str = ""


@dataclass
class PageInfo:
    page: int
    page_size: int
    total_ads: int


class OLXListingParse(IParse):
    """Recebe o HTML de uma página de listagem da OLX e extrai os anúncios."""

    _PUSH_RE = re.compile(r'self\.__next_f\.push\(\[1,(".*?")\]\)</script>', re.S)

    # ------------------------------------------------------------------
    # JSON embutido (preferencial)
    # ------------------------------------------------------------------
    def _flight_payload(self, html: str) -> str:
        """Concatena e decodifica os chunks do RSC (self.__next_f.push)."""
        parts: list[str] = []
        for m in self._PUSH_RE.finditer(html):
            try:
                parts.append(json.loads(m.group(1)))
            except json.JSONDecodeError:
                continue
        return "".join(parts)

    @staticmethod
    def _read_balanced(text: str, start: int) -> Any | None:
        """Lê o array/objeto JSON que começa em `start`, balanceando colchetes."""
        if start >= len(text) or text[start] not in "[{":
            return None
        opener = text[start]
        closer = "]" if opener == "[" else "}"
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            c = text[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
                continue
            if c == '"':
                in_str = True
            elif c == opener:
                depth += 1
            elif c == closer:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        return None
        return None

    @classmethod
    def _iter_json_values(cls, text: str, key: str) -> Iterator[Any]:
        """Itera sobre TODOS os valores JSON que seguem `"key":` (a chave pode repetir)."""
        needle = f'"{key}":'
        pos = text.find(needle)
        while pos != -1:
            start = pos + len(needle)
            while start < len(text) and text[start] in " \n":
                start += 1
            value = cls._read_balanced(text, start)
            if value is not None:
                yield value
            pos = text.find(needle, pos + len(needle))

    @staticmethod
    def _props(ad: dict[str, Any]) -> dict[str, str]:
        return {
            str(p["name"]): str(p.get("value", ""))
            for p in (ad.get("properties") or [])
            if isinstance(p, dict) and "name" in p
        }

    @staticmethod
    def _first_image(ad: dict[str, Any]) -> str:
        thumb = ad.get("thumbnail")
        if isinstance(thumb, str) and thumb:
            return thumb
        imgs = ad.get("images") or []
        if imgs and isinstance(imgs[0], dict):
            return str(imgs[0].get("original") or imgs[0].get("url") or "")
        return ""

    @staticmethod
    def _iso_date(ts: Any) -> str:
        if not isinstance(ts, (int, float)) or ts <= 0:
            return ""
        if ts > 1e11:  # veio em milissegundos
            ts = ts / 1000
        return datetime.fromtimestamp(ts).isoformat()

    def _from_json_ad(self, ad: dict[str, Any]) -> Anuncio:
        p = self._props(ad)
        loc: dict[str, Any] = ad.get("locationDetails") or {}
        pay: dict[str, Any] = ad.get("olxPay") or {}
        # Chaves marcadas com (*) não foram confirmadas contra um HTML real da OLX:
        # se vierem vazias, confira o nome da chave no JSON da página.
        return Anuncio(
            list_id=str(ad.get("listId", "")),
            url=str(ad.get("url", "")),
            titulo=str(ad.get("subject", "")),
            categoria=str(ad.get("category", "")),
            tipo=p.get("real_estate_type", ""),
            preco=str(ad.get("price") or ""),                # (*)
            preco_antigo=str(ad.get("oldPrice") or ""),      # (*)
            municipio=str(loc.get("municipality", "")),
            bairro=str(loc.get("neighbourhood", "")),        # (*)
            area_m2=p.get("size", ""),                       # (*)
            quartos=p.get("rooms", ""),                      # (*)
            banheiros=p.get("bathrooms", ""),                # (*)
            vagas=p.get("garage_spaces", ""),                # (*)
            condominio=p.get("condominio", ""),              # (*)
            iptu=p.get("iptu", ""),                          # (*)
            imagem=self._first_image(ad),                    # (*)
            profissional=ad.get("professionalAd"),
            anunciante=str(pay.get("transactionalSellerName", "")),
            publicado_em=self._iso_date(ad.get("date")),
        )

    def _parse_json(self, html: str) -> tuple[list[Anuncio], PageInfo | None]:
        flight = self._flight_payload(html)
        for ads_raw in self._iter_json_values(flight, "ads"):
            if not isinstance(ads_raw, list):
                continue
            # ignora slots de publicidade ({"advertisingId": ...})
            ads = [a for a in ads_raw if isinstance(a, dict) and "listId" in a]
            if not ads:
                continue

            def _num(key: str, default: int) -> int:
                m = re.search(rf'"{key}":(\d+)', flight)
                return int(m.group(1)) if m else default

            anuncios = [self._from_json_ad(a) for a in ads]
            info = PageInfo(
                page=_num("pageIndex", 1),
                page_size=_num("pageSize", 50),
                total_ads=_num("totalOfAds", len(anuncios)),
            )
            return anuncios, info
        return [], None

    # ------------------------------------------------------------------
    # HTML (fallback)
    # ------------------------------------------------------------------
    @staticmethod
    def _txt(node: Tag | None) -> str:
        return node.get_text(" ", strip=True) if node else ""

    def _parse_html(self, html: str) -> list[Anuncio]:
        soup = BeautifulSoup(html, "html.parser")
        out: list[Anuncio] = []
        for card in soup.select("section.olx-adcard"):
            link = card.select_one("a[data-testid=adcard-link]")
            if not link:
                continue
            url = str(link.get("href", ""))
            m = re.search(r"-(\d+)$", url.split("?")[0])
            a = Anuncio(
                list_id=m.group(1) if m else "",
                url=url,
                titulo=str(link.get("title", "")),
                preco=self._txt(card.select_one(".olx-adcard__price")),
                preco_antigo=self._txt(card.select_one(".olx-adcard__old-price")),
            )

            loc = self._txt(card.select_one(".olx-adcard__location"))
            if "," in loc:
                a.municipio, a.bairro = (s.strip() for s in loc.split(",", 1))
            else:
                a.municipio = loc

            for d in card.select(".olx-adcard__detail"):
                label = str(d.get("aria-label", "")).lower()
                val = self._txt(d)
                if "metros" in label:
                    a.area_m2 = val
                elif "quarto" in label:
                    a.quartos = val
                elif "banheiro" in label:
                    a.banheiros = val
                elif "vaga" in label:
                    a.vagas = val

            for info in card.select(".olx-adcard__price-info"):
                t = self._txt(info)
                if t.startswith("Condom"):
                    a.condominio = t.split("R$")[-1].strip()
                elif t.startswith("IPTU"):
                    a.iptu = t.split("R$")[-1].strip()

            img = card.select_one("picture img")
            a.imagem = str(img.get("src", "")) if img else ""
            out.append(a)
        return out

    def _total_from_html(self, html: str) -> PageInfo | None:
        soup = BeautifulSoup(html, "html.parser")
        t = soup.select_one("#total-of-ads p")
        if not t:
            return None
        m = re.search(r"(\d+)\s*-\s*(\d+)\s+de\s+([\d.]+)", t.get_text())
        if not m:
            return None
        ini, fim = int(m.group(1)), int(m.group(2))
        total = int(m.group(3).replace(".", ""))
        return PageInfo(page=1, page_size=max(fim - ini + 1, 1), total_ads=total)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def parse_with_info(self, html: str) -> tuple[list[Anuncio], PageInfo | None]:
        """Versão rica: devolve os Anuncio e o PageInfo (útil para saber quando parar)."""
        try:
            anuncios, info = self._parse_json(html)
            if anuncios:
                return anuncios, info
        except Exception:
            pass  # qualquer falha no JSON embutido cai no fallback em HTML
        return self._parse_html(html), self._total_from_html(html)

    def parse(self, html: str) -> list[dict[str, Any]]:
        """Contrato de IParse: lista de anúncios como dicts."""
        anuncios, _ = self.parse_with_info(html)
        return [asdict(a) for a in anuncios]
