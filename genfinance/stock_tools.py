import os

import requests
from strands import tool
from tavily import TavilyClient


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
        response = tavily.search(query=query, search_depth="advanced")

        results = []
        for result in response.get("results", []):
            title = result.get("title", "No Title")
            url = result.get("url", "No URL")
            content = result.get("content", "No Content")
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
    search_query = f"{company_name} 주가 실적 뉴스 분석"
    return tavily_search(search_query)


@tool
def fmp_get_stock_data(ticker: str, data_type: str) -> str:
    """
    Financial Modeling Prep (FMP) API를 사용하여 특정 기업의 주식 데이터를 조회합니다.
    Legacy Endpoint 문제를 회피하고 범용 API 호출 방식을 적용합니다.
    """
    fmp_key = os.environ.get("FMP_API_KEY")

    if not fmp_key:
        return "오류: FMP_API_KEY 환경 변수가 설정되지 않았습니다."

    base_url = "https://financialmodelingprep.com/stable/"
    params = {"symbol": ticker}

    if data_type in ["price", "quote", "profile"]:
        path = "profile"
    elif data_type == "financials":
        path = "income-statement-ttm"
    else:
        return f"오류: 지원하지 않는 data_type '{data_type}'입니다."

    url = f"{base_url}{path}"
    params["apikey"] = fmp_key

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()

        if not data or (isinstance(data, list) and len(data) == 0):
            return f"FMP API에서 티커 {ticker}에 대한 정보를 찾을 수 없습니다."

        if data_type in ["price", "quote", "profile"] and isinstance(data, list):
            profile_data = data[0]
            return (
                f"기업 프로필 및 주가 정보 (출처: FMP Stable/profile):\n"
                f"기업명: {profile_data.get('companyName', 'N/A')}\n"
                f"티커: {profile_data.get('symbol', ticker)}\n"
                f"현재 주가: {profile_data.get('price', 'N/A')}\n"
                f"산업: {profile_data.get('industry', 'N/A')}\n"
                f"설명 요약: {profile_data.get('description', 'N/A')[:200]}..."
            )

        return str(data[0]) if isinstance(data, list) and len(data) > 0 else str(data)

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
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
