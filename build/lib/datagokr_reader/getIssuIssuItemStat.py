from __future__ import annotations
from typing import Any
from .base_reader import get_datagokr_document, normalize_name


"""
Read https://www.data.go.kr/data/15043421/openapi.do
"""


def get_IssuIssuItemStat(
    serviceKey: str,
    bondIsurNm: str,
    timeout_seconds: float = 60.0,
) -> Any | None:
    """ 발행인에 따른 채권 조회. """
    service_url = "1160100/service/GetBondTradInfoService/getIssuIssuItemStat"

    params: dict[str, Any] = {
        "serviceKey": serviceKey,
        "bondIsurNm": bondIsurNm
    }
    return get_datagokr_document(
        serviceUrl=service_url,
        params=params,
        timeout_seconds=timeout_seconds
    )


def parse_issu_issu_item_stat(
    serviceKey: str,
    bondIsurNm: str,
    bondNm: str,
    timeout_seconds: float = 60.0,
) -> dict[str, Any] | None:
    """ Parse get_IssuIssuItemStat results. """
    raw = get_IssuIssuItemStat(
        serviceKey=serviceKey,
        bondIsurNm=bondIsurNm,
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
        return None
    for it in items:
        normalized_isinCdNm = normalize_name(it.get("isinCdNm"))
        normalized_bondNm = normalize_name(bondNm)
        if normalized_isinCdNm == normalized_bondNm:
            result = {
                "기준일자": it.get("basDt", ""),
                "법인등록번호": it.get("crno", ""),
                "isinCd": it.get("isinCd", ""),

                "만기일": it.get("bondExprDt", ""), # 상환된 경우 상환일
                "발행일": it.get("bondIssuDt", ""),
                "최초발행권면": it.get("bondIssuAmt", ""),

                "isinCdNm": it.get("isinCdNm", ""),
                "최초납입금액": it.get("bondPymtAmt", ""),
            }
            return result
    return None
