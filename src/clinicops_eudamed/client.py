from __future__ import annotations

from dataclasses import dataclass

import requests

BASE = "https://ec.europa.eu/tools/eudamed/api/devices"


@dataclass
class EudamedClient:
    timeout: float = 20.0
    user_agent: str = "ClinicOps-public-research/0.1"

    def _get(self, url: str, params: dict | None = None):
        r = requests.get(
            url,
            params=params,
            timeout=self.timeout,
            headers={"User-Agent": self.user_agent},
        )
        r.raise_for_status()
        return r.json()

    def search_trade_name(
        self,
        trade_name: str,
        page: int = 0,
        page_size: int = 50,
        language: str = "en",
    ):
        return self._get(
            f"{BASE}/udiDiData",
            {
                "page": page,
                "pageSize": page_size,
                "size": page_size,
                "iso2Code": language,
                "tradeName": trade_name,
                "languageIso2Code": language,
            },
        )

    def basic_udi_detail(self, udi_di_uuid: str, language: str = "en"):
        return self._get(
            f"{BASE}/basicUdiData/udiDiData/{udi_di_uuid}",
            {"languageIso2Code": language},
        )

    def udi_di_detail(self, uuid: str, language: str = "en"):
        return self._get(
            f"{BASE}/udiDiData/{uuid}",
            {"languageIso2Code": language},
        )
