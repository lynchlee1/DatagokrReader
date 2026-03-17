from __future__ import annotations

from typing import Any

from .base_reader import get_datagokr_document

"""
Read https://www.data.go.kr/data/15059592/openapi.do
"""

def get_BondBasiInfo(
    serviceKey: str,
    basDt: str,
    isinCd: str,
    timeout_seconds: float = 60.0,
) -> Any | None:
    """ 채권 기초정보 다운로드. """
    if not basDt or not isinCd:
        return None

    service_url = "1160100/service/GetBondIssuInfoService/getBondBasiInfo"
    params: dict[str, Any] = {
        "serviceKey": serviceKey,
        "basDt": basDt,
        "isinCd": isinCd,
    }

    return get_datagokr_document(
        serviceUrl=service_url,
        params=params,
        timeout_seconds=timeout_seconds
    )


def parse_bond_basi_info(
    serviceKey: str,
    basDt: str,
    isinCd: str,
    timeout_seconds: float = 60.0,
) -> list[dict[str, Any]] | None:
    """ Parse get_BondBasiInfo results. """
    raw = get_BondBasiInfo(
        serviceKey=serviceKey,
        basDt=basDt,
        isinCd=isinCd,
        timeout_seconds=timeout_seconds,
    )
    if raw is None:
        return None

    try:
        body = raw["response"]["body"]
        items_obj = body.get("items")
    except Exception:
        return None

    def extract_items(items: Any) -> list[dict[str, Any]]:
        if items is None:
            return []
        if isinstance(items, dict) and "item" in items:
            inner = items.get("item")
            if inner is None:
                return []
            if isinstance(inner, list):
                return [i for i in inner if isinstance(i, dict)]
            return [inner] if isinstance(inner, dict) else []
        if isinstance(items, list):
            return [i for i in items if isinstance(i, dict)]
        return [items] if isinstance(items, dict) else []

    items = extract_items(items_obj)
    if not items:
        return []

    out: list[dict[str, Any]] = []
    for it in items:
        out.append(
            {
                "발행잔액": it.get("bondBal", ""),
            }
        )

    return out

