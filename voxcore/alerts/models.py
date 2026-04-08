from sqlalchemy import Column, String, Text, Float
import time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True)
    tenant_id = Column(String)
    type = Column(String)  # anomaly, spike, decline
    severity = Column(String)  # low, medium, high
    message = Column(Text)
    metric = Column(String)
    entity = Column(String)
    confidence = Column(Float)
    timestamp = Column(Float, default=time.time)
