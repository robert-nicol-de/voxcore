from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StoredCredential(Base):
    __tablename__ = "credentials"
    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True)
    user_id = Column(String)
    connector_type = Column(String)
    encrypted_config = Column(Text)
