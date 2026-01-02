import pandas as pd
import requests
import time

API_URL = "http://127.0.0.1:8000/ingest"
CSV_PATH = "output/vehicle_data.csv"

def send_data():
    df = pd.read_csv(CSV_PATH)

    for _, row in df.iterrows():
        payload = {
            "vehicle_id": row["vehicle_id"],
            "timestamp": row["timestamp"],
            "engine_temp": float(row["engine_temp"]),
            "rpm": int(row["rpm"]),
            "speed": int(row["speed"]),
            "coolant_level": float(row["coolant_level"]),
            "battery_voltage": float(row["battery_voltage"]),
            "dtc_code": row["dtc_code"]
        }

        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            print(f"Sent data for {row['vehicle_id']} at {row['timestamp']}")
        else:
            print("Failed to send data")

        time.sleep(1)  # simulate real-time streaming (1 sec delay)

if __name__ == "__main__":
    send_data()
