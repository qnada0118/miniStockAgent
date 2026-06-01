import streamlit as st

def apply_styles():
    st.markdown(
        """
        <style>
        :root {
            --chat-bg: #f6f7fb;
            --chat-panel: #ffffff;
            --chat-text: #151923;
            --chat-muted: #667085;
            --chat-border: #e6e8ef;
            --chat-user: #2563eb;
            --chat-user-dark: #1d4ed8;
            --chat-assistant: #ffffff;
            --chat-font-size: 0.92rem;
            --chat-small-font-size: 0.88rem;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.10), transparent 30rem),
                linear-gradient(180deg, #ffffff 0%, var(--chat-bg) 100%);
        }

        section.main > div {
            max-width: 920px;
            padding-top: 2.4rem;
        }

        h1 {
            color: var(--chat-text) !important;
            font-weight: 800 !important;
            letter-spacing: 0 !important;
            margin-bottom: 0.3rem !important;
        }

        label {
            color: var(--chat-muted) !important;
            font-weight: 650 !important;
        }

        div[data-testid="stTextInput"] input {
            border: 1px solid var(--chat-border) !important;
            border-radius: 12px !important;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04) !important;
        }

        section[data-testid="stSidebar"] {
            background: #fbfcff;
            border-right: 1px solid var(--chat-border);
        }

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            color: var(--chat-text);
        }

        section[data-testid="stSidebar"] button {
            border-radius: 10px !important;
            border: 1px solid transparent !important;
            transition: background 140ms ease, border-color 140ms ease, transform 140ms ease;
        }

        section[data-testid="stSidebar"] button:hover {
            border-color: var(--chat-border) !important;
            background: #ffffff !important;
            transform: translateY(-1px);
        }

        .bubble {
            padding: 0.72rem 0.95rem;
            border-radius: 20px;
            max-width: min(74%, 680px);
            font-size: var(--chat-font-size);
            line-height: 1.56;
            margin: 0.18rem 0;
            word-break: break-word;
            overflow-wrap: anywhere;
            box-shadow: 0 12px 28px rgba(16, 24, 40, 0.09);
        }

        .bubble-assistant {
            background: var(--chat-assistant) !important;
            color: var(--chat-text) !important;
            border: 1px solid var(--chat-border);
            border-bottom-left-radius: 6px;
        }

        .bubble-user {
            background: linear-gradient(135deg, var(--chat-user), var(--chat-user-dark)) !important;
            color: #ffffff !important;
            border-bottom-right-radius: 6px;
            box-shadow: 0 12px 26px rgba(37, 99, 235, 0.22);
        }

        .chat-row {
            display: flex;
            align-items: flex-end;
            margin: 0.55rem 0;
        }

        .chat-row.assistant {
            justify-content: flex-start;
        }

        .chat-row.user {
            justify-content: flex-end;
        }

        div[data-testid="stChatMessage"] {
            background-color: transparent !important;
            border: none !important;
            padding: 0.25rem 0 !important;
        }

        div[data-testid="stChatMessage"] > div:first-child {
            align-self: flex-start !important;
            margin-top: 0.25rem !important;
        }

        div[data-testid="stChatMessage"] > div:first-child div {
            background: #eef2ff !important;
            color: var(--chat-user-dark) !important;
        }

        div[data-testid="stChatMessage"] > div:nth-child(2) {
            max-width: min(82%, 720px) !important;
            background: var(--chat-assistant);
            color: var(--chat-text);
            border: 1px solid var(--chat-border);
            border-radius: 20px;
            border-bottom-left-radius: 6px;
            padding: 1.08rem 1.22rem 1.5rem !important;
            font-size: var(--chat-font-size);
            line-height: 1.62;
            box-shadow: 0 14px 34px rgba(16, 24, 40, 0.08);
        }

        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
            font-size: var(--chat-font-size);
            line-height: 1.62;
        }

        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 {
            color: var(--chat-text) !important;
            letter-spacing: 0 !important;
            line-height: 1.28 !important;
            margin: 1.1rem 0 0.55rem !important;
        }

        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1 {
            font-size: 1.22rem !important;
            font-weight: 780 !important;
        }

        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2 {
            font-size: 1.12rem !important;
            font-weight: 760 !important;
        }

        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 {
            font-size: 1.02rem !important;
            font-weight: 740 !important;
        }

        div[data-testid="stChatMessage"] p:first-child {
            margin-top: 0;
        }

        div[data-testid="stChatMessage"] p:last-child {
            margin-bottom: 0.35rem;
        }

        div[data-testid="stChatMessage"] p {
            margin: 0.35rem 0 0.7rem;
        }

        div[data-testid="stChatMessage"] ul,
        div[data-testid="stChatMessage"] ol {
            margin: 0.35rem 0 0.8rem;
            padding-left: 1.25rem;
        }

        div[data-testid="stChatMessage"] li {
            margin: 0.34rem 0;
            padding-left: 0.12rem;
            line-height: 1.58;
        }

        div[data-testid="stChatMessage"] table {
            width: 100%;
            border-collapse: collapse;
            border-radius: 10px;
            overflow: hidden;
            font-size: var(--chat-small-font-size);
        }

        div[data-testid="stChatMessage"] th,
        div[data-testid="stChatMessage"] td {
            padding: 0.45rem 0.6rem;
            border: 1px solid var(--chat-border);
            vertical-align: top;
        }

        div[data-testid="stChatMessage"] th {
            background: #f8fafc;
            font-weight: 700;
        }

        div[data-testid="stChatMessage"] a {
            word-break: break-word;
        }

        div[data-testid="stChatMessage"] code {
            font-size: 0.86em;
            border-radius: 6px;
            padding: 0.12rem 0.3rem;
        }

        div[data-testid="stChatMessage"] pre {
            border-radius: 12px;
            border: 1px solid var(--chat-border);
        }

        div[data-testid="stChatInput"] {
            background: rgba(246, 247, 251, 0.86);
            backdrop-filter: blur(8px);
            border-top: 1px solid rgba(230, 232, 239, 0.72);
        }

        div[data-baseweb="textarea"] > textarea {
            border-radius: 999px !important;
            font-size: 0.95rem !important;
            border: 1px solid var(--chat-border) !important;
            box-shadow: 0 8px 24px rgba(16, 24, 40, 0.08) !important;
            padding-left: 1rem !important;
        }

        @media (max-width: 640px) {
            section.main > div {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .bubble,
            div[data-testid="stChatMessage"] > div:nth-child(2) {
                max-width: 88% !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
