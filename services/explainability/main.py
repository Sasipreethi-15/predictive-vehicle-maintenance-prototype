from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Explainability Service")

class ExplainInput(BaseModel):
    engine_temp: float
    rpm: int
    coolant_level: float
    battery_voltage: float
    risk: str  # HIGH or LOW

@app.post("/explain")
def explain_prediction(data: ExplainInput):
    reasons = []

    if data.engine_temp > 100:
        reasons.append("engine temperature is unusually high")

    if data.rpm > 3000:
        reasons.append("engine RPM is unstable")

    if data.coolant_level < 0.7:
        reasons.append("coolant level is low")

    if data.battery_voltage < 12.0:
        reasons.append("battery voltage is dropping")

    if data.risk == "HIGH":
        explanation = " and ".join(reasons) if reasons else "abnormal sensor patterns detected"
        message = f"Potential issue detected because {explanation}. We recommend scheduling a service check."
    else:
        message = "All sensor readings are within normal range. No immediate action required."

    return {
        "risk": data.risk,
        "explanation": message
    }

 
