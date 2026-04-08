from sqlalchemy import Column, String, Text, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
import time

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True)
    user_id = Column(String, index=True)
    action = Column(String)  # query, login, connector_test, etc.
    resource_type = Column(String)  # connector, dataset, etc.
    resource_id = Column(String)
    query = Column(Text)
    status = Column(String)
    risk_score = Column(Integer)
    execution_time_ms = Column(Float)
    rows_returned = Column(Integer)
    metadata = Column(Text)  # JSON string if needed
    timestamp = Column(Float, default=time.time)
