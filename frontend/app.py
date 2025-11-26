import os
import requests
import streamlit as st

API = os.getenv("IR_API", "http://localhost:8008")

st.title("IR Downloader")

if "latest_response" not in st.session_state:
    st.session_state["latest_response"] = None
if "settings_status" not in st.session_state:
    st.session_state["settings_status"] = None

def refresh_settings_status():
    try:
        resp = requests.get(f"{API}/settings", timeout=10)
        resp.raise_for_status()
        st.session_state["settings_status"] = resp.json()
    except requests.RequestException as e:
        st.warning(f"Unable to fetch settings: {e}")

if st.session_state["settings_status"] is None:
    refresh_settings_status()

prompt_text = st.text_input(
    "Prompt",
    value="",
    placeholder="Download the latest annual report of Apple",
)
ticker = st.text_input("Company ticker", "", placeholder="e.g., AAPL").strip().upper()

with st.popover("⚙️ Manage API keys"):
    status = st.session_state.get("settings_status") or {}
    st.write("Current status (masked):")
    st.json(status)

    st.markdown("Update any value below (leave blank to keep the existing one).")
    with st.form("settings_form"):
        new_openai = st.text_input("OpenAI API Key", type="password")
        new_tavily = st.text_input("Tavily API Key", type="password")
        new_google = st.text_input("Google API Key", type="password")
        new_cse = st.text_input("Google CSE ID", type="password")
        new_provider = st.selectbox("Default provider", ["", "openai", "gemini"])
        submitted = st.form_submit_button("Save settings")

        if submitted:
            payload = {}
            if new_openai:
                payload["openai_api_key"] = new_openai
            if new_tavily:
                payload["tavily_api_key"] = new_tavily
            if new_google:
                payload["google_api_key"] = new_google
            if new_cse:
                payload["google_cse_id"] = new_cse
            if new_provider:
                payload["default_provider"] = new_provider

            if not payload:
                st.warning("Enter at least one value to update.")
            else:
                try:
                    resp = requests.post(f"{API}/settings", json=payload, timeout=10)
                    resp.raise_for_status()
                    st.success(f"Updated: {', '.join(resp.json().get('updated', []))}")
                    refresh_settings_status()
                except requests.RequestException as e:
                    st.error(f"Failed to update settings: {e}")

run_disabled = not prompt_text.strip()
if st.button("Run", disabled=run_disabled):
    if not prompt_text.strip():
        st.warning("Please enter a prompt describing the document you need.")
    else:
        with st.spinner("Fetching documents..."):
            try:
                payload = {
                    "prompt": prompt_text.strip(),
                }
                if ticker:
                    payload["ticker"] = ticker
                r = requests.post(f"{API}/download", json=payload, timeout=300)
                r.raise_for_status()
                data = r.json()
                st.session_state["latest_response"] = data
                st.success(f"Found {len(data.get('results', []))} documents.")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to download: {e}")
                if hasattr(e, "response") and e.response is not None:
                    try:
                        st.json(e.response.json() if e.response.content else {"error": str(e)})
                    except ValueError:
                        st.write(e.response.text)

if st.session_state.get("latest_response"):
    st.subheader("Results")
    response_data = st.session_state["latest_response"]
    results = response_data.get("results", [])
    if not results:
        st.info("No documents found for this request.")
    else:
        for doc in results:
            url = doc.get("url")
            url_display = f"[{url}]({url})" if url else "-"
            st.markdown(
                f"""
**company name:** {doc.get('company', '-')}  
**doc_type:** {doc.get('doc_type', '-')}  
**year:** {doc.get('year', '-')}  
**file_path:** {doc.get('file_path', '-')}  
**filename:** {doc.get('filename', '-')}  
**url:** {url_display}  
**mimetype:** {doc.get('mimetype', '-')}  
**source:** {doc.get('source', '-')}  
---
"""
            )
