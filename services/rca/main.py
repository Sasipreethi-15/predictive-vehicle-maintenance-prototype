from fastapi import FastAPI
from pydantic import BaseModel
from collections import defaultdict

app = FastAPI(title="RCA / CAPA Service")

# In-memory fault counter (prototype)
fault_counter = defaultdict(int)

class RCAInput(BaseModel):
    vehicle_id: str
    fault_type: str  # e.g., OVERHEATING, MISFIRE

@app.post("/analyze")
def analyze_fault(data: RCAInput):
    fault_counter[data.fault_type] += 1

    if fault_counter[data.fault_type] >= 3:
        return {
            "rca": f"Recurring {data.fault_type} detected across vehicles",
            "capa": f"Investigate {data.fault_type} root cause and apply design or maintenance improvements"
        }
    else:
        return {
            "message": "Fault recorded. Monitoring for recurrence."
        }
