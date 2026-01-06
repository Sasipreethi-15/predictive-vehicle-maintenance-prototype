from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="UEBA Service")

request_log = []

@app.post("/log")
def log_activity(component: str):
    timestamp = datetime.now()
    request_log.append((component, timestamp))

    # Simple anomaly rule
    if len(request_log) > 10:
        return {
            "alert": "Anomalous behavior detected",
            "details": "Unusually high number of requests"
        }

    return {"message": "Activity logged"}
