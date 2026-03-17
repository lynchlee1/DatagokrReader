from __future__ import annotations

from datagokr_reader import (
    parse_bond_with_opti_call_rede,
    parse_earl_exer_opti,
    parse_issu_issu_item_stat,
    parse_opti_exer,
    parse_opti_exer_pric_adju,
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

    crno = issu.get("crno") if isinstance(issu, dict) else ""
    isinCdKey = issu.get("isinCd") if isinstance(issu, dict) else None
    basDt = issu.get("basDt") if isinstance(issu, dict) else None

    bond_with = parse_bond_with_opti_call_rede(
        serviceKey=datagokr_api_key,
        crno=crno,
        opbdIsurNm=issuer_name,
        isinCdKey=isinCdKey,
    )
    opti_exer = parse_opti_exer(
        serviceKey=datagokr_api_key,
        crno=crno,
        isinCdKey=isinCdKey,
    )
    opti_adju = parse_opti_exer_pric_adju(
        serviceKey=datagokr_api_key,
        crno=crno,
        isinCdKey=isinCdKey,
    )
    earl = parse_earl_exer_opti(
        serviceKey=datagokr_api_key,
        basDt=basDt,
        bondIsurNm=issuer_name,
        crno=crno,
        isinCdKey=isinCdKey,
    )

    return {
        "parse_issu_issu_item_stat": issu,
        "parse_bond_with_opti_call_rede": bond_with,
        "parse_opti_exer": opti_exer,
        "parse_opti_exer_pric_adju": opti_adju,
        "parse_earl_exer_opti": earl,
    }

