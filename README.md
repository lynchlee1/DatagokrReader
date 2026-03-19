 ## DatagokrReader
- 본 프로젝트는 data.go.kr의 채권 관련 API를 보다 간편하게 사용할 수 있도록 만든 라이브러리입니다. 
- 최신 버전은 다음 링크에서 확인하실 수 있습니다 : https://github.com/lynchlee1/FinanceChatbot
 
 ### Example
 
 ```python
from datagokr_reader import run_bond_workflow

# 띄어쓰기 및 대소문자 무관, 채권 관련 주요 데이터 모두 정리
 result = run_bond_workflow(datagokr_api_key, "공공데이터포털1EB") 
 ```
