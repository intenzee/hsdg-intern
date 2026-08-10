"""
Pydantic schemas for request/response validation.
Ensures type safety and automatic API documentation.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List


# ============= Client Schemas =============

class ClientBase(BaseModel):
    """Base schema with common client fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Client name")
    entity_type: str = Field(..., description="Entity type: Individual, Company, LLP, Partnership, etc.")
    pan: Optional[str] = Field(None, max_length=10, description="PAN number")
    gstin: Optional[str] = Field(None, max_length=15, description="GSTIN number")
    contact_name: Optional[str] = Field(None, max_length=255, description="Contact person name")
    contact_email: Optional[str] = Field(None, max_length=255, description="Contact email")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    partner_in_charge: str = Field(..., min_length=1, max_length=255, description="Partner in charge")


class ClientCreate(ClientBase):
    """Schema for creating a new client."""
    pass


class ClientUpdate(ClientBase):
    """Schema for updating an existing client."""
    pass


class ClientResponse(ClientBase):
    """Schema for client response with database fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============= Task Schemas =============

class ComplianceTaskBase(BaseModel):
    """Base schema with common task fields."""
    client_id: int = Field(..., description="Client ID")
    task_type: str = Field(..., min_length=1, max_length=100, description="Task type: GSTR-3B, TDS, etc.")
    period_label: str = Field(..., min_length=1, max_length=50, description="Period: Jul 2026, Q2 FY26, etc.")
    due_date: date = Field(..., description="Due date for the task")
    assignee: str = Field(..., min_length=1, max_length=255, description="Assignee name")
    status: str = Field(default="Not Started", description="Status: Not Started, In Progress, Awaiting Client, Filed")


class ComplianceTaskCreate(ComplianceTaskBase):
    """Schema for creating a new task."""
    pass


class ComplianceTaskUpdate(BaseModel):
    """Schema for updating an existing task (all fields optional)."""
    task_type: Optional[str] = Field(None, min_length=1, max_length=100)
    period_label: Optional[str] = Field(None, min_length=1, max_length=50)
    due_date: Optional[date] = None
    assignee: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None


class ComplianceTaskResponse(ComplianceTaskBase):
    """Schema for task response with database fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ComplianceTaskWithClient(ComplianceTaskResponse):
    """Schema for task response with embedded client information."""
    client: ClientResponse
    
    model_config = ConfigDict(from_attributes=True)


class ComplianceTaskWithDocuments(ComplianceTaskResponse):
    """Schema for task response with embedded documents."""
    client: ClientResponse
    documents: List["TaskDocumentResponse"]
    
    model_config = ConfigDict(from_attributes=True)


# ============= Document Schemas =============

class TaskDocumentBase(BaseModel):
    """Base schema with common document fields."""
    document_name: str = Field(..., min_length=1, max_length=255, description="Document name")
    is_received: bool = Field(default=False, description="Whether document is received")


class TaskDocumentCreate(BaseModel):
    """Schema for creating a new document (task_id from URL path)."""
    document_name: str = Field(..., min_length=1, max_length=255, description="Document name")
    is_received: bool = Field(default=False, description="Whether document is received")


class TaskDocumentUpdate(BaseModel):
    """Schema for updating document status."""
    is_received: bool = Field(..., description="Whether document is received")


class TaskDocumentResponse(TaskDocumentBase):
    """Schema for document response with database fields."""
    id: int
    task_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============= Dashboard Schemas =============

class WorkloadSummary(BaseModel):
    """Schema for assignee workload summary."""
    assignee: str
    task_count: int
    
    model_config = ConfigDict(from_attributes=True)


# ============= Seed Data Schema =============

class SeedResponse(BaseModel):
    """Schema for seed endpoint response."""
    message: str
    clients_created: int
    tasks_created: int
    documents_created: int
