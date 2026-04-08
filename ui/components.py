from __future__ import annotations

import streamlit as st


def inject_saas_styles() -> None:
    st.markdown(
        """
        <style>
        /* Card styling for Streamlit containers */
        /* Use !important because Streamlit theme CSS can override ours. */
        div[data-testid="stVerticalBlock"]{
            background: #ffffff !important;
            border-radius: 14px !important;
            border: 1px solid #ececec !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.06) !important;
            padding: 16px !important;
            margin-bottom: 14px !important;
            color: #111111 !important;
        }

        /* Ensure bordered containers look consistent */
        div.block-container{
            background: transparent;
        }

        /* Force readable text inside our “card” blocks */
        div[data-testid="stVerticalBlock"] *{
            color: #111111 !important;
        }

        /* But if the background is dark (e.g., Streamlit buttons), keep labels white */
        div[data-testid="stVerticalBlock"] button,
        div[data-testid="stVerticalBlock"] [role="button"],
        div[data-testid="stVerticalBlock"] [data-baseweb="button"]{
            color: #ffffff !important;
        }

        /* Streamlit button text is often inside spans; force it too */
        div[data-testid="stVerticalBlock"] button *,
        div[data-testid="stVerticalBlock"] [role="button"] *,
        div[data-testid="stVerticalBlock"] [data-baseweb="button"] *{
            color: #ffffff !important;
        }

        /* Fix sidebar dark form controls (inputs/selects) where text was becoming black */
        div[data-testid="stVerticalBlock"] input,
        div[data-testid="stVerticalBlock"] textarea,
        div[data-testid="stVerticalBlock"] select{
            color: #ffffff !important;
        }

        /* BaseWeb select (Streamlit selectbox) */
        div[data-testid="stVerticalBlock"] [data-baseweb="select"] *{
            color: #ffffff !important;
        }

        .ai-card {
            padding: 16px;
            border-radius: 14px;
            background: #ffffff;
            box-shadow: 0 2px 10px rgba(0,0,0,0.06);
            border: 1px solid #ececec;
        }
        .ai-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def card_begin(title: str) -> None:
    st.markdown(f'<div class="ai-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-title">{title}</div>', unsafe_allow_html=True)


def card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)

