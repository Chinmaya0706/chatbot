from dotenv import load_dotenv
import streamlit as st
import os

def get_api_key():
    try:
        api_key = None
        if "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
        # 2. If not found, fall back to environment variables (for local development with .env)
        else:
            st.error("No API key is present")
    except Exception as e:
            load_dotenv() # Load the .env file contents
            api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        st.error("🔑 API Key Missing! Please set GOOGLE_API_KEY in .env or Streamlit Secrets.")
        st.stop()
    
    return api_key