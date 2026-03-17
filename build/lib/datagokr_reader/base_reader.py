from __future__ import annotations

from typing import Any

import re
import httpx


def get_datagokr_data(
    serviceUrl: str, params: dict[str, Any], timeout_seconds: float = 60.0
) -> Any | None:
    """ Datagokr API를 호출해서 응답 JSON을 반환한다. """
    baseUrl = "http://apis.data.go.kr"
    url = f"{baseUrl}/{serviceUrl}"
    try:
        resp = httpx.get(url, params=params, timeout=timeout_seconds)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None

def get_datagokr_document(
    serviceUrl: str, params: dict[str, Any], timeout_seconds: float = 60.0,
    numOfRows: int = 100, resultType: str = "json",
) -> Any | None:
    """
    Datagokr API를 반복 호출해서 응답 JSON을 반환한다.
    1. `pageNo = 1`부터 `pageNo = totalCount / numOfRows` 페이지까지 반복 호출한다.
    2. 각 페이지의 items를 모두 모아서 반환한다. 
        반환 형식은 기본 형식과 동일하며, items는 {"item": [...]} 구조와 단순 리스트 구조를 모두 지원한다. 
    ```json
    {
      "response": {
        "body": {
          "pageNo": 1,
          "numOfRows": 100,
          "totalCount": ...,
          "items": # contents
        }
      }
    }
    ```
    """
    # 공통 파라미터 설정 (기본값이 있으면 덮어쓰지 않음)
    base_params: dict[str, Any] = dict(params)
    base_params.setdefault("numOfRows", numOfRows)
    base_params.setdefault("resultType", resultType)

    # 1페이지 호출
    first_params = dict(base_params)
    first_params["pageNo"] = 1
    first_doc = get_datagokr_data(serviceUrl, first_params, timeout_seconds)
    if first_doc is None:
        return None
    try:
        body = first_doc["response"]["body"]
    except Exception:
        return first_doc

    # 전체 개수 확인
    total_count_raw = body.get("totalCount", 0)
    try:
        total_count = int(total_count_raw)
    except Exception:
        total_count = 0
    if total_count <= 0:
        return first_doc

    # items 추출
    def extract_items(items_obj: Any) -> list[Any]:
        # 1) items가 None인 경우 -> []
        if items_obj is None:
            return []
        # 2) "items": {"item": [...]} OR "items": {"item": {...}} 인 경우
        #    - inner가 리스트면 그대로 리스트 반환
        #    - inner가 단일 객체면 리스트로 감싸서 반환
        if isinstance(items_obj, dict) and "item" in items_obj:
            inner = items_obj.get("item")
            if inner is None:
                return []
            if isinstance(inner, list):
                return inner
            return [inner]
        # 3) "items": [...] 인 경우 -> 그대로 리스트 반환
        if isinstance(items_obj, list):
            return items_obj
        # 4) 그 외에는 리스트로 감싸서 반환
        return [items_obj]

    items_obj = body.get("items")
    all_items: list[Any] = extract_items(items_obj)

    # 총 페이지 수 계산
    total_pages = (total_count + numOfRows - 1) // numOfRows

    # 2페이지부터 마지막 페이지까지 반복 호출
    for page_no in range(2, total_pages + 1):
        page_params = dict(base_params)
        page_params["pageNo"] = page_no
        page_doc = get_datagokr_data(serviceUrl, page_params, timeout_seconds)
        if page_doc is None:
            break
        try:
            page_body = page_doc["response"]["body"]
            page_items_obj = page_body.get("items")
        except Exception:
            break
        all_items.extend(extract_items(page_items_obj))

    # 첫 응답 객체에 모든 items를 합쳐서 세팅
    if isinstance(items_obj, dict) and "item" in items_obj:
        items_obj["item"] = all_items
        body["items"] = items_obj
    else:
        body["items"] = all_items

    # 메타 정보 정리 (pageNo는 1, numOfRows는 입력값, totalCount는 실제 아이템 개수)
    body["pageNo"] = 1
    body["numOfRows"] = numOfRows
    body["totalCount"] = len(all_items)

    return first_doc


def normalize_name(name: str) -> str:
    name_no_space = name.replace(" ", "")
    name_no_space = re.sub(r"[A-Za-z]+", lambda m: m.group(0).lower(), name_no_space)
    paren_index = name_no_space.find("(")
    if paren_index != -1:
        return name_no_space[:paren_index]
    return name_no_space

def issuer_name_from_bond_name(bond_name: str) -> str:
    """ 채권명에서 발행사명을 추출. (숫자를 기준으로 절삭) """
    normalized = normalize_name(bond_name)
    m = re.search(r"\d", normalized)
    if not m:
        return normalized
    return normalized[: m.start()]  
