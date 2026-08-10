from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    pan = Column(String(10), nullable=True, unique=True, index=True)
    gstin = Column(String(15), nullable=True, unique=True, index=True)
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    partner_in_charge = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    tasks = relationship("ComplianceTask", back_populates="client", cascade="all, delete-orphan")


class ComplianceTask(Base):
    __tablename__ = "compliance_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(String(100), nullable=False, index=True)
    period_label = Column(String(50), nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    assignee = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="Not Started", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    client = relationship("Client", back_populates="tasks")
    documents = relationship("TaskDocument", back_populates="task", cascade="all, delete-orphan")


class TaskDocument(Base):
    __tablename__ = "task_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("compliance_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    is_received = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    task = relationship("ComplianceTask", back_populates="documents")


RECURRENCE_RULES = {
    "GSTR-3B": {"frequency": "monthly", "due_day": 20},
    "GSTR-1": {"frequency": "monthly", "due_day": 11},
    "TDS": {"frequency": "monthly", "due_day": 7},
    "GST Quarterly": {"frequency": "quarterly", "due_day": 30},
    "Income Tax Audit": {"frequency": "annual", "due_month": 9, "due_day": 30},
    "ROC Annual Filing": {"frequency": "annual", "due_month": 11, "due_day": 30},
}
