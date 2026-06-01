import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


class FakeAgent:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def install_dependency_stubs():
    dotenv = types.ModuleType("dotenv")
    dotenv.load_dotenv = lambda: None
    sys.modules["dotenv"] = dotenv

    strands = types.ModuleType("strands")
    strands.Agent = FakeAgent
    strands.tool = lambda func: func
    sys.modules["strands"] = strands

    strands_tools = types.ModuleType("strands_tools")

    def retrieve(query):
        return f"retrieve: {query}"

    strands_tools.retrieve = retrieve
    sys.modules["strands_tools"] = strands_tools

    tavily = types.ModuleType("tavily")
    tavily.TavilyClient = object
    sys.modules["tavily"] = tavily


def import_stock_agent():
    install_dependency_stubs()
    sys.modules.pop("stock_agent", None)
    return importlib.import_module("stock_agent")


class ContextManager:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def install_streamlit_stub():
    streamlit = types.ModuleType("streamlit")
    streamlit.session_state = {}
    streamlit.set_page_config = lambda **kwargs: None
    streamlit.markdown = lambda *args, **kwargs: None
    streamlit.title = lambda *args, **kwargs: None
    streamlit.text_input = lambda label, value="", key=None: value
    streamlit.container = lambda: ContextManager()
    streamlit.chat_message = lambda role: ContextManager()
    streamlit.spinner = lambda text: ContextManager()
    streamlit.chat_input = lambda prompt: None
    streamlit.rerun = lambda: None

    sidebar = types.SimpleNamespace(
        header=lambda *args, **kwargs: None,
        button=lambda *args, **kwargs: False,
    )
    streamlit.sidebar = sidebar
    sys.modules["streamlit"] = streamlit


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class StockAgentTests(unittest.TestCase):
    def setUp(self):
        self.stock_agent = import_stock_agent()
        self.stock_tools = importlib.import_module("genfinance.stock_tools")

    def test_create_stock_agent_registers_required_tools(self):
        agent = self.stock_agent.create_stock_agent()

        self.assertEqual(agent.kwargs["model"], "us.amazon.nova-lite-v1:0")
        self.assertIn("Knowledge Base", agent.kwargs["system_prompt"])

        tools = agent.kwargs["tools"]
        self.assertIn(self.stock_agent.retrieve, tools)
        self.assertIn(self.stock_agent.tavily_search, tools)
        self.assertIn(self.stock_agent.fmp_get_stock_data, tools)

    def test_streamlit_app_imports_with_stubbed_runtime(self):
        install_streamlit_stub()
        sys.modules.pop("chat_app", None)

        chat_app = importlib.import_module("chat_app")

        self.assertIn("stock_agent", chat_app.st.session_state)
        tools = chat_app.st.session_state["stock_agent"].kwargs["tools"]
        self.assertIn(self.stock_agent.retrieve, tools)
        self.assertIn(self.stock_agent.tavily_search, tools)
        self.assertIn(self.stock_agent.fmp_get_stock_data, tools)

    def test_fmp_returns_clear_error_without_api_key(self):
        with patch.dict(self.stock_agent.os.environ, {}, clear=True):
            result = self.stock_agent.fmp_get_stock_data("AAPL", "price")

        self.assertIn("FMP_API_KEY", result)
        self.assertIn("설정되지 않았습니다", result)

    def test_fmp_profile_data_types_call_profile_endpoint(self):
        for data_type in ["price", "quote", "profile"]:
            with self.subTest(data_type=data_type):
                response = FakeResponse([
                    {
                        "companyName": "Apple Inc.",
                        "symbol": "AAPL",
                        "price": 200,
                        "industry": "Consumer Electronics",
                        "description": "iPhone maker",
                    }
                ])
                requests_get = Mock(return_value=response)

                with patch.dict(self.stock_agent.os.environ, {"FMP_API_KEY": "test-key"}):
                    with patch.object(self.stock_tools.requests, "get", requests_get):
                        result = self.stock_agent.fmp_get_stock_data("AAPL", data_type)

                requests_get.assert_called_once()
                url = requests_get.call_args.args[0]
                params = requests_get.call_args.kwargs["params"]

                self.assertEqual(url, "https://financialmodelingprep.com/stable/profile")
                self.assertEqual(params["symbol"], "AAPL")
                self.assertEqual(params["apikey"], "test-key")
                self.assertIn("Apple Inc.", result)
                self.assertIn("출처: FMP", result)

    def test_fmp_financials_calls_income_statement_endpoint(self):
        response = FakeResponse([
            {
                "symbol": "AAPL",
                "revenue": 100,
                "netIncome": 25,
            }
        ])
        requests_get = Mock(return_value=response)

        with patch.dict(self.stock_agent.os.environ, {"FMP_API_KEY": "test-key"}):
            with patch.object(self.stock_tools.requests, "get", requests_get):
                result = self.stock_agent.fmp_get_stock_data("AAPL", "financials")

        requests_get.assert_called_once()
        url = requests_get.call_args.args[0]
        params = requests_get.call_args.kwargs["params"]

        self.assertEqual(url, "https://financialmodelingprep.com/stable/income-statement-ttm")
        self.assertEqual(params["symbol"], "AAPL")
        self.assertIn("revenue", result)

    def test_fmp_rejects_unsupported_data_type_before_api_call(self):
        requests_get = Mock()

        with patch.dict(self.stock_agent.os.environ, {"FMP_API_KEY": "test-key"}):
            with patch.object(self.stock_tools.requests, "get", requests_get):
                result = self.stock_agent.fmp_get_stock_data("AAPL", "dividends")

        requests_get.assert_not_called()
        self.assertIn("지원하지 않는 data_type", result)


if __name__ == "__main__":
    unittest.main()
