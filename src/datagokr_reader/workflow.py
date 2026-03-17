from __future__ import annotations

from datagokr_reader import (
    parse_bond_with_opti_call_rede,
    parse_earl_exer_opti,
    parse_issu_issu_item_stat,
    parse_opti_exer,
    parse_opti_exer_pric_adju,
    parse_bond_basi_info,
)
from datagokr_reader.base_reader import issuer_name_from_bond_name, normalize_name


def run_bond_workflow(datagokr_api_key: str, bond_name: str):
    """
    채권명 to {"함수명": 결과, ...} dict
    """
    bond_name_normalized = normalize_name(bond_name)
    issuer_name = issuer_name_from_bond_name(bond_name)

    issu = parse_issu_issu_item_stat(
        serviceKey=datagokr_api_key,
        bondIsurNm=issuer_name,
        bondNm=bond_name_normalized,
    )

    isinCd = issu.get("isinCd") if isinstance(issu, dict) else ""
    basDt = issu.get("기준일자") if isinstance(issu, dict) else ""

    bond_with = parse_bond_with_opti_call_rede(
        serviceKey=datagokr_api_key,
        isinCd=isinCd,
    )
    opti_exer = parse_opti_exer(
        serviceKey=datagokr_api_key,
        isinCd=isinCd,
    )
    opti_adju = parse_opti_exer_pric_adju(
        serviceKey=datagokr_api_key,
        isinCd=isinCd,
    )
    earl = (
        parse_earl_exer_opti(
            serviceKey=datagokr_api_key,
            basDt=basDt,
            isinCd=isinCd,
        )
        if basDt and isinCd
        else None
    )

    bond_basi = (
        parse_bond_basi_info(
            serviceKey=datagokr_api_key,
            basDt=basDt,
            isinCd=isinCd,
        )
        if basDt and isinCd
        else None
    )

    return {
        "발행인별채권조회": issu,
        "옵션행사내역": bond_with,
        "주식행사내역": opti_exer,
        "주식행사가조정내역": opti_adju,
        "옵션행사일정": earl,
        "채권기초정보": bond_basi,
    }
