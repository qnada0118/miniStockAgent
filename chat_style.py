import streamlit as st

def apply_styles():
    st.markdown(
        """
        <style>
        /* 제목 더 뚜렷하게 */
        h1 {
            color: #111 !important;
            font-weight: 800 !important;
        }

        /* 공통 말풍선 스타일 */
        .bubble {
            padding: 8px 14px;
            border-radius: 16px;
            max-width: 75%;
            line-height: 1.45;
            margin: 4px 0;
        }

        /* 어시스턴트 말풍선 */
        .bubble-assistant {
            background: #f2f2f2 !important;
            color: #111 !important;
        }

        /* 유저 말풍선 */
        .bubble-user {
            background: #0b93f6 !important;
            color: #ffffff !important;
        }

        /* 한 줄(이모지 + 말풍선) 컨테이너 */
        .chat-row {
            display: flex;
            align-items: flex-end;
            margin: 4px 0;
        }

        /* 어시스턴트: 왼쪽 정렬 */
        .chat-row.assistant {
            justify-content: flex-start;
        }

        /* 유저: 이모지+말풍선 통째로 오른쪽 정렬 */
        .chat-row.user {
            justify-content: flex-end;
        }

        /* Streamlit 기본 말풍선 배경 제거 */
        div[data-testid="stChatMessage"] {
            background-color: transparent !important;
            border: none !important;
            padding: 2px 0 !important;
        }
        /* Streamlit 기본 채팅 아바타 컬럼 숨기기 */
        div[data-testid="stChatMessage"] > div:first-child {
            display: none !important;
        }

        /* 내용 컬럼을 전체 너비로 확장 */
        div[data-testid="stChatMessage"] > div:nth-child(2) {
            width: 100% !important;
        }

        /* 입력창 둥글게 유지 */
        div[data-baseweb="textarea"] > textarea {
            border-radius: 999px !important;
            font-size: 0.95rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
