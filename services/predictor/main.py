from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

# Load trained model
model = joblib.load("services/predictor/fault_prediction_model.pkl")

app = FastAPI(title="Vehicle Fault Prediction Service")

# Input schema
class PredictionInput(BaseModel):
    engine_temp: float
    rpm: int
    speed: int
    coolant_level: float
    battery_voltage: float

@app.post("/predict")
def predict_fault(data: PredictionInput):
    features = np.array([[
        data.engine_temp,
        data.rpm,
        data.speed,
        data.coolant_level,
        data.battery_voltage
    ]])

    prediction = model.predict(features)[0]

    if prediction == 1:
        return {
            "risk": "HIGH",
            "message": "Potential vehicle fault detected"
        }
    else:
        return {
            "risk": "LOW",
            "message": "Vehicle operating normally"
        }
