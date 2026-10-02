# frontend_dashboard/app.py
import streamlit as st
import requests

API = "http://localhost:8000"

st.set_page_config(page_title="LUMIS Control Panel", layout="wide")
st.title("🤖 LUMIS — Software Prototype Dashboard")

tab1, tab2, tab3 = st.tabs(["💬 Companion Chat", "🎤 Communication Practice", "🏠 Home Monitoring"])

with tab1:
    user_id = st.text_input("User ID", "user_1")
    user_name = st.text_input("Your name", "Zainab")
    emotion = st.selectbox("Detected emotion (simulate vision/voice module)",
                            ["Neutral", "Happiness", "Sadness", "Anger", "Fear", "Surprise", "Disgust"])
    msg = st.text_area("Say something to LUMIS")
    if st.button("Send"):
        resp = requests.post(f"{API}/companion/chat", json={
            "user_id": user_id, "user_name": user_name,
            "message": msg, "detected_emotion": emotion
        }).json()
        st.write("**LUMIS:**", resp["reply"])
        if resp["crisis_flag"]:
            st.error("⚠️ Crisis language detected — helpline info shown to user.")

with tab2:
    scenario = st.selectbox("Scenario", ["interview", "presentation", "workplace_discussion", "difficult_conversation"])
    if st.button("Start Scenario"):
        resp = requests.post(f"{API}/practice/start", json={"user_id": "user_1", "scenario_key": scenario}).json()
        st.session_state["session_id"] = resp["session_id"]
        st.write("**LUMIS:**", resp["opening_line"])

    user_turn = st.text_input("Your response")
    if st.button("Submit turn") and "session_id" in st.session_state:
        resp = requests.post(f"{API}/practice/turn", json={
            "session_id": st.session_state["session_id"], "user_text": user_turn
        }).json()
        st.write("**LUMIS:**", resp["reply"])

with tab3:
    consent = st.checkbox("I consent to Home Monitoring Mode")
    if st.button("Update Consent"):
        requests.post(f"{API}/monitoring/consent", json={"user_id": "user_1", "consent": consent})
        st.success(f"Monitoring consent set to {consent}")

    if st.button("Refresh Status"):
        status = requests.get(f"{API}/monitoring/status").json()
        st.json(status)

    if st.button("View Alert History"):
        alerts = requests.get(f"{API}/monitoring/alerts").json()
        st.table(alerts)