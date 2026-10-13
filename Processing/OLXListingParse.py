from __future__ import annotations
import json
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Iterator, Optional
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

class ListingParser:

    """Recebe o HTML de uma página de listagem da OLX e extrai os anúncios."""

    @dataclass
    class Anuncio:
        list_id: str
        url: str
        titulo: str = ""
        categoria: str = ""
        tipo: str = ""
        municipio: str = ""
        profissional: Optional[bool] = None
        anunciante: str = ""
        publicado_em: str = ""


    _PUSH_RE = re.compile(r"self\.__next_f\.push\(\[1,(\".*?\")\]\)</script>", re.S)

    # -------- JSON embutido (preferencial)
    def _flight_payload(self, html: str) -> str:
        """Concatena e decodifica os chunks do RSC (self.__next_f.push)."""
        parts = []
        for m in self._PUSH_RE.finditer(html):
            try:
                parts.append(json.loads(m.group(1)))
            except json.JSONDecodeError:
                continue
        return "".join(parts)

    @staticmethod
    def _extract_json_value(text: str, key: str) -> Optional[object]:
        """Extrai o valor JSON (array/objeto) que segue `"key":` balanceando colchetes."""
        idx = text.find(f'"{key}":')
        if idx == -1:
            return None
        start = idx + len(key) + 3
        while start < len(text) and text[start] in " \n":
            start += 1
        opener = text[start]
        if opener not in "[{":
            return None
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
                    return json.loads(text[start:i + 1])
        return None

    @staticmethod
    def _props(ad: dict) -> dict:
        return {p["name"]: p["value"] for p in ad.get("properties", [])}

    def _from_json_ad(self, ad: dict) -> Anuncio:
        p = self._props(ad)
        loc = ad.get("locationDetails") or {}
        imgs = ad.get("images") or []
        ts = ad.get("date")
        return Anuncio(
            list_id=str(ad.get("listId", "")),
            url=ad.get("url", ""),
            titulo=ad.get("subject", ""),
            categoria=ad.get("category", ""),
            tipo=p.get("real_estate_type", ""),
            municipio=loc.get("municipality", ""),
            profissional=ad.get("professionalAd"),
            anunciante=(ad.get("olxPay") or {}).get("transactionalSellerName", ""),
            publicado_em=datetime.fromtimestamp(ts).isoformat() if ts else ""
        )

    def _parse_json(self, html: str) -> tuple[list[Anuncio], Optional[PageInfo]]:
        flight = self._flight_payload(html)
        ads_raw = self._extract_json_value(flight, "ads")
        if not isinstance(ads_raw, list):
            return [], None

        # ignora slots de publicidade ({"advertisingId": ...})
        anuncios = [self._from_json_ad(a) for a in ads_raw if "listId" in a]

        def _num(key: str, default: int) -> int:
            m = re.search(rf'"{key}":(\d+)', flight)
            return int(m.group(1)) if m else default

        info = PageInfo(
            page=_num("pageIndex", 1),
            page_size=_num("pageSize", 50),
            total_ads=_num("totalOfAds", len(anuncios)),
        )
        return anuncios, info

    # -------- HTML (fallback)
    @staticmethod
    def _txt(node) -> str:
        return node.get_text(" ", strip=True) if node else ""

    def _parse_html(self, html: str) -> list[Anuncio]:
        soup = BeautifulSoup(html, "html.parser")
        out = []
        for card in soup.select("section.olx-adcard"):
            link = card.select_one("a[data-testid=adcard-link]")
            if not link:
                continue
            url = link.get("href", "")
            m = re.search(r"-(\d+)$", url)
            a = Anuncio(
                list_id=m.group(1) if m else "",
                url=url,
                titulo=link.get("title", ""),
                preco=self._txt(card.select_one(".olx-adcard__price")),
                preco_antigo=self._txt(card.select_one(".olx-adcard__old-price")),
            )
            loc = self._txt(card.select_one(".olx-adcard__location"))
            if "," in loc:
                a.municipio, a.bairro = [s.strip() for s in loc.split(",", 1)]
            else:
                a.municipio = loc
            for d in card.select(".olx-adcard__detail"):
                label = d.get("aria-label", "").lower()
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
            a.imagem = img.get("src", "") if img else ""
            a.profissional = None
            out.append(a)
        return out

    def _total_from_html(self, html: str) -> Optional[PageInfo]:
        soup = BeautifulSoup(html, "html.parser")
        t = soup.select_one("#total-of-ads p")
        if not t:
            return None
        m = re.search(r"(\d+)\s*-\s*(\d+)\s+de\s+([\d.]+)", t.get_text())
        if not m:
            return None
        ini, fim, total = int(m.group(1)), int(m.group(2)), int(m.group(3).replace(".", ""))
        return PageInfo(page=1, page_size=max(fim - ini + 1, 1), total_ads=total)

    # -------- API pública
    def parse(self, html: str) -> tuple[list[Anuncio], Optional[PageInfo]]:
        try:
            anuncios, info = self._parse_json(html)
            if anuncios:
                return anuncios, info
        except Exception:
            pass  # cai no fallback
        return self._parse_html(html), self._total_from_html(html)