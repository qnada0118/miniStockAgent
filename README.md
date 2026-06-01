# miniStockAgent

AWS Bedrock Knowledge Base, Financial Modeling Prep(FMP), Tavily를 함께 사용하는 주식 투자 분석 Agent입니다. 사용자의 투자 관련 질문에 대해 사내/개인 리서치 자료를 먼저 검색하고, 필요한 경우 최신 웹 정보와 정량 금융 데이터를 보완해 한국어 답변을 생성합니다.

> 투자 판단을 자동화하는 도구가 아니라, 자료 검색과 분석 초안 작성을 돕는 보조 Agent입니다. 최종 투자 결정과 결과에 대한 책임은 사용자 본인에게 있습니다.

## 주요 기능

- AWS Bedrock Knowledge Base 기반 리서치 자료 검색
- FMP 기반 주가, 기업 프로필, 재무제표, 재무지표 조회
- Tavily 기반 최신 뉴스와 웹 정보 검색
- Streamlit 채팅 UI
- CLI 대화 모드
- 한국 상장사 이름/종목코드 일부를 FMP용 심볼로 변환
- 외부 API 호출 없이 실행 가능한 단위 테스트

## 동작 흐름

1. 사용자가 투자 관련 질문을 입력합니다.
2. Agent가 먼저 Bedrock Knowledge Base의 `retrieve` 도구를 호출합니다.
3. Knowledge Base 결과가 부족하거나 최신 뉴스/정량 데이터가 필요하면 Tavily 또는 FMP를 호출합니다.
4. 사용한 근거와 출처를 포함해 한국어 투자 분석 답변을 생성합니다.

## 프로젝트 구조

```text
.
├── chat_app.py                 # Streamlit 채팅 UI
├── stock_agent.py              # CLI 실행 진입점
├── genfinance/
│   ├── agent_factory.py        # Strands Agent 생성 및 모델/도구 설정
│   ├── env.py                  # .env 로딩 및 AWS 환경변수 보정
│   ├── stock_prompt.py         # Agent 시스템 프롬프트
│   └── stock_tools.py          # Tavily/FMP 도구 및 KRX 심볼 변환
├── ui/
│   ├── assets/                 # UI 로고 등 정적 자산
│   └── chat_style.py           # Streamlit 스타일
├── docs/s3/raw/krx/            # 예시 KRX 원천 데이터
├── tests/                      # 단위 테스트
├── node-sample/                # Node 샘플 보관
├── requirements.txt
└── README.md
```

## 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 환경 변수

프로젝트 루트에 `.env` 파일을 만들고 필요한 값을 설정합니다.

```env
KNOWLEDGE_BASE_ID=
TAVILY_API_KEY=
FMP_API_KEY=
AWS_REGION=
AWS_PROFILE=
BEDROCK_MODEL_ID=
```

| 이름 | 필수 | 설명 |
| --- | --- | --- |
| `KNOWLEDGE_BASE_ID` | 권장 | AWS Bedrock Knowledge Base ID. 없으면 KB 검색 기능이 제한됩니다. |
| `TAVILY_API_KEY` | 권장 | 최신 뉴스/웹 검색용 Tavily API 키. 없으면 웹 검색 기능이 제한됩니다. |
| `FMP_API_KEY` | 권장 | 주가/기업 프로필/재무 데이터 조회용 FMP API 키. 없으면 정량 데이터 조회가 제한됩니다. |
| `AWS_REGION` | 권장 | Bedrock과 Knowledge Base가 있는 AWS 리전. 예: `ap-northeast-2` |
| `AWS_PROFILE` | 선택 | 로컬 AWS 자격 증명 프로필 이름. 빈 값이면 자동 제거됩니다. |
| `BEDROCK_MODEL_ID` | 선택 | 사용할 Bedrock 모델 또는 inference profile ID. 비워두면 리전에 따라 Nova Lite profile을 자동 선택합니다. |

`BEDROCK_MODEL_ID`를 설정하지 않으면 `AWS_REGION` 기준으로 다음 profile을 사용합니다.

| 리전 | 기본 profile |
| --- | --- |
| `ap-*` | `apac.amazon.nova-lite-v1:0` |
| `eu-*`, `il-central-1`, `me-central-1` | `eu.amazon.nova-lite-v1:0` |
| 그 외 | `us.amazon.nova-lite-v1:0` |

## 실행

Streamlit UI:

```bash
streamlit run chat_app.py
```

CLI:

```bash
python stock_agent.py
```

CLI 종료 명령:

```text
종료
exit
quit
q
```

## 테스트

외부 API와 AWS를 실제 호출하지 않는 단위 테스트를 실행합니다.

```bash
python3 -m unittest discover -s tests
```

## Agent 도구

현재 Agent는 다음 도구를 등록합니다.

```python
tools = [retrieve, tavily_search, fmp_get_stock_data, get_stock_info]
```

| 도구 | 용도 |
| --- | --- |
| `retrieve` | Bedrock Knowledge Base 검색 |
| `tavily_search` | 최신 뉴스, 시장 동향, 웹 정보 검색 |
| `fmp_get_stock_data` | FMP 주가/재무 데이터 조회 |
| `get_stock_info` | 기업명 기반 Tavily 검색 보조 도구 |

투자 관련 질문은 매 턴 `retrieve`를 먼저 호출하도록 프롬프트가 구성되어 있습니다. 이후 부족한 정보 유형에 따라 Tavily 또는 FMP를 보조 근거로 사용합니다.

## FMP 지원 데이터 타입

`fmp_get_stock_data(ticker, data_type)`에서 사용할 수 있는 `data_type`은 다음과 같습니다.

| data_type | 용도 |
| --- | --- |
| `price` | 현재 주가와 기업 프로필 |
| `quote` | 현재 주가와 기업 프로필 |
| `profile` | 기업 프로필 |
| `historical_price` | 과거 일별 시세 |
| `market_cap` | 시가총액 |
| `enterprise_value` | 기업가치 |
| `ratios` | 주요 재무비율(TTM) |
| `key_metrics` | 주요 재무지표(TTM) |
| `financials` | TTM 손익계산서 |
| `income_statement` | 손익계산서 |
| `balance_sheet` | 재무상태표 |
| `cash_flow` | 현금흐름표 |

한국 상장사는 `docs/s3/raw/krx/stock-master`의 KRX 종목 마스터 CSV를 참고해 일부 종목명을 FMP 심볼로 변환합니다. 예를 들어 `삼성전자`는 `005930.KS`로 조회됩니다. 6자리 숫자 코드는 기본적으로 KOSPI 심볼인 `.KS`를 붙입니다.

## Bedrock Knowledge Base 준비

1. AWS 콘솔에서 S3 버킷을 생성합니다.
2. 투자 분석에 사용할 PDF, Excel, 리서치 자료를 S3에 업로드합니다.
3. Amazon Bedrock에서 Knowledge Base를 생성합니다.
4. 데이터 소스로 S3 버킷을 연결합니다.
5. 임베딩 모델과 벡터 저장소를 설정합니다.
6. Sync 또는 Ingestion 작업을 실행해 문서를 인덱싱합니다.
7. 생성된 Knowledge Base ID를 `.env`의 `KNOWLEDGE_BASE_ID`에 설정합니다.

## 답변 원칙

- 투자 관련 질문은 Knowledge Base 검색을 먼저 수행합니다.
- Knowledge Base 결과를 1차 근거로 사용합니다.
- 주가, 실적, 재무제표, 재무지표는 FMP로 보완합니다.
- 최신 뉴스, 최근 이슈, KB에 없는 정보는 Tavily로 보완합니다.
- 답변에는 가능한 한 데이터 출처를 포함합니다.
- 근거가 부족한 내용은 추측하지 않고 부족한 정보를 명시합니다.
