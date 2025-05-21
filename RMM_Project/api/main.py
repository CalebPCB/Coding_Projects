from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

app = FastAPI()

# PostgreSQL connection string (adjust as needed)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://caleb:postgresadmin@prod-rmm-db.cluster-c0rcwo8m2en7.us-east-1.rds.amazonaws.com/rmm"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SystemInfo(Base):
    __tablename__ = "system_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # new column for user name
    hostname = Column(String, index=True)
    os = Column(String)
    os_version = Column(String)
    cpu = Column(String)
    memory_gb = Column(Float)
    ip = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class SystemInfoIn(BaseModel):
    user_id: str = Field(..., description="User's name identifier")
    hostname: str
    os: str
    os_version: str
    cpu: str
    memory_gb: float
    ip: str

@app.post("/api/report")
def receive_system_info(data: SystemInfoIn):
    db = SessionLocal()
    try:
        info = SystemInfo(**data.dict())
        db.add(info)
        db.commit()
        db.refresh(info)
        return {"status": "success", "id": info.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
