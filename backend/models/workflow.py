# Workflow orchestration DB migrations

from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Workflow(Base):
    __tablename__ = 'workflows'
    id = Column(String, primary_key=True)
    name = Column(String)
    trigger_type = Column(String)
    enabled = Column(Boolean)
    created_at = Column(TIMESTAMP)

class WorkflowStep(Base):
    __tablename__ = 'workflow_steps'
    id = Column(String, primary_key=True)
    workflow_id = Column(String)
    step_order = Column(Integer)
    step_type = Column(String)
    config = Column(Text)

class WorkflowExecution(Base):
    __tablename__ = 'workflow_executions'
    id = Column(String, primary_key=True)
    workflow_id = Column(String)
    current_step = Column(Integer)
    status = Column(String)
    context = Column(Text)
    started_at = Column(TIMESTAMP)
