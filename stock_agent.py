import sys
import os
import io
import requests # FMP
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import retrieve
from tavily import TavilyClient
import setting

STOCK_AGENT_PROMPT = """
당신은 GenFinance 아키텍처를 따르는 한국어 주식 투자 분석 Agent입니다.
모든 답변은 투자 초보자도 이해할 수 있도록 쉽고 명확하게 작성합니다.

## 도구 사용 순서
1. 모든 투자 관련 질문은 반드시 `retrieve` 도구를 먼저 호출해 AWS Bedrock Knowledge Base를 검색합니다.
2. 답변의 1차 근거는 항상 Knowledge Base 검색 결과입니다.
3. Knowledge Base 결과가 부족하거나 최신/정량 데이터가 필요할 때만 보조 도구를 사용합니다.
4. 주가, 기업 프로필, 실적, 재무제표, 재무지표 등 구조화된 금융 데이터는 `fmp_get_stock_data`를 사용합니다.
5. 최신 뉴스, 최근 이슈, 시장 동향, Knowledge Base에 없는 웹 정보는 `tavily_search`를 사용합니다.
6. 근거가 부족하면 추측하지 말고 어떤 정보가 부족한지 명확히 말합니다.

## 출처 규칙
- 답변에는 반드시 사용한 데이터 출처를 포함합니다.
- `retrieve` 결과는 문서명, 페이지, 표/문단 등 가능한 메타데이터를 함께 표시합니다.
- `fmp_get_stock_data`를 사용한 경우 출처를 Financial Modeling Prep(FMP)로 표시합니다.
- `tavily_search`를 사용한 경우 검색 결과의 제목과 URL을 표시합니다.

## 답변 형식
일반 투자 분석 답변은 아래 구조를 따릅니다.

## [기업명 또는 주제] 분석

### 핵심 요약
- 질문에 대한 결론을 3줄 이내로 요약합니다.

### 사용한 데이터 출처
- Knowledge Base:
- FMP:
- Tavily:

### 재무 데이터
- 매출, 영업이익, 순이익, 성장률, 마진율, 밸류에이션 등 확인 가능한 수치를 정리합니다.
- 숫자는 단위와 기준 시점을 함께 씁니다.

### 최신 뉴스/이슈
- 최신 정보가 필요한 경우에만 작성합니다.

### 투자 포인트
- 사실 기반의 긍정 요인을 1~3개 정리합니다.

### 리스크
- 확인 가능한 위험 요인을 1~3개 정리합니다.

---
투자는 본인의 판단과 책임 하에 이루어져야 합니다.
"""




@tool
def tavily_search(query: str) -> str:
    """Tavily API를 사용하여 웹에서 주식 및 투자 관련 정보를 검색합니다.

    최신 주식 뉴스, 시장 동향, 기업 공시, 경제 뉴스 등을 검색할 때 유용합니다.
    
    Args:
        query: 검색할 키워드나 질문 (예: "삼성전자 최근 뉴스", "반도체 시장 전망")
    """
    tavily_key = os.environ.get("TAVILY_API_KEY")
    if not tavily_key:
        return "오류: TAVILY_API_KEY 환경 변수가 설정되지 않았습니다."
        
    try:
        tavily = TavilyClient(api_key=tavily_key)
        # search_depth="advanced"로 설정하면 더 깊이 있는 검색 결과를 제공합니다.
        response = tavily.search(query=query, search_depth="advanced")
        
        # 결과를 문자열로 포맷팅
        results = []
        for result in response.get('results', []):
            title = result.get('title', 'No Title')
            url = result.get('url', 'No URL')
            content = result.get('content', 'No Content')
            results.append(f"Title: {title}\nURL: {url}\nContent: {content}\n---")
            
        return "\n".join(results)
    except Exception as e:
        return f"Tavily 검색 중 오류 발생: {str(e)}"


@tool
def get_stock_info(company_name: str) -> str:
    """특정 기업의 주식 정보와 최근 뉴스를 검색합니다.
    
    Args:
        company_name: 기업명 (예: "삼성전자", "Apple", "Tesla")
    """
    # Tavily를 사용하여 기업 정보 검색
    search_query = f"{company_name} 주가 실적 뉴스 분석"
    return tavily_search(search_query)


@tool
def fmp_get_stock_data(ticker: str, data_type: str) -> str:
    """
    Financial Modeling Prep (FMP) API를 사용하여 특정 기업의 주식 데이터를 조회합니다.
    Legacy Endpoint 문제를 회피하고 범용 API 호출 방식을 적용합니다.
    """

    # 1. API 키 로드 (os.environ.get만 사용)
    fmp_key = os.environ.get("FMP_API_KEY")

    if not fmp_key:
        return "오류: FMP_API_KEY 환경 변수가 설정되지 않았습니다."

    # 🚨 안정적인 (Stable) 기본 URL 사용
    BASE_URL = "https://financialmodelingprep.com/stable/"
    path = ""
    params = {}

    # 2. 데이터 유형별 경로 및 매개변수 설정 (수정된 부분)
    if data_type in ['price', 'quote', 'profile']:
        # 주가/쿼트 요청 시, Basic 플랜에서 접근 가능한 'profile' 엔드포인트 사용 (Legacy 회피 전략)
        path = "profile"
        params['symbol'] = ticker
    elif data_type == 'financials':
        # ✅ 수정 완료: TTM 손익계산서 호출을 위해 BASE_URL과 path 변경
        BASE_URL = "https://financialmodelingprep.com/stable/"
        path = "income-statement-ttm"
        params['symbol'] = ticker
    else:
        return f"오류: 지원하지 않는 data_type '{data_type}'입니다."

    # 3. API 호출
    url = f"{BASE_URL}{path}"
    params['apikey'] = fmp_key # 최종적으로 API 키를 매개변수에 추가

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status() # 4xx, 5xx 에러 발생 시 예외 처리

        data = response.json()

        if not data or (isinstance(data, list) and len(data) == 0):
            return f"FMP API에서 티커 {ticker}에 대한 정보를 찾을 수 없습니다."

        # 4. 결과 포맷팅 (AI 모델이 읽기 쉬운 문자열로 변환)
        if data_type in ['price', 'quote', 'profile'] and isinstance(data, list) and len(data) > 0:
            profile_data = data[0]
            # Profile 엔드포인트에서 주가(price)를 추출하여 반환
            return (
                f"기업 프로필 및 주가 정보 (출처: FMP Stable/profile):\n"
                f"기업명: {profile_data.get('companyName', 'N/A')}\n"
                f"티커: {profile_data.get('symbol', ticker)}\n"
                f"현재 주가: {profile_data.get('price', 'N/A')}\n"
                f"산업: {profile_data.get('industry', 'N/A')}\n"
                f"설명 요약: {profile_data.get('description', 'N/A')[:200]}..."
            )

        # 재무 정보의 경우 JSON 문자열 그대로 반환
        return str(data[0]) if isinstance(data, list) and len(data) > 0 else str(data)

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        # 권한 오류(403) 발생 시, Tavily로 우회하도록 유도하는 메시지 반환
        if status == 403:
            return (
                f"FMP API 호출 실패 (상태 코드 {status}): 권한 부족. "
                "요청 데이터에 접근이 제한됩니다. Tavily 검색으로 최신 정보를 시도하세요."
            )
        return f"FMP API 호출 중 HTTP 오류 발생 (코드 {status}): {e.response.text}"
    except requests.exceptions.RequestException as e:
        return f"FMP API 호출 중 네트워크 오류 발생: {e}"
    except Exception as e:
        return f"FMP API 응답 처리 중 오류 발생: {e}"


def safe_input(prompt: str) -> str:
    """UTF-8 인코딩 오류를 안전하게 처리하는 input 함수."""
    try:
        # 먼저 일반 input 시도
        return input(prompt).strip()
    except UnicodeDecodeError:
        # 인코딩 오류 발생 시 재시도
        try:
            # stdin을 UTF-8로 재설정
            if hasattr(sys.stdin, 'buffer'):
                sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
            return input(prompt).strip()
        except (UnicodeDecodeError, UnicodeError):
            # 그래도 실패하면 raw bytes로 읽기
            try:
                sys.stdout.write(prompt)
                sys.stdout.flush()
                line = sys.stdin.buffer.readline()
                return line.decode('utf-8', errors='replace').strip()
            except Exception:
                raise


def main():
    """Main function to run the stock investment advisor agent as a script."""
    
    # .env 파일에서 환경 변수 로드
    load_dotenv()
    
    # Knowledge Base ID와 Tavily API Key 확인
    kb_id = os.environ.get("KNOWLEDGE_BASE_ID")
    tavily_key = os.environ.get("TAVILY_API_KEY")
    fmp_key = os.environ.get("FMP_API_KEY")
    
    if not kb_id:
        print("⚠️ 경고: KNOWLEDGE_BASE_ID가 .env 파일에 설정되지 않았습니다.")
        print("Knowledge Base 검색 기능이 작동하지 않을 수 있습니다.\n")
    
    if not tavily_key:
        print("⚠️ 경고: TAVILY_API_KEY가 .env 파일에 설정되지 않았습니다.")
        print("인터넷 검색 기능이 작동하지 않을 수 있습니다.\n")
    
    if not fmp_key:
        print("⚠️ 경고: FMP_API_KEY가 .env 파일에 설정되지 않았습니다.")
        print("실시간 주가/재무 정보 검색 기능이 제한될 수 있습니다.\n")

    stock_agent = Agent(
        model="us.amazon.nova-lite-v1:0",
        system_prompt=STOCK_AGENT_PROMPT,
        tools=[retrieve, tavily_search, fmp_get_stock_data, get_stock_info]
    )
    
    '''
    # Command line argument이 있으면 한 번만 실행하고 종료
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        try:
            response = stock_agent(prompt)
            print(response)
        except UnicodeDecodeError as e:
            print(f"인코딩 오류가 발생했습니다: {e}")
            print("응답을 처리하는 중 문제가 발생했습니다.")
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
        return
    '''
    
    # 대화형 모드: 사용자가 "종료" 또는 "exit"를 입력할 때까지 계속 실행
    print("=" * 60)
    print("🔹 주식 투자 어드바이저 챗봇을 시작합니다 🔹")
    print("=" * 60)
    print("\n💡 사용 가능한 질문 예시:")
    print("  - 삼성전자 최근 주가 동향은?")
    print("  - 반도체 산업 전망 분석해줘")
    print("  - 테슬라 실적 발표 내용 알려줘")
    print("  - AI 관련 주식 추천해줘")
    print("\n  투자 책임은 본인에게 있습니다.")
    print("종료하려면 '종료' 또는 'exit'를 입력하세요.\n")
    print("=" * 60 + "\n")
    
    while True:
        try:
            prompt = safe_input("질문을 입력하세요: ")
            
            # 종료 조건 확인
            if prompt.lower() in ['종료', 'exit', 'quit', 'q']:
                print("\n주식 투자 어드바이저를 종료합니다. 성공적인 투자 되세요!")
                break
            
            # 빈 입력 처리
            if not prompt:
                print("질문을 입력해주세요.\n")
                continue
            
            # 에이전트 실행
            try:
                print("\n🔍 분석 중...\n")
                response = stock_agent(prompt)
                #print(f"답변:\n{response}\n")
                print("\n"+"=" * 60 + "\n")
            except UnicodeDecodeError as e:
                print(f"\n인코딩 오류가 발생했습니다: {e}")
                print("응답을 처리하는 중 문제가 발생했습니다. 다시 시도해주세요.\n")
            except Exception as e:
                print(f"\n오류가 발생했습니다: {e}\n")
                
        except KeyboardInterrupt:
            print("\n\n주식 투자 어드바이저를 종료합니다. 성공적인 투자 되세요! 📈")
            break
        except EOFError:
            print("\n\n주식 투자 어드바이저를 종료합니다. 성공적인 투자 되세요! 📈")
            break


if __name__ == "__main__":
    main()
