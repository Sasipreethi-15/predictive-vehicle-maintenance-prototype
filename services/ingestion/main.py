from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = "sqlite:///database/vehicle_data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Table model
class VehicleTelemetry(Base):
    __tablename__ = "vehicle_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String)
    timestamp = Column(String)
    engine_temp = Column(Float)
    rpm = Column(Integer)
    speed = Column(Integer)
    coolant_level = Column(Float)
    battery_voltage = Column(Float)
    dtc_code = Column(String)

Base.metadata.create_all(bind=engine)

# API app
app = FastAPI(title="Vehicle Data Ingestion Service")

# Input schema
class TelemetryInput(BaseModel):
    vehicle_id: str
    timestamp: str
    engine_temp: float
    rpm: int
    speed: int
    coolant_level: float
    battery_voltage: float
    dtc_code: str

@app.post("/ingest")
def ingest_data(data: TelemetryInput):
    db = SessionLocal()
    record = VehicleTelemetry(**data.dict())
    db.add(record)
    db.commit()
    db.close()
    return {"message": "Telemetry data ingested successfully"}
