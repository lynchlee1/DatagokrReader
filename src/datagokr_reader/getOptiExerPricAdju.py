from __future__ import annotations

from typing import Any

from .base_reader import get_datagokr_document


def get_OptiExerPricAdju(
    serviceKey: str,
    crno: str,
    timeout_seconds: float = 60.0,
    numOfRows: int = 100,
    resultType: str = "json",
) -> Any | None:
    """ 행사가 변동내역 및 현재 행사가 다운로드. """
    service_url = "1160100/service/GetBondRedeInfoService/getOptiExerPricAdju"
    if not crno:
        raise ValueError("crno가 없습니다.")

    params: dict[str, Any] = {
        "serviceKey": serviceKey,
        "crno": crno,
    }

    return get_datagokr_document(
        serviceUrl=service_url,
        params=params,
        timeout_seconds=timeout_seconds,
        numOfRows=numOfRows,
        resultType=resultType,
    )


def parse_opti_exer_pric_adju(
    serviceKey: str,
    crno: str,
    timeout_seconds: float = 60.0,
    raw: Any | None = None,
    isinCdKey: str | None = None,
) -> list[dict[str, Any]] | None:
    """ Parse get_OptiExerPricAdju results. """
    if raw is None:
        raw = get_OptiExerPricAdju(
            serviceKey=serviceKey,
            crno=crno,
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
    # "trgtStckIsinCd": it.get("trgtStckIsinCd"),       # 대상 주식의 ISIN 종목번호, 현재 프로젝트에서 사용하지 않음(추후 복원 가능하도록 주석 처리)
    # "trgtStckIsinCdNm": it.get("trgtStckIsinCdNm"),   # 대상 주식의 ISIN 종목명, 현재 프로젝트에서 사용하지 않음(추후 복원 가능하도록 주석 처리)
    for it in items:
        isin = it.get("isinCd")
        if not isin:
            continue
        if isinCdKey and isin != isinCdKey:
            continue
        out.append(
            {
                "isinCd": isin,
                "basDt": it.get("basDt"),
                "crno": it.get("crno"),
                "isinCdNm": it.get("isinCdNm"),
                "scrsIsurNm": it.get("scrsIsurNm"),
                "optnExertPrc": it.get("optnExertPrc"),
                "rgtExertPricAdjDt": it.get("rgtExertPricAdjDt"),
                "rgtBchgExertPrc": it.get("rgtBchgExertPrc"),
                "rgtAchgExertPrc": it.get("rgtAchgExertPrc"),
            }
        )

    # items 에 "rgtExertPricAdjDt": "00010101" 하나만 있으면 items 를 None 으로 처리
    out = [x for x in out if (x.get("rgtExertPricAdjDt") != "00010101")]
    return out

