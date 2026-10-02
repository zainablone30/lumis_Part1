import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(__file__))
from auth import ProfessionalAuth
from consent_linking import ConsentLinker
from aggregation_service import AggregationService

st.set_page_config(page_title="LUMIS Professional Dashboard", layout="wide")

auth = ProfessionalAuth()
linker = ConsentLinker()
agg = AggregationService()

if "professional" not in st.session_state:
    st.session_state.professional = None

# ---------------- LOGIN ----------------
if st.session_state.professional is None:
    st.title("🔒 LUMIS Professional Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = auth.login(email, password)
        if user:
            st.session_state.professional = user
            st.rerun()
        else:
            st.error("Invalid credentials.")
    st.stop()

# ---------------- DASHBOARD ----------------
prof = st.session_state.professional
st.sidebar.success(f"Logged in as {prof['name']} ({prof['role']})")

clients = linker.get_consented_clients(prof["id"])
if not clients:
    st.warning("No clients have granted consent to share their progress with you yet.")
    st.stop()

selected_client = st.sidebar.selectbox("Select client (consented only)", clients)

st.title(f"📊 Progress Overview — {selected_client}")
st.caption("All data shown is aggregated and anonymized. Raw conversation content is never visible here.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Emotional State Distribution (last 30 days)")
    emo_data = agg.emotion_trend(selected_client)
    if emo_data:
        df = pd.DataFrame(list(emo_data.items()), columns=["Emotion", "Percentage"])
        st.plotly_chart(px.pie(df, names="Emotion", values="Percentage"), use_container_width=True)
    else:
        st.info("No emotion data available yet.")

with col2:
    st.subheader("Physiological Stress Trend")
    stress_data = agg.physiological_trend(selected_client)
    if stress_data:
        df = pd.DataFrame(stress_data)
        st.plotly_chart(px.line(df, x="date", y="stress_score", color="stress_level"),
                         use_container_width=True)
    else:
        st.info("No physiological data available yet.")

st.subheader("Communication Practice Progress")
comm_data = agg.communication_progress(selected_client)
if comm_data:
    for scenario, points in comm_data.items():
        st.markdown(f"**{scenario.replace('_', ' ').title()}**")
        df = pd.DataFrame(points)
        st.plotly_chart(px.line(df, x="date", y="clarity_score", markers=True,
                                 title=f"Clarity score over sessions — {scenario}"),
                         use_container_width=True)
else:
    st.info("No communication practice sessions recorded yet.")

st.subheader("Home Monitoring Alert Summary")
alerts = agg.alert_summary(selected_client)
if alerts:
    st.table(pd.DataFrame(list(alerts.items()), columns=["Alert Type:Severity", "Count"]))
else:
    st.info("No alerts recorded.")