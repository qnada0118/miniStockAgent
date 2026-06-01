import io
import os
import sys

from genfinance.agent_factory import create_stock_agent, get_agent_tools, retrieve
from genfinance.env import load_app_env
from genfinance.stock_prompt import STOCK_AGENT_PROMPT
from genfinance.stock_tools import fmp_get_stock_data, get_stock_info, tavily_search


def safe_input(prompt: str) -> str:
    """UTF-8 인코딩 오류를 안전하게 처리하는 input 함수."""
    try:
        return input(prompt).strip()
    except UnicodeDecodeError:
        try:
            if hasattr(sys.stdin, "buffer"):
                sys.stdin = io.TextIOWrapper(
                    sys.stdin.buffer,
                    encoding="utf-8",
                    errors="replace",
                )
            return input(prompt).strip()
        except (UnicodeDecodeError, UnicodeError):
            try:
                sys.stdout.write(prompt)
                sys.stdout.flush()
                line = sys.stdin.buffer.readline()
                return line.decode("utf-8", errors="replace").strip()
            except Exception:
                raise


def print_environment_warnings():
    required_vars = [
        (
            "KNOWLEDGE_BASE_ID",
            "Knowledge Base 검색 기능이 작동하지 않을 수 있습니다.",
        ),
        (
            "TAVILY_API_KEY",
            "인터넷 검색 기능이 작동하지 않을 수 있습니다.",
        ),
        (
            "FMP_API_KEY",
            "실시간 주가/재무 정보 검색 기능이 제한될 수 있습니다.",
        ),
    ]

    for name, message in required_vars:
        if not os.environ.get(name):
            print(f"경고: {name}가 .env 파일에 설정되지 않았습니다.")
            print(f"{message}\n")


def print_intro():
    print("=" * 60)
    print("주식 투자 어드바이저 챗봇을 시작합니다")
    print("=" * 60)
    print("\n사용 가능한 질문 예시:")
    print("  - 삼성전자 최근 주가 동향은?")
    print("  - 반도체 산업 전망 분석해줘")
    print("  - 테슬라 실적 발표 내용 알려줘")
    print("  - AI 관련 주식 추천해줘")
    print("\n투자 책임은 본인에게 있습니다.")
    print("종료하려면 '종료' 또는 'exit'를 입력하세요.\n")
    print("=" * 60 + "\n")


def should_exit(prompt: str) -> bool:
    return prompt.lower() in ["종료", "exit", "quit", "q"]


def run_chat_loop(stock_agent):
    while True:
        try:
            prompt = safe_input("질문을 입력하세요: ")

            if should_exit(prompt):
                print("\n주식 투자 어드바이저를 종료합니다.")
                break

            if not prompt:
                print("질문을 입력해주세요.\n")
                continue

            try:
                print("\n분석 중...\n")
                stock_agent(prompt)
                print("\n" + "=" * 60 + "\n")
            except UnicodeDecodeError as e:
                print(f"\n인코딩 오류가 발생했습니다: {e}")
                print("응답을 처리하는 중 문제가 발생했습니다. 다시 시도해주세요.\n")
            except Exception as e:
                print(f"\n오류가 발생했습니다: {e}\n")

        except KeyboardInterrupt:
            print("\n\n주식 투자 어드바이저를 종료합니다.")
            break
        except EOFError:
            print("\n\n주식 투자 어드바이저를 종료합니다.")
            break


def main():
    """Run the stock investment advisor agent as a script."""
    load_app_env()
    print_environment_warnings()
    stock_agent = create_stock_agent()
    print_intro()
    run_chat_loop(stock_agent)


if __name__ == "__main__":
    main()
