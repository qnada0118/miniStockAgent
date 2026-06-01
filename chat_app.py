# chat_app.py
import streamlit as st
import uuid
import re
import html
import base64
from datetime import datetime
from pathlib import Path

from stock_agent import build_turn_prompt, create_stock_agent
from genfinance.env import load_app_env
from ui.chat_style import apply_styles


DEFAULT_CHAT_TITLE = "새 대화"
UNTITLED_CHAT_TITLE = "제목 없는 대화"
LOGO_SVG_PATH = Path(__file__).parent / "ui" / "assets" / "genfinance_logo.svg"


st.set_page_config(page_title="GenFinance", page_icon="💬")
load_app_env()
apply_styles()


def load_logo_img() -> str:
    try:
        logo_data = base64.b64encode(LOGO_SVG_PATH.read_bytes()).decode("ascii")
        return f'<img src="data:image/svg+xml;base64,{logo_data}" alt="GenFinance logo" />'
    except OSError:
        return '<div class="logo-fallback">GenFinance</div>'


def log_to_terminal(label: str, content: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] {label}")
    print("-" * 60)
    print(content)
    print("-" * 60, flush=True)


def summarize_reasoning_path(user_input: str) -> str:
    return "\n".join(
        [
            "내부 사고 원문은 표시하지 않고, 확인 가능한 처리 기준만 요약합니다.",
            f"1. 사용자 질문 확인: {user_input}",
            "2. 투자 관련 질문이면 Knowledge Base 검색을 우선 사용합니다.",
            "3. 최신 뉴스/정량 데이터가 필요하면 Tavily 또는 FMP 도구 결과를 보조 근거로 사용합니다.",
            "4. 최종 답변은 출처, 긍정 요인, 리스크, 투자 유의사항을 중심으로 정리합니다.",
        ]
    )


def clean_agent_reply(raw_reply: str) -> str:
    cleaned_reply = re.sub(
        r"<thinking>.*?</thinking>",
        "",
        raw_reply,
        flags=re.DOTALL,
    ).strip()

    return cleaned_reply if cleaned_reply else raw_reply


def render_user_message(content: str) -> None:
    escaped = html.escape(content).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="chat-row user">
            <div class="bubble bubble-user">{escaped}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_chat_session(title=None) -> dict:
    return {
        "title": title or DEFAULT_CHAT_TITLE,
        "messages": [],
    }


def reset_pending_response() -> None:
    st.session_state["awaiting_response"] = False
    st.session_state["pending_user_input"] = None


def start_new_chat() -> None:
    new_id = str(uuid.uuid4())[:8]
    chat_count = len(st.session_state["chat_sessions"])
    st.session_state["chat_sessions"][new_id] = create_chat_session(
        title=f"{DEFAULT_CHAT_TITLE} {chat_count}"
    )
    st.session_state["current_session"] = new_id
    reset_pending_response()
    st.rerun()


def switch_chat(session_id: str) -> None:
    st.session_state["current_session"] = session_id
    reset_pending_response()
    st.rerun()


def get_display_title(chat: dict) -> str:
    return chat["title"].strip() or UNTITLED_CHAT_TITLE


def format_chat_button_label(chat: dict) -> str:
    return f"{get_display_title(chat)} ({len(chat['messages'])})"


def initialize_session_state() -> None:
    if "chat_sessions" not in st.session_state:
        st.session_state["chat_sessions"] = {}

    if "current_session" not in st.session_state:
        new_id = str(uuid.uuid4())[:8]
        st.session_state["current_session"] = new_id
        st.session_state["chat_sessions"][new_id] = create_chat_session()

    if "awaiting_response" not in st.session_state:
        st.session_state["awaiting_response"] = False

    if "pending_user_input" not in st.session_state:
        st.session_state["pending_user_input"] = None

    if "stock_agent" not in st.session_state:
        st.session_state["stock_agent"] = create_stock_agent()


def render_app_header() -> None:
    logo_img = load_logo_img()
    st.markdown(
        f"""
        <div class="app-hero">
            <div class="hero-logo">{logo_img}</div>
            <p class="app-kicker">AI Stock Research Assistant</p>
            <p class="app-subtitle">시장 데이터, 뉴스, 리서치 근거를 함께 보는 주식 투자 어드바이저</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(current_id: str, current_chat: dict) -> None:
    logo_img = load_logo_img()
    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="sidebar-logo">{logo_img}</div>
            <div class="sidebar-caption">Investment chats</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        '<div class="sidebar-section-title">채팅방</div>',
        unsafe_allow_html=True,
    )

    for session_id, chat in st.session_state["chat_sessions"].items():
        if st.sidebar.button(
            format_chat_button_label(chat),
            key=session_id,
            use_container_width=True,
            disabled=session_id == current_id,
        ):
            switch_chat(session_id)

    st.sidebar.markdown('<div class="sidebar-new-chat">', unsafe_allow_html=True)
    if st.sidebar.button("새 대화 시작", use_container_width=True):
        start_new_chat()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)


def render_messages(chat: dict) -> None:
    for message in chat["messages"]:
        if message["role"] == "user":
            render_user_message(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])


def extract_agent_reply(result) -> str:
    if hasattr(result, "final_output") and isinstance(result.final_output, str):
        return result.final_output
    return str(result)


def append_message(chat: dict, role: str, content: str) -> None:
    chat["messages"].append({"role": role, "content": content})


initialize_session_state()

current_id = st.session_state["current_session"]
current_chat = st.session_state["chat_sessions"][current_id]

# -------------------------------------------
# 메인 타이틀 + 대화 제목 (최상단 고정)
# -------------------------------------------
render_app_header()

current_title = st.text_input(
    "대화 제목",
    value=current_chat["title"],
    key=f"title_{current_id}",
)
current_chat["title"] = current_title

# 채팅 영역 컨테이너
chat_container = st.container()

# -------------------------------------------
# Sidebar: 이전 대화 목록
# -------------------------------------------
render_sidebar(current_id, current_chat)

# -------------------------------------------
# 1) 항상: 지금까지 메시지 한 번만 렌더
# -------------------------------------------
with chat_container:
    render_messages(current_chat)

# -------------------------------------------
# 2) 상태에 따라 분기
# -------------------------------------------

# (A) 아직 답변을 기다리는 중이 아님 → 새 입력 받기
if not st.session_state["awaiting_response"]:
    user_input = st.chat_input("질문을 입력하세요")

    if user_input:
        log_to_terminal("사용자 입력", user_input)
        log_to_terminal("처리 기준 요약", summarize_reasoning_path(user_input))

        append_message(current_chat, "user", user_input)
        st.session_state["chat_sessions"][current_id] = current_chat

        st.session_state["pending_user_input"] = user_input
        st.session_state["awaiting_response"] = True

        st.rerun()

# (B) 답변을 기다리는 중 → LLM 호출 + 답변 추가
else:
    pending = st.session_state["pending_user_input"]

    if pending:
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("🔍 분석 중..."):
                    try:
                        agent = st.session_state["stock_agent"]
                        result = agent(build_turn_prompt(pending))  # AgentResult 객체
                        raw_reply = extract_agent_reply(result)
                        bot_reply = clean_agent_reply(raw_reply)

                    except Exception as e:
                        bot_reply = f"오류가 발생했습니다: {e}"
                        log_to_terminal("에이전트 오류", bot_reply)

                    st.markdown(bot_reply)

        # assistant 메시지 state에 추가
        append_message(current_chat, "assistant", bot_reply)
        st.session_state["chat_sessions"][current_id] = current_chat

    st.session_state["pending_user_input"] = None
    st.session_state["awaiting_response"] = False

    st.rerun()
