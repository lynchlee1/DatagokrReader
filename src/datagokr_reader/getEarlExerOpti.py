from __future__ import annotations
from typing import Any
from .base_reader import get_datagokr_document


"""
Read https://www.data.go.kr/data/15059595/openapi.do
"""


def get_EarlExerOpti(
    serviceKey: str,
    basDt: str,
    isinCd: str,
    timeout_seconds: float = 60.0,
) -> Any | None:
    """ 
    옵션 행사 일정 다운로드. 콜옵션은 대부분의 경우 누락되니 주의.
    basDt가 없는 경우 수만 개에 달하기 때문에 사실상 사용 불가능.
    """
    if not basDt or not isinCd:
        return None

    service_url = "1160100/service/GetBondRedeInfoService/getEarlExerOpti"
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


def parse_earl_exer_opti(
    serviceKey: str,
    basDt: str,
    isinCd: str,
    timeout_seconds: float = 60.0,
) -> list[dict[str, Any]] | None:
    """ Parse get_EarlExerOpti results. """
    raw = get_EarlExerOpti(
        serviceKey=serviceKey,
        basDt=basDt,
        isinCd=isinCd,
        timeout_seconds=timeout_seconds
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
                "옵션분류": it.get("optnTcdNm", ""),
                "행사일정": [
                    it.get("옵션청구시작일", ""),
                    it.get("옵션청구종료일", ""),
                    it.get("지급일", ""),
                ],
            }
        )

    return out
