 ## DatagokrReader
 
 data.go.kr의 채권 관련 API를 사용하기 편하게 만든 라이브러리입니다.
 
 ### Example
 
 ```python
 from src.search_bond import run_bond_workflow

# 띄어쓰기 및 대소문자 무관, 채권 관련 주요 데이터 모두 정리
 result = run_bond_workflow(datagokr_api_key, "공공데이터포털1EB") 
 ```