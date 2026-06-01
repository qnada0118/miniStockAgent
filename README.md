# miniStockAgent

AWS Bedrock Knowledge Base, Financial Modeling Prep(FMP), Tavily를 함께 사용하는 GenFinance 구조의 주식 투자 분석 Agent입니다.

핵심 흐름은 다음과 같습니다.

1. 사용자가 투자 관련 질문을 입력합니다.
2. Agent가 먼저 AWS Bedrock Knowledge Base를 검색합니다.
3. Knowledge Base 결과가 부족하거나 최신/정량 데이터가 필요하면 FMP 또는 Tavily를 호출합니다.
4. 출처를 포함해 한국어 투자 분석 답변을 생성합니다.

## 프로젝트 구조

```text
.
├── chat_app.py          # Streamlit 채팅 UI
├── chat_style.py        # Streamlit 스타일
├── stock_agent.py       # Strands Agent, 도구, 프롬프트
├── node-sample/         # Elastic Beanstalk Node 샘플 분리 보관
└── README.md
```

## 실행 방법

Python 가상환경을 만들고 필요한 패키지를 설치합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Streamlit 앱 실행:

```bash
streamlit run chat_app.py
```

CLI 실행:

```bash
python stock_agent.py
```

## 환경 변수

프로젝트 루트에 `.env` 파일을 만들고 아래 값을 설정합니다.

```env
KNOWLEDGE_BASE_ID=
TAVILY_API_KEY=
FMP_API_KEY=
AWS_REGION=
AWS_PROFILE=
```

### 환경 변수 설명

| 이름 | 설명 | 필수 여부 |
| --- | --- | --- |
| `KNOWLEDGE_BASE_ID` | AWS Bedrock Knowledge Base ID | 필수 |
| `TAVILY_API_KEY` | 최신 뉴스/웹 검색용 Tavily API 키 | 필수 |
| `FMP_API_KEY` | 주가/기업 프로필/재무 데이터 조회용 FMP API 키 | 필수 |
| `AWS_REGION` | Bedrock과 Knowledge Base가 있는 AWS 리전 | 필수 |
| `AWS_PROFILE` | 로컬 AWS 자격 증명 프로필 이름 | 선택 |

## AWS Bedrock Knowledge Base 준비

1. AWS 콘솔에서 S3 버킷을 생성합니다.
2. 투자 분석에 사용할 PDF, Excel, 리서치 자료를 S3에 업로드합니다.
3. Amazon Bedrock에서 Knowledge Base를 생성합니다.
4. 데이터 소스로 S3 버킷을 연결합니다.
5. 임베딩 모델과 벡터 저장소를 설정합니다.
6. Sync 또는 Ingestion 작업을 실행해 문서를 인덱싱합니다.
7. 생성된 Knowledge Base ID를 `.env`의 `KNOWLEDGE_BASE_ID`에 넣습니다.

## 외부 API 설정

### FMP

FMP는 주가, 기업 프로필, 손익계산서 등 구조화된 금융 데이터를 조회하는 데 사용합니다.

1. Financial Modeling Prep에서 API 키를 발급합니다.
2. `.env`의 `FMP_API_KEY`에 값을 설정합니다.
3. 현재 `fmp_get_stock_data`는 `price`, `quote`, `profile`, `financials` 데이터 타입을 지원합니다.

### Tavily

Tavily는 최신 뉴스, 최근 이슈, Knowledge Base에 없는 웹 정보를 검색하는 데 사용합니다.

1. Tavily에서 API 키를 발급합니다.
2. `.env`의 `TAVILY_API_KEY`에 값을 설정합니다.

## Agent 도구 구성

현재 Agent는 다음 도구를 사용합니다.

```python
tools=[retrieve, tavily_search, fmp_get_stock_data, get_stock_info]
```

GenFinance 기준 핵심 도구는 다음 세 가지입니다.

```python
tools=[retrieve, tavily_search, fmp_get_stock_data]
```

`get_stock_info`는 Tavily 검색을 감싼 보조 도구이므로, 구조를 더 단순하게 가져가려면 이후 제거할 수 있습니다.

## 답변 원칙

Agent는 다음 원칙을 따릅니다.

- 모든 투자 관련 질문은 Knowledge Base 검색을 먼저 수행합니다.
- Knowledge Base 결과를 1차 근거로 사용합니다.
- 주가, 실적, 재무제표, 재무지표는 FMP를 사용합니다.
- 최신 뉴스, 최근 이슈, KB에 없는 정보는 Tavily를 사용합니다.
- 답변에는 사용한 데이터 출처를 포함합니다.
- 근거가 부족한 내용은 추측하지 않고 부족한 정보를 명시합니다.

## 주의 사항

이 프로젝트는 투자 판단을 자동화하기 위한 도구가 아니라, 자료 검색과 분석 초안을 돕기 위한 보조 Agent입니다.

투자는 본인의 판단과 책임 하에 이루어져야 합니다.
