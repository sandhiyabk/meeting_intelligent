# core/config.py

import os

def get_secret(key: str) -> str:
    """
    Get secret from Streamlit secrets (cloud)
    or .env file (local development).
    Works in both environments automatically.
    """
    try:
        import streamlit as st
        return st.secrets[key]
    except Exception:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(key, "")


# Ready-to-use variables
GROQ_API_KEY = get_secret("GROQ_API_KEY")
HF_TOKEN = get_secret("HF_TOKEN")
EMAIL_ADDRESS = get_secret("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = get_secret("EMAIL_APP_PASSWORD")