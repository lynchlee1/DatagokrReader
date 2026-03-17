from __future__ import annotations

from typing import Any

from .base_reader import get_datagokr_document

"""
BondBasiInfo : (bondIsurNm|crno) 
-> bondBal(발행잔액) +
    "basDt": 채권의 기준일
    "crno": 기업의 법인등록번호
    "bondIsurNm": 채권의 발행사명
    "isinCdNm": 채권의 ISIN 종목명
    "bondIssuDt": 채권의 발행일
    "bondExprDt": 채권의 만기일
    "bondIssuAmt": 채권의 발행액
    "bondPymtAmt": 채권의 납입액
    "issuDptyNm": 주간사명
"""
def get_BondBasiInfo(serviceKey: str, basDt: str, bondIsurNm: str, crno: str, timeout_seconds: float = 60.0) -> Any | None:
    """ 채권 기본 정보 다운로드. """
    service_url = "1160100/service/GetBondIssuInfoService/getBondBasiInfo"
    if not bondIsurNm and not crno:
        raise ValueError("bondIsurNm 또는 crno가 없습니다.")

    params: dict[str, Any] = {
        "serviceKey": serviceKey
    }
    if basDt:
        params["basDt"] = basDt
    if bondIsurNm:
        params["bondIsurNm"] = bondIsurNm
    if crno:
        params["crno"] = crno

    return get_datagokr_document(
        serviceUrl=service_url,
        params=params,
        timeout_seconds=timeout_seconds
    )


def parse_bond_basi_info(serviceKey: str, basDt: str, bondIsurNm: str, crno: str, timeout_seconds: float = 60.0) -> dict[str, Any] | None:
    """ Parse get_BondBasiInfo results. """
    raw = get_BondBasiInfo(serviceKey=serviceKey, basDt=basDt, bondIsurNm=bondIsurNm, crno=crno, timeout_seconds=timeout_seconds)
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
        return {}

    result: dict[str, Any] = {}
    for it in items:
        isin = it.get("isinCd")
        if not isin:
            continue

        meta = result.setdefault(
            isin,
            {
                "metadata": {
                    "basDt": it.get("basDt"),
                    "crno": it.get("crno"),
                    "bondIsurNm": it.get("bondIsurNm"),
                    "isinCd": it.get("isinCd"),
                    "isinCdNm": it.get("isinCdNm"),
                    "bondIssuDt": it.get("bondIssuDt"),
                    "bondIssuAmt": it.get("bondIssuAmt"),
                    "bondExprDt": it.get("bondExprDt"),
                    "bondPymtAmt": it.get("bondPymtAmt"),
                    # "bondSrfcInrt": it.get("bondSrfcInrt"), # 표면이자율(추후 복원 가능하도록 주석 처리)
                    "issuDptyNm": it.get("issuDptyNm"),
                },
                "items": [],
            },
        )

        meta["items"].append(
            {
                "bondBal": it.get("bondBal"),
            }
        )

    return result


