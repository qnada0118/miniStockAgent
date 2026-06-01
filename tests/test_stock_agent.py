import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


class FakeAgent:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.calls = []

    def __call__(self, prompt):
        self.calls.append(prompt)
        return types.SimpleNamespace(final_output="테스트 답변")


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

    requests = types.ModuleType("requests")

    class RequestException(Exception):
        pass

    class HTTPError(RequestException):
        pass

    requests.get = Mock()
    requests.exceptions = types.SimpleNamespace(
        HTTPError=HTTPError,
        RequestException=RequestException,
    )
    sys.modules["requests"] = requests


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
        with patch.dict(self.stock_agent.os.environ, {}, clear=True):
            agent = self.stock_agent.create_stock_agent()

        self.assertEqual(agent.kwargs["model"], "us.amazon.nova-lite-v1:0")
        self.assertIn("Knowledge Base", agent.kwargs["system_prompt"])
        self.assertIn("`retrieve` 호출 없이", agent.kwargs["system_prompt"])
        self.assertIn("시장 전체를 묻는 질문은", agent.kwargs["system_prompt"])
        self.assertIn("임의의 종목 조회용으로 사용하지 않습니다", agent.kwargs["system_prompt"])
        self.assertIn("일반론만 나열하지 않습니다", agent.kwargs["system_prompt"])
        self.assertIn("최종 투자 결정과 그 결과에 대한 책임", agent.kwargs["system_prompt"])

        tools = agent.kwargs["tools"]
        self.assertIn(self.stock_agent.retrieve, tools)
        self.assertIn(self.stock_agent.tavily_search, tools)
        self.assertIn(self.stock_agent.fmp_get_stock_data, tools)

    def test_build_turn_prompt_enforces_retrieve_first_per_turn(self):
        prompt = self.stock_agent.build_turn_prompt("오늘 한국 증시 어때?")

        self.assertIn("새로운 투자 분석 요청", prompt)
        self.assertIn("첫 번째 도구 호출은 `retrieve`", prompt)
        self.assertIn("Tavily 또는 FMP를 먼저 사용했더라도", prompt)
        self.assertIn("오늘 한국 증시 어때?", prompt)

    def test_create_stock_agent_uses_apac_nova_lite_profile_for_ap_region(self):
        with patch.dict(
            self.stock_agent.os.environ,
            {"AWS_REGION": "ap-northeast-2"},
            clear=True,
        ):
            agent = self.stock_agent.create_stock_agent()

        self.assertEqual(agent.kwargs["model"], "apac.amazon.nova-lite-v1:0")

    def test_create_stock_agent_uses_bedrock_model_id_from_env(self):
        with patch.dict(
            self.stock_agent.os.environ,
            {"BEDROCK_MODEL_ID": "anthropic.claude-3-5-sonnet-20241022-v2:0"},
            clear=True,
        ):
            agent = self.stock_agent.create_stock_agent()

        self.assertEqual(
            agent.kwargs["model"],
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
        )

    def test_streamlit_app_imports_with_stubbed_runtime(self):
        install_streamlit_stub()
        sys.modules.pop("chat_app", None)

        chat_app = importlib.import_module("chat_app")

        self.assertIn("stock_agent", chat_app.st.session_state)
        tools = chat_app.st.session_state["stock_agent"].kwargs["tools"]
        self.assertIn(self.stock_agent.retrieve, tools)
        self.assertIn(self.stock_agent.tavily_search, tools)
        self.assertIn(self.stock_agent.fmp_get_stock_data, tools)

    def test_streamlit_app_removes_thinking_tags_from_agent_reply(self):
        install_streamlit_stub()
        sys.modules.pop("chat_app", None)

        chat_app = importlib.import_module("chat_app")

        raw_reply = "<thinking>hidden chain</thinking>\n최종 답변"

        self.assertEqual(chat_app.clean_agent_reply(raw_reply), "최종 답변")

    def test_streamlit_app_summarizes_reasoning_without_hidden_chain(self):
        install_streamlit_stub()
        sys.modules.pop("chat_app", None)

        chat_app = importlib.import_module("chat_app")

        summary = chat_app.summarize_reasoning_path("삼성전자 분석해줘")

        self.assertIn("내부 사고 원문은 표시하지 않고", summary)
        self.assertIn("Knowledge Base", summary)
        self.assertIn("삼성전자 분석해줘", summary)

    def test_load_app_env_removes_blank_aws_profile(self):
        env = importlib.import_module("genfinance.env")

        with patch.object(env, "load_dotenv", lambda: None):
            with patch.dict(env.os.environ, {"AWS_PROFILE": ""}, clear=True):
                env.load_app_env()

                self.assertNotIn("AWS_PROFILE", env.os.environ)

    def test_load_app_env_keeps_named_aws_profile(self):
        env = importlib.import_module("genfinance.env")

        with patch.object(env, "load_dotenv", lambda: None):
            with patch.dict(env.os.environ, {"AWS_PROFILE": "demo"}, clear=True):
                env.load_app_env()

                self.assertEqual(env.os.environ["AWS_PROFILE"], "demo")

    def test_load_app_env_mirrors_aws_region_to_default_region(self):
        env = importlib.import_module("genfinance.env")

        with patch.object(env, "load_dotenv", lambda: None):
            with patch.dict(env.os.environ, {"AWS_REGION": "us-east-1"}, clear=True):
                env.load_app_env()

                self.assertEqual(env.os.environ["AWS_DEFAULT_REGION"], "us-east-1")

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

    def test_fmp_converts_korean_company_name_to_krx_symbol(self):
        response = FakeResponse([
            {
                "companyName": "Samsung Electronics Co., Ltd.",
                "symbol": "005930.KS",
                "price": 317000,
                "industry": "Consumer Electronics",
                "description": "Memory and device maker",
            }
        ])
        requests_get = Mock(return_value=response)

        with patch.dict(self.stock_agent.os.environ, {"FMP_API_KEY": "test-key"}):
            with patch.object(self.stock_tools.requests, "get", requests_get):
                result = self.stock_agent.fmp_get_stock_data("삼성전자", "profile")

        params = requests_get.call_args.kwargs["params"]

        self.assertEqual(params["symbol"], "005930.KS")
        self.assertIn("005930.KS", result)

    def test_fmp_adds_krx_suffix_to_numeric_code(self):
        response = FakeResponse([
            {
                "companyName": "Samsung Electronics Co., Ltd.",
                "symbol": "005930.KS",
                "price": 317000,
                "industry": "Consumer Electronics",
                "description": "Memory and device maker",
            }
        ])
        requests_get = Mock(return_value=response)

        with patch.dict(self.stock_agent.os.environ, {"FMP_API_KEY": "test-key"}):
            with patch.object(self.stock_tools.requests, "get", requests_get):
                self.stock_agent.fmp_get_stock_data("005930", "price")

        params = requests_get.call_args.kwargs["params"]

        self.assertEqual(params["symbol"], "005930.KS")

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

    def test_fmp_additional_data_types_call_expected_endpoints(self):
        expected_endpoints = {
            "historical_price": "historical-price-eod/full",
            "market_cap": "market-capitalization",
            "enterprise_value": "enterprise-values",
            "ratios": "ratios-ttm",
            "key_metrics": "key-metrics-ttm",
            "income_statement": "income-statement",
            "balance_sheet": "balance-sheet-statement",
            "cash_flow": "cash-flow-statement",
        }

        for data_type, endpoint in expected_endpoints.items():
            with self.subTest(data_type=data_type):
                response = FakeResponse([{"symbol": "AAPL", "value": 100}])
                requests_get = Mock(return_value=response)

                with patch.dict(self.stock_agent.os.environ, {"FMP_API_KEY": "test-key"}):
                    with patch.object(self.stock_tools.requests, "get", requests_get):
                        result = self.stock_agent.fmp_get_stock_data("AAPL", data_type)

                requests_get.assert_called_once()
                url = requests_get.call_args.args[0]
                params = requests_get.call_args.kwargs["params"]

                self.assertEqual(url, f"https://financialmodelingprep.com/stable/{endpoint}")
                self.assertEqual(params["symbol"], "AAPL")
                self.assertEqual(params["apikey"], "test-key")
                self.assertIn("출처: FMP", result)

    def test_fmp_rejects_unsupported_data_type_before_api_call(self):
        requests_get = Mock()

        with patch.dict(self.stock_agent.os.environ, {"FMP_API_KEY": "test-key"}):
            with patch.object(self.stock_tools.requests, "get", requests_get):
                result = self.stock_agent.fmp_get_stock_data("AAPL", "dividends")

        requests_get.assert_not_called()
        self.assertIn("지원하지 않는 data_type", result)


if __name__ == "__main__":
    unittest.main()
