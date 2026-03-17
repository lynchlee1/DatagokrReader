from __future__ import annotations
from typing import Any
from .base_reader import get_datagokr_document


"""
Read https://www.data.go.kr/data/15059595/openapi.do
"""


def get_OptiExer(
    serviceKey: str,
    isinCd: str,
    timeout_seconds: float = 60.0,
) -> str | None:
    """ 옵션 실제 행사내역 다운로드. """
    if not isinCd:
        return None

    service_url = "1160100/service/GetBondRedeInfoService/getOptiExer"
    params: dict[str, Any] = {
        "serviceKey": serviceKey,
        "isinCd": isinCd,
    }
    return get_datagokr_document(
        serviceUrl=service_url,
        params=params,
        timeout_seconds=timeout_seconds
    )


def parse_opti_exer(
    serviceKey: str,
    isinCd: str,
    timeout_seconds: float = 60.0,
) -> list[dict[str, Any]] | None:
    """ Parse get_OptiExer results. """
    raw = get_OptiExer(
        serviceKey=serviceKey,
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
                "현재행사단가": it.get("optnExertPrc"),
                "행사일": it.get("rgtOccrBasDt"),
                "행사단가": it.get("exertPric"),
                "행사금액": it.get("exertAmt"),
            }
        )

    # items 에 "rgtOccrBasDt": "00010101" 하나만 있으면 items 를 None 으로 처리
    out = [x for x in out if (x.get("rgtOccrBasDt") != "00010101")]
    return out
