from sqlalchemy import Column, String, Integer
from voxcore.security.models import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True)
    name = Column(String)
    tier = Column(String)  # free, pro, enterprise
    max_queries = Column(Integer, default=1000)
