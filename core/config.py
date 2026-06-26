# core/config.py

import os


def get_secret(key: str) -> str:
    """
    Get secret from environment variables, Streamlit secrets,
    or .env file. Works in Streamlit, FastAPI, and local contexts.
    """
    value = os.getenv(key, "")
    if value:
        return value

    try:
        import streamlit as st
        value = st.secrets.get(key, "")
        if value:
            os.environ[key] = value
            return value
    except Exception:
        pass

    try:
        from dotenv import load_dotenv
        load_dotenv()
        value = os.getenv(key, "")
        if value:
            os.environ[key] = value
            return value
    except Exception:
        pass

    return ""


GROQ_API_KEY = get_secret("GROQ_API_KEY")
HF_TOKEN = get_secret("HF_TOKEN")
EMAIL_ADDRESS = get_secret("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = get_secret("EMAIL_APP_PASSWORD")