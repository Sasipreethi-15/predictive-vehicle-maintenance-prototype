import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
DB_PATH = "database/vehicle_data.db"

PREDICT_API = "http://127.0.0.1:8001/predict"
EXPLAIN_API = "http://127.0.0.1:8002/explain"
RCA_API = "http://127.0.0.1:8003/analyze"
UEBA_API = "http://127.0.0.1:8004/log"

# -----------------------------
# HELPERS
# -----------------------------
def get_latest_vehicle_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT * FROM vehicle_telemetry ORDER BY id DESC LIMIT 1",
        conn
    )
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
    return requests.post(PREDICT_API, json=payload).json()

def explain_fault(row, risk):
    payload = {
        "engine_temp": row["engine_temp"],
        "rpm": int(row["rpm"]),
        "coolant_level": row["coolant_level"],
        "battery_voltage": row["battery_voltage"],
        "risk": risk
    }
    return requests.post(EXPLAIN_API, json=payload).json()

def send_rca(vehicle_id, fault_type):
    payload = {
        "vehicle_id": vehicle_id,
        "fault_type": fault_type
    }
    return requests.post(RCA_API, json=payload).json()

def log_ueba():
    return requests.post(UEBA_API, params={"component": "dashboard"}).json()

# -----------------------------
# SESSION STATE
# -----------------------------
if "notifications" not in st.session_state:
    st.session_state.notifications = []

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Predictive Maintenance Dashboard", layout="wide")
st.title("🚗 Vehicle Predictive Maintenance Dashboard")

st.button("🔄 Refresh Data")

df = get_latest_vehicle_data()

if df.empty:
    st.warning("No vehicle data available yet.")
    st.stop()

row = df.iloc[0]

# -----------------------------
# LAYOUT
# -----------------------------
col1, col2 = st.columns(2)

# Vehicle Data
with col1:
    st.subheader("📡 Latest Vehicle Data")
    st.write(f"Vehicle ID: {row['vehicle_id']}")
    st.write(f"Engine Temp: {row['engine_temp']} °C")
    st.write(f"RPM: {row['rpm']}")
    st.write(f"Speed: {row['speed']} km/h")
    st.write(f"Coolant Level: {row['coolant_level']}")
    st.write(f"Battery Voltage: {row['battery_voltage']} V")
    st.write(f"Timestamp: {row['timestamp']}")

# Prediction
with col2:
    st.subheader("🧠 ML Prediction")
    prediction = predict_fault(row)
    risk = prediction["risk"]

    if risk == "HIGH":
        st.error("⚠ HIGH RISK of fault detected")
    else:
        st.success("✅ LOW risk – vehicle healthy")

    st.write(prediction["message"])

# Explanation
st.subheader("💬 Explanation (Driver Message)")
explanation = explain_fault(row, risk)
explanation_text = explanation["explanation"]
st.info(explanation_text)

# -----------------------------
# MOCK DRIVER NOTIFICATION
# -----------------------------
st.subheader("📱 Driver Notification (Mock Push)")

if risk == "HIGH":
    if st.button("Send Notification to Driver"):
        st.session_state.notifications.insert(0, {
            "time": datetime.now().strftime("%H:%M:%S"),
            "vehicle": row["vehicle_id"],
            "message": explanation_text
        })
        st.success("Notification sent (mock)")
else:
    st.info("No notification needed for LOW risk")

if st.session_state.notifications:
    st.markdown("### Notification History")
    for n in st.session_state.notifications[:5]:
        st.write(f"{n['time']} | {n['vehicle']} | {n['message']}")

# -----------------------------
# RCA / CAPA
# -----------------------------
st.subheader("🛠 RCA / CAPA")

fault_type = "OVERHEATING" if row["engine_temp"] > 100 else "GENERAL_FAULT"
rca_result = send_rca(row["vehicle_id"], fault_type)

if "rca" in rca_result:
    st.warning(rca_result["rca"])
    st.success(rca_result["capa"])
else:
    st.write(rca_result["message"])

# -----------------------------
# UEBA
# -----------------------------
st.subheader("🔐 UEBA Status")
ueba = log_ueba()

if "alert" in ueba:
    st.error(ueba["details"])
else:
    st.success("System behavior normal")

st.caption("Academic Prototype – Predictive Maintenance System")
