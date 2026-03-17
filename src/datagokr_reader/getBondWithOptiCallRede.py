from __future__ import annotations

from typing import Any

from .base_reader import get_datagokr_document


def get_BondWithOptiCallRede(
    serviceKey: str,
    crno: str,
    opbdIsurNm: str,
    timeout_seconds: float = 60.0,
    numOfRows: int = 100,
    resultType: str = "json",
) -> Any | None:
    """ 옵션 행사내역 다운로드. """
    service_url = "1160100/service/GetBondRedeInfoService/getBondWithOptiCallRede"
    if not crno and not opbdIsurNm:
        raise ValueError("crno 또는 opbdIsurNm가 없습니다.")

    params: dict[str, Any] = {
        "serviceKey": serviceKey,
    }
    if crno:
        params["crno"] = crno
    if opbdIsurNm:
        params["opbdIsurNm"] = opbdIsurNm

    return get_datagokr_document(
        serviceUrl=service_url,
        params=params,
        timeout_seconds=timeout_seconds,
        numOfRows=numOfRows,
        resultType=resultType,
    )


def parse_bond_with_opti_call_rede(
    serviceKey: str,
    crno: str,
    opbdIsurNm: str,
    timeout_seconds: float = 60.0,
    raw: Any | None = None,
    isinCdKey: str | None = None,
) -> list[dict[str, Any]] | None:
    """ Parse get_BondWithOptiCallRede results. """
    if raw is None:
        raw = get_BondWithOptiCallRede(
            serviceKey=serviceKey,
            crno=crno,
            opbdIsurNm=opbdIsurNm,
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

    # 아래 항목들은 it에 존재하지만, 현재 라이브러리 목적상 파싱하지 않음
    # "isinCd": it.get("isinCd"),            # ISIN 종목번호, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)
    # "crno": it.get("crno"),                # 기업의 법인등록번호, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)
    # "isinCdNm": it.get("isinCdNm"),        # ISIN 종목명, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)
    # "opbdIsurNm": it.get("opbdIsurNm"),    # 채권의 발행사명, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)
    # "opbdIssuDt": it.get("opbdIssuDt"),    # 채권의 발행일, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)
    # "opbdExprDt": it.get("opbdExprDt"),    # 채권의 만기일, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)
    # "opbdIssuAmt": it.get("opbdIssuAmt"),  # 최초발행액, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)
    # "bondIssuAmt": it.get("bondIssuAmt"),  # 발행잔액, BasiInfo에서 이미 있음(추후 복원 가능하도록 주석 처리)

    out: list[dict[str, Any]] = []
    for it in items:
        isin = it.get("isinCd")
        if isinCdKey:
            if not isin or isin != isinCdKey:
                continue
        else:
            if not isin:
                continue
        out.append(
            {
                "isinCd": isin,
                "optnTcdNm": it.get("optnTcdNm"),
                "opbdClrdDt": it.get("opbdClrdDt"),
                "opbdPamtPayAmt": it.get("opbdPamtPayAmt"),
            }
        )

    return out


