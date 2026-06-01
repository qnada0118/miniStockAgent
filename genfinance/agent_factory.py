import os

from strands import Agent
from strands_tools import retrieve

from genfinance.stock_prompt import STOCK_AGENT_PROMPT
from genfinance.stock_tools import fmp_get_stock_data, get_stock_info, tavily_search


DEFAULT_BEDROCK_MODEL_ID = "us.amazon.nova-lite-v1:0"


def infer_nova_lite_profile_id(region: str) -> str:
    """Return the Nova Lite inference profile ID for a Bedrock source region."""
    if region.startswith("ap-"):
        return "apac.amazon.nova-lite-v1:0"
    if region.startswith("eu-") or region in {"il-central-1", "me-central-1"}:
        return "eu.amazon.nova-lite-v1:0"
    return DEFAULT_BEDROCK_MODEL_ID


def get_bedrock_model_id():
    """Return the Bedrock model ID configured for this app."""
    configured_model_id = os.environ.get("BEDROCK_MODEL_ID", "").strip()
    if configured_model_id:
        return configured_model_id

    region = (
        os.environ.get("AWS_REGION", "").strip()
        or os.environ.get("AWS_DEFAULT_REGION", "").strip()
    )
    return infer_nova_lite_profile_id(region)


def get_agent_tools():
    """Return the shared tool list for CLI, Streamlit, and tests."""
    return [retrieve, tavily_search, fmp_get_stock_data, get_stock_info]


def build_turn_prompt(user_input: str) -> str:
    """Add per-turn tool-order instructions to reduce carryover from prior turns."""
    return "\n".join(
        [
            "이번 사용자 질문을 새로운 투자 분석 요청으로 처리하세요.",
            "이전 답변에서 Tavily 또는 FMP를 먼저 사용했더라도 그 순서를 반복하지 마세요.",
            "투자 관련 질문이면 반드시 첫 번째 도구 호출은 `retrieve`여야 합니다.",
            "`retrieve` 결과를 먼저 확인한 뒤, 필요한 경우에만 Tavily 또는 FMP로 보완하세요.",
            "",
            "사용자 질문:",
            user_input,
        ]
    )


def create_stock_agent():
    """Create the stock investment advisor Agent with the shared configuration."""
    return Agent(
        model=get_bedrock_model_id(),
        system_prompt=STOCK_AGENT_PROMPT,
        tools=get_agent_tools(),
    )
