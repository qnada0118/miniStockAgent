# chat_app.py
import streamlit as st
from dotenv import load_dotenv
import uuid
import re
import html

from strands import Agent
from strands_tools import retrieve
from stock_agent import STOCK_AGENT_PROMPT, tavily_search, fmp_get_stock_data, get_stock_info
from chat_style import apply_styles 


st.set_page_config(page_title="Chat Demo", page_icon="💬")
load_dotenv()
apply_styles()


# -------------------------------------------
# 초기 세션 상태 생성
# -------------------------------------------

# 전체 저장된 대화 세션
if "chat_sessions" not in st.session_state:
    st.session_state["chat_sessions"] = {} 

# 현재 활성 세션 ID
if "current_session" not in st.session_state:
    new_id = str(uuid.uuid4())[:8]
    st.session_state["current_session"] = new_id
    st.session_state["chat_sessions"][new_id] = {
        "title": "새 대화",
        "messages": []
    }

current_id = st.session_state["current_session"]
current_chat = st.session_state["chat_sessions"][current_id]

# 답변 대기 상태 관련 플래그
if "awaiting_response" not in st.session_state:
    st.session_state["awaiting_response"] = False

if "pending_user_input" not in st.session_state:
    st.session_state["pending_user_input"] = None

# -------------------------------------------
# Agent 생성
# -------------------------------------------
if "stock_agent" not in st.session_state:
    st.session_state["stock_agent"] = Agent(
        model="us.amazon.nova-lite-v1:0",
        system_prompt=STOCK_AGENT_PROMPT,
        tools=[retrieve, tavily_search, fmp_get_stock_data, get_stock_info],
    )

# -------------------------------------------
# 메인 타이틀 + 대화 제목 (최상단 고정)
# -------------------------------------------
st.title("Chat with 주식 투자 어드바이저")

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
st.sidebar.header("이전 대화")

for sid, data in st.session_state["chat_sessions"].items():
    if st.sidebar.button(data["title"], key=sid, use_container_width=True):
        st.session_state["current_session"] = sid
        st.session_state["awaiting_response"] = False
        st.session_state["pending_user_input"] = None
        st.rerun()

if st.sidebar.button("➕ 새 대화 시작", use_container_width=True):
    new_id = str(uuid.uuid4())[:8]
    st.session_state["chat_sessions"][new_id] = {
        "title": f"새 대화 {len(st.session_state['chat_sessions'])}",
        "messages": []
    }
    st.session_state["current_session"] = new_id
    st.session_state["awaiting_response"] = False
    st.session_state["pending_user_input"] = None
    st.rerun()

# -------------------------------------------
# 1) 항상: 지금까지 메시지 한 번만 렌더
# -------------------------------------------
with chat_container:
    for msg in current_chat["messages"]:
        role = msg["role"]
        safe_text = html.escape(msg["content"])

        if role == "user":
            with st.chat_message("user"):
                st.markdown(
                    f"""
                    <div class="chat-row user">
                        <div class="bubble bubble-user">{safe_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            with st.chat_message("assistant"):
                st.markdown(
                    f"""
                    <div class="chat-row assistant">
                        <div class="bubble bubble-assistant">{safe_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )



# -------------------------------------------
# 2) 상태에 따라 분기
# -------------------------------------------

# (A) 아직 답변을 기다리는 중이 아님 → 새 입력 받기
if not st.session_state["awaiting_response"]:
    user_input = st.chat_input("질문을 입력하세요")

    if user_input:
        current_chat["messages"].append(
            {"role": "user", "content": user_input}
        )
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
                        result = agent(pending)  # AgentResult 객체

                        if hasattr(result, "final_output") and isinstance(result.final_output, str):
                            raw_reply = result.final_output
                        else:
                            raw_reply = str(result)

                        # <thinking> 제거
                        cleaned_reply = re.sub(
                            r"<thinking>.*?</thinking>",
                            "",
                            raw_reply,
                            flags=re.DOTALL
                        ).strip()

                        bot_reply = cleaned_reply if cleaned_reply else raw_reply

                    except Exception as e:
                        bot_reply = f"오류가 발생했습니다: {e}"

                    safe_text = html.escape(bot_reply)
                    st.markdown(
                        f"""
                        <div class="chat-row assistant">
                            <div class="chat-avatar">🤖</div>
                            <div class="bubble bubble-assistant">{safe_text}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # assistant 메시지 state에 추가
        current_chat["messages"].append(
            {"role": "assistant", "content": bot_reply}
        )
        st.session_state["chat_sessions"][current_id] = current_chat

    st.session_state["pending_user_input"] = None
    st.session_state["awaiting_response"] = False

    st.rerun()
