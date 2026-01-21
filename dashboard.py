import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime
import time

# -----------------------------
# Config
# -----------------------------
DB_PATH = "database/vehicle_data.db"

PREDICT_API = "http://127.0.0.1:8001/predict"
EXPLAIN_API = "http://127.0.0.1:8002/explain"
RCA_API = "http://127.0.0.1:8003/analyze"
UEBA_API = "http://127.0.0.1:8004/log"

# -----------------------------
# Helpers
# -----------------------------
def get_all_vehicle_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM vehicle_telemetry ORDER BY id DESC", conn)
    conn.close()
    return df

def predict_fault(row):
    payload = {
        "engine_temp": row["engine_temp"],
        "rpm": int(row["rpm"]),
        "speed": int(row["speed"]),
        "coolant_level": row["coolant_level"],
        "battery_voltage": row["battery_voltage"]
    }
    r = requests.post(PREDICT_API, json=payload, timeout=3)
    return r.json()

def explain_fault(row, risk):
    payload = {
        "engine_temp": row["engine_temp"],
        "rpm": int(row["rpm"]),
        "coolant_level": row["coolant_level"],
        "battery_voltage": row["battery_voltage"],
        "risk": risk
    }
    r = requests.post(EXPLAIN_API, json=payload, timeout=3)
    return r.json()

def send_rca(vehicle_id, fault_type):
    payload = {
        "vehicle_id": vehicle_id,
        "fault_type": fault_type
    }
    r = requests.post(RCA_API, json=payload, timeout=3)
    return r.json()

def log_ueba(component="dashboard"):
    payload = {"component": component}
    r = requests.post(UEBA_API, params=payload, timeout=3)
    return r.json()

# -----------------------------
# Session State
# -----------------------------
if "notifications" not in st.session_state:
    st.session_state.notifications = []

# -----------------------------
# UI Setup
# -----------------------------
st.set_page_config(page_title="Predictive Maintenance Dashboard", layout="wide")
st.title("🚗 Predictive Vehicle Maintenance Dashboard")

auto_refresh = st.toggle("🔄 Auto refresh every 5 seconds")
st.button("Manual Refresh")

# -----------------------------
# Load Data
# -----------------------------
df_all = get_all_vehicle_data()

if df_all.empty:
    st.warning("No vehicle data found yet.")
    st.stop()

vehicle_ids = df_all["vehicle_id"].unique().tolist()
selected_vehicle = st.selectbox("Select Vehicle", vehicle_ids)

row = df_all[df_all["vehicle_id"] == selected_vehicle].iloc[0]

# -----------------------------
# Prediction
# -----------------------------
prediction = predict_fault(row)
risk = prediction["risk"]

explanation = explain_fault(row, risk)
explanation_text = explanation["explanation"]

# -----------------------------
# Tabs Layout
# -----------------------------
tab1, tab2, tab3 = st.tabs(["🚗 Vehicle Data", "🧠 Prediction & Notification", "🏭 System Insights"])

# =============================
# TAB 1: Vehicle Data
# =============================
with tab1:
    st.subheader("📡 Latest Sensor Readings")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Engine Temp (°C)", row["engine_temp"])
        st.metric("RPM", row["rpm"])
        st.metric("Speed (km/h)", row["speed"])

    with col2:
        st.metric("Coolant Level", row["coolant_level"])
        st.metric("Battery Voltage (V)", row["battery_voltage"])
        st.metric("Timestamp", row["timestamp"])

    st.subheader("📊 Recent Sensor Trends (last 20 records)")
    history = df_all[df_all["vehicle_id"] == selected_vehicle].head(20)
    st.line_chart(history[["engine_temp", "rpm", "battery_voltage"]])

# =============================
# TAB 2: Prediction + Notification
# =============================
with tab2:
    st.subheader("🧠 ML Prediction Result")

    if risk == "HIGH":
        st.error("⚠ HIGH RISK of vehicle fault detected")
        risk_value = 90
    else:
        st.success("✅ LOW risk – vehicle healthy")
        risk_value = 20

    st.progress(risk_value)
    st.caption("Low ←────────────→ High")

    st.subheader("💬 Explanation for Driver")
    st.info(explanation_text)

    st.subheader("📱 Driver Notification (Mock Push System)")

    if risk == "HIGH":
        if st.button("📤 Send to Driver (Mock Push Notification)"):
            notification = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "vehicle": selected_vehicle,
                "message": explanation_text
            }
            st.session_state.notifications.insert(0, notification)
            st.toast("📱 Driver notification sent successfully!", icon="📨")
    else:
        st.info("No notification sent when risk is LOW")

    if st.session_state.notifications:
        st.markdown("### 🧾 Notification History")
        for n in st.session_state.notifications[:5]:
            st.write(f"🕒 {n['time']} | 🚗 {n['vehicle']} | {n['message']}")

# =============================
# TAB 3: RCA + UEBA
# =============================
with tab3:
    st.subheader("🛠 RCA / CAPA Analysis")

    fault_type = "OVERHEATING" if row["engine_temp"] > 100 else "GENERAL_FAULT"
    rca_result = send_rca(selected_vehicle, fault_type)

    if "rca" in rca_result:
        st.warning(f"**RCA:** {rca_result['rca']}")
        st.success(f"**CAPA:** {rca_result['capa']}")
    else:
        st.write(rca_result["message"])

    st.subheader("🔐 UEBA Security Monitoring")

    ueba_result = log_ueba()

    if "alert" in ueba_result:
        st.error(f"UEBA ALERT: {ueba_result['details']}")
    else:
        st.success("System behavior normal")

# -----------------------------
# Auto Refresh
# -----------------------------
if auto_refresh:
    time.sleep(5)
    st.experimental_rerun()

st.caption("Academic Prototype – Predictive Vehicle Maintenance System")
