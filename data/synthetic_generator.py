import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

NUM_VEHICLES = 10
RECORDS_PER_VEHICLE = 100

def generate_vehicle_data():
    data = []

    for vehicle_id in range(1, NUM_VEHICLES + 1):
        base_temp = random.uniform(85, 95)
        base_rpm = random.randint(700, 900)

        timestamp = datetime.now()

        for _ in range(RECORDS_PER_VEHICLE):
            # Simulate gradual fault
            temp_drift = random.uniform(0, 0.2)
            rpm_noise = random.randint(-100, 100)

            engine_temp = base_temp + temp_drift
            rpm = base_rpm + rpm_noise
            speed = random.randint(0, 100)
            coolant_level = round(random.uniform(0.6, 1.0), 2)
            battery_voltage = round(random.uniform(11.8, 13.5), 2)

            dtc = random.choice(["NONE", "P0128", "P0300", "P0562"])

            data.append({
                "vehicle_id": f"V{vehicle_id}",
                "timestamp": timestamp,
                "engine_temp": round(engine_temp, 2),
                "rpm": rpm,
                "speed": speed,
                "coolant_level": coolant_level,
                "battery_voltage": battery_voltage,
                "dtc_code": dtc
            })

            timestamp += timedelta(seconds=10)

    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_vehicle_data()
    df.to_csv("output/vehicle_data.csv", index=False)
    print("Synthetic vehicle data generated successfully!")
