from __future__ import annotations

from typing import Any

from .base_reader import get_datagokr_document

def get_EarlExerOpti(
    serviceKey: str,
    basDt: str | None,
    bondIsurNm: str,
    crno: str,
    timeout_seconds: float = 60.0,
) -> Any | None:
    """ 옵션 행사 일정 다운로드. 
        사모 사채는 콜옵션이 공시되지 않는 경우가 있으니 주의. 
    """
    service_url = "1160100/service/GetBondRedeInfoService/getEarlExerOpti"
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


def parse_earl_exer_opti(
    serviceKey: str,
    basDt: str | None,
    bondIsurNm: str,
    crno: str,
    timeout_seconds: float = 60.0,
    isinCdKey: str | None = None,
) -> list[dict[str, Any]] | None:
    """ Parse get_EarlExerOpti results. """
    raw = get_EarlExerOpti(serviceKey=serviceKey, basDt=basDt, bondIsurNm=bondIsurNm, crno=crno, timeout_seconds=timeout_seconds)
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

    # 아래 항목들은 it에 존재하지만, 현재 라이브러리 목적상 파싱하지 않음
    # "isinCd": it.get("isinCd"),           # ISIN 종목번호, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)
    # "basDt": it.get("basDt"),             # 채권의 기준일, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)
    # "crno": it.get("crno"),               # 기업의 법인등록번호, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)
    # "bondIsurNm": it.get("bondIsurNm"),   # 채권의 발행사명, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)
    # "isinCdNm": it.get("isinCdNm"),       # ISIN 종목명, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)

    out: list[dict[str, Any]] = []
    for it in items:
        isin = it.get("isinCd")
        if not isin:
            continue
        if isinCdKey and isin != isinCdKey:
            continue
        out.append(
            {
                "isinCd": isin,
                "type": it.get("optnTcdNm"),
                "dates": [
                    it.get("optnExertSttgDt"),
                    it.get("optnExertEdDt"),
                    it.get("clrdDt"),
                ],
            }
        )

    return out
