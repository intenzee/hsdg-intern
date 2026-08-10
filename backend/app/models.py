"""
SQLAlchemy ORM models for CA Firm MIS.
Defines the database schema with proper relationships and constraints.
"""
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Client(Base):
    """
    Client master table.
    Stores information about clients served by the CA firm.
    """
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # Individual, Company, LLP, Partnership, etc.
    pan = Column(String(10), nullable=True, unique=True, index=True)
    gstin = Column(String(15), nullable=True, unique=True, index=True)
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    partner_in_charge = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tasks = relationship("ComplianceTask", back_populates="client", cascade="all, delete-orphan")


class ComplianceTask(Base):
    """
    Compliance tasks table.
    Stores compliance obligations for each client with due dates and status tracking.
    """
    __tablename__ = "compliance_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(String(100), nullable=False, index=True)  # GSTR-3B, GSTR-1, TDS, Income Tax Audit, etc.
    period_label = Column(String(50), nullable=False)  # "Jul 2026", "Q2 FY26", "FY 2025-26"
    due_date = Column(Date, nullable=False, index=True)
    assignee = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="Not Started", index=True)  # Not Started, In Progress, Awaiting Client, Filed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="tasks")
    documents = relationship("TaskDocument", back_populates="task", cascade="all, delete-orphan")


class TaskDocument(Base):
    """
    Task documents table.
    Tracks required documents for each compliance task with received/pending status.
    """
    __tablename__ = "task_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("compliance_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    is_received = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    task = relationship("ComplianceTask", back_populates="documents")


# Recurrence rules are encoded as constants for now
# This can be moved to a database table later for more flexibility
RECURRENCE_RULES = {
    "GSTR-3B": {
        "frequency": "monthly",
        "due_day": 20,  # 20th of next month
        "description": "GST Return 3B - Monthly"
    },
    "GSTR-1": {
        "frequency": "monthly",
        "due_day": 11,  # 11th of next month
        "description": "GST Return 1 - Monthly"
    },
    "TDS": {
        "frequency": "monthly",
        "due_day": 7,  # 7th of next month
        "description": "TDS Return - Monthly"
    },
    "GST Quarterly": {
        "frequency": "quarterly",
        "due_day": 30,  # 30 days after quarter end
        "description": "GST Return - Quarterly"
    },
    "Income Tax Audit": {
        "frequency": "annual",
        "due_month": 9,  # September
        "due_day": 30,
        "description": "Income Tax Audit Report"
    },
    "ROC Annual Filing": {
        "frequency": "annual",
        "due_month": 11,  # November
        "due_day": 30,
        "description": "ROC Annual Filing"
    },
}
