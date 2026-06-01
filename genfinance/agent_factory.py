from strands import Agent
from strands_tools import retrieve

from genfinance.stock_prompt import STOCK_AGENT_PROMPT
from genfinance.stock_tools import fmp_get_stock_data, get_stock_info, tavily_search


def get_agent_tools():
    """Return the shared tool list for CLI, Streamlit, and tests."""
    return [retrieve, tavily_search, fmp_get_stock_data, get_stock_info]


def create_stock_agent():
    """Create the stock investment advisor Agent with the shared configuration."""
    return Agent(
        model="us.amazon.nova-lite-v1:0",
        system_prompt=STOCK_AGENT_PROMPT,
        tools=get_agent_tools(),
    )
