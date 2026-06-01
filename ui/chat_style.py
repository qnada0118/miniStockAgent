import streamlit as st

def apply_styles():
    st.markdown(
        """
        <style>
        :root {
            --chat-bg: #05070c;
            --chat-panel: #0b1018;
            --chat-text: #f4ecd8;
            --chat-muted: #a99a72;
            --chat-border: rgba(215, 187, 116, 0.22);
            --chat-user: #d7bb74;
            --chat-user-dark: #8f6b2e;
            --chat-assistant: rgba(11, 16, 24, 0.92);
            --brand: #d7bb74;
            --brand-dark: #fff2bf;
            --brand-soft: rgba(215, 187, 116, 0.12);
            --accent: #f1e7cb;
            --chat-font-size: 0.92rem;
            --chat-small-font-size: 0.88rem;
        }

        .stApp {
            background:
                radial-gradient(circle at 14% 0%, rgba(215, 187, 116, 0.13), transparent 31rem),
                radial-gradient(circle at 92% 4%, rgba(28, 36, 50, 0.82), transparent 28rem),
                linear-gradient(180deg, #0b1018 0%, var(--chat-bg) 100%);
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

        .app-hero {
            padding: 0.2rem 0 1.15rem;
            border-bottom: 1px solid rgba(215, 187, 116, 0.12);
        }

        .hero-logo {
            width: min(100%, 31rem);
            margin-bottom: 0.55rem;
        }

        .hero-logo img {
            display: block;
            width: 100%;
            height: auto;
        }

        .app-kicker {
            display: inline-flex;
            align-items: center;
            margin: 0 0 0.48rem;
            padding: 0.28rem 0.62rem;
            border: 1px solid rgba(215, 187, 116, 0.3);
            border-radius: 999px;
            background: rgba(215, 187, 116, 0.1);
            color: var(--brand-dark);
            font-size: 0.76rem;
            font-weight: 760;
            letter-spacing: 0.04em;
        }

        .app-subtitle {
            margin: 0.55rem 0 0;
            color: var(--chat-muted);
            font-size: 0.96rem;
            line-height: 1.5;
        }

        label {
            color: var(--chat-muted) !important;
            font-weight: 650 !important;
        }

        div[data-testid="stTextInput"] input {
            border: 1px solid rgba(215, 187, 116, 0.18) !important;
            border-radius: 12px !important;
            background: rgba(11, 16, 24, 0.88) !important;
            color: var(--chat-text) !important;
            box-shadow: none !important;
            outline: none !important;
        }

        div[data-testid="stTextInput"] input:focus {
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }

        div[data-testid="stTextInput"] [data-baseweb="input"] {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top left, rgba(215, 187, 116, 0.16), transparent 18rem),
                linear-gradient(180deg, #0b1018 0%, #04060a 100%);
            border-right: 1px solid var(--chat-border);
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.35rem;
            min-height: 100vh;
        }

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            color: var(--chat-text);
        }

        .sidebar-brand {
            display: grid;
            gap: 0.35rem;
            padding: 0.6rem 0.25rem 1rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid rgba(215, 187, 116, 0.2);
        }

        .sidebar-logo {
            width: 100%;
        }

        .sidebar-logo img {
            display: block;
            width: 100%;
            height: auto;
        }

        .sidebar-caption {
            margin-left: 0.45rem;
            color: var(--chat-muted);
            font-size: 0.76rem;
            font-weight: 620;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .sidebar-section-title {
            margin: 1rem 0.25rem 0.45rem;
            color: #a99a72;
            font-size: 0.72rem;
            font-weight: 780;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        section[data-testid="stSidebar"] button {
            min-height: 2.55rem !important;
            justify-content: flex-start !important;
            border-radius: 12px !important;
            border: 1px solid rgba(215, 187, 116, 0.18) !important;
            background: rgba(12, 17, 25, 0.76) !important;
            color: #f1e7cb !important;
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.26) !important;
            transition: background 140ms ease, border-color 140ms ease, transform 140ms ease, box-shadow 140ms ease;
        }

        section[data-testid="stSidebar"] button p {
            font-size: 0.88rem;
            font-weight: 650;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        section[data-testid="stSidebar"] button:hover {
            border-color: rgba(215, 187, 116, 0.42) !important;
            background: rgba(28, 36, 50, 0.9) !important;
            box-shadow: 0 14px 28px rgba(0, 0, 0, 0.36) !important;
            transform: translateY(-1px);
        }

        .sidebar-new-chat {
            margin-top: 1.4rem;
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
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.28);
        }

        .bubble-assistant {
            background: var(--chat-assistant) !important;
            color: var(--chat-text) !important;
            border: 1px solid var(--chat-border);
            border-bottom-left-radius: 6px;
        }

        .bubble-user {
            background: linear-gradient(135deg, var(--chat-user), var(--chat-user-dark)) !important;
            color: #090d14 !important;
            border-bottom-right-radius: 6px;
            box-shadow: 0 12px 26px rgba(215, 187, 116, 0.18);
            font-weight: 650;
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
            display: flex !important;
            align-items: flex-start !important;
            gap: 0.6rem !important;
        }

        div[data-testid="stChatMessage"] > div:first-child {
            align-self: flex-start !important;
            margin-top: 0.25rem !important;
            margin-right: 0 !important;
            width: 4rem !important;
            min-width: 4rem !important;
            max-width: 4rem !important;
            flex: 0 0 4rem !important;
        }

        div[data-testid="stChatMessage"] > div:first-child div {
            background: rgba(215, 187, 116, 0.14) !important;
            color: var(--brand-dark) !important;
        }

        div[data-testid="stChatMessage"] > div:nth-child(2) {
            max-width: min(82%, 720px) !important;
            margin-left: 0 !important;
            background: var(--chat-assistant);
            color: var(--chat-text);
            border: 1px solid var(--chat-border);
            border-radius: 20px;
            border-bottom-left-radius: 6px;
            padding: 1.08rem 1.22rem 1.5rem !important;
            font-size: var(--chat-font-size);
            line-height: 1.62;
            box-shadow: 0 14px 34px rgba(0, 0, 0, 0.32);
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
            background: rgba(215, 187, 116, 0.12);
            font-weight: 700;
        }

        div[data-testid="stChatMessage"] a {
            word-break: break-word;
            color: #fff2bf;
        }

        div[data-testid="stChatMessage"] code {
            font-size: 0.86em;
            border-radius: 6px;
            padding: 0.12rem 0.3rem;
            background: rgba(241, 231, 203, 0.1);
            color: #fff2bf;
        }

        div[data-testid="stChatMessage"] pre {
            border-radius: 12px;
            border: 1px solid var(--chat-border);
            background: rgba(4, 6, 10, 0.88);
        }

        div[data-testid="stChatInput"] {
            background: rgba(5, 7, 12, 0.88);
            backdrop-filter: blur(8px);
            border-top: 1px solid rgba(215, 187, 116, 0.16);
        }

        div[data-baseweb="textarea"] > textarea {
            border-radius: 999px !important;
            font-size: 0.95rem !important;
            border: 1px solid var(--chat-border) !important;
            background: rgba(11, 16, 24, 0.96) !important;
            color: var(--chat-text) !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28) !important;
            padding-left: 1rem !important;
        }

        div[data-baseweb="textarea"] > textarea::placeholder {
            color: rgba(241, 231, 203, 0.56) !important;
        }

        .stMarkdown,
        .stTextInput,
        [data-testid="stMarkdownContainer"] {
            color: var(--chat-text);
        }

        .logo-fallback {
            color: var(--brand-dark);
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 2rem;
            font-weight: 700;
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
