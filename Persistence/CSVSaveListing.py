from __future__ import annotations

import asyncio
import csv
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from Persistence.Abstract.ISave import ISave


class CSVSaveListing(ISave):
    """Grava anúncios em CSV, acrescentando linhas a cada chamada de save().

    O cabeçalho é escrito uma vez (a partir de `fieldnames` ou das chaves do primeiro
    lote). Se o arquivo já existir, reaproveita o cabeçalho dele.
    O encoding padrão (utf-8-sig) abre com acentos corretos no Excel.
    """

    def __init__(
        self,
        path: str | Path,
        fieldnames: Sequence[str] | None = None,
        encoding: str = "utf-8-sig",
    ) -> None:
        self._path: Path = Path(path)
        self._fieldnames: list[str] | None = list(fieldnames) if fieldnames else None
        self._encoding: str = encoding

    async def save(self, data: list[dict[str, Any]]) -> None:
        if not data:
            return
        await asyncio.to_thread(self._write_rows, data)

    def _read_header(self) -> list[str]:
        with self._path.open("r", newline="", encoding=self._encoding) as f:
            return next(csv.reader(f), [])

    def _write_rows(self, data: list[dict[str, Any]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        exists = self._path.exists() and self._path.stat().st_size > 0
        if self._fieldnames is None:
            self._fieldnames = self._read_header() if exists else list(data[0].keys())
        with self._path.open("a", newline="", encoding=self._encoding) as f:
            writer = csv.DictWriter(f, fieldnames=self._fieldnames, extrasaction="ignore")
            if not exists:
                writer.writeheader()
            writer.writerows(data)
